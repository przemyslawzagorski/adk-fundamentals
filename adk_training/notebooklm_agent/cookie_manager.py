"""cookie_manager.py — Ekstrakcja i wstrzykiwanie ciasteczek Google/NotebookLM.

Obsługuje trzy źródła ciasteczek:
  A) Playwright storage_state (JSON) — eksport z istniejącego profilu agenta
  B) Chrome SQLite (Cookies) — prawdziwy profil Chrome, deszyfrowanie Windows DPAPI
  C) Dowolny plik JSON w formacie Playwright lub Netscape/JSON array

Wstrzykiwanie do nowej, izolowanej instancji Playwright BrowserContext
eliminuje problemy z blokadą pliku profilu i zajętymi portami CDP.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import sqlite3
import tempfile
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("notebooklm_agent.cookie_manager")

# Domeny Google wymagane do autoryzacji NotebookLM
GOOGLE_AUTH_DOMAINS = [
    ".google.com",
    ".accounts.google.com",
    "notebooklm.google.com",
    ".googleapis.com",
]


# ── Typ ciasteczka Playwright ───────────────────────────────────────────────

def _normalize_cookie(raw: dict) -> dict:
    """Normalizuj ciasteczko do formatu wymaganego przez Playwright add_cookies()."""
    cookie: dict[str, Any] = {
        "name": raw.get("name", ""),
        "value": raw.get("value", ""),
        "domain": raw.get("domain", ""),
        "path": raw.get("path", "/"),
        "secure": bool(raw.get("secure", False)),
        "httpOnly": bool(raw.get("httpOnly", raw.get("http_only", False))),
        "sameSite": raw.get("sameSite", raw.get("same_site", "Lax")),
    }
    # expires: Playwright przyjmuje float (unix timestamp), -1 = session cookie
    expires = raw.get("expires", raw.get("expirationDate", -1))
    if expires is None:
        expires = -1
    cookie["expires"] = float(expires)
    return cookie


# ── A: Playwright storage_state JSON ───────────────────────────────────────

def load_cookies_from_storage_state(path: str | Path) -> list[dict]:
    """Wczytaj ciasteczka z pliku storage_state.json Playwright."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"storage_state nie istnieje: {path}")
    with open(path, encoding="utf-8") as f:
        state = json.load(f)
    raw_cookies = state.get("cookies", [])
    cookies = [_normalize_cookie(c) for c in raw_cookies]
    logger.info("Wczytano %d ciasteczek z storage_state: %s", len(cookies), path)
    return cookies


# ── B: Chrome SQLite (Windows DPAPI) ───────────────────────────────────────

_CHROME_APP_BOUND_PREFIX_LEN = 32
"""Chrome 127+ prepend 32-byte App-Bound Encryption context to each cookie plaintext.

After AES-GCM decryption the raw plaintext has structure:
  [32B app-bound context] + [actual cookie value as ASCII]

The 32-byte prefix is the same for all cookies from a given eTLD+1 domain
and changes between browser sessions. It must be stripped to get the real value.
"""


def _decrypt_chrome_cookie_win(encrypted: bytes, master_key: bytes) -> str:
    """Deszyfruj ciasteczko Chrome (v10 = AES-256-GCM, starsze = DPAPI)."""
    if not encrypted:
        return ""
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError:
        raise ImportError("Zainstaluj: pip install cryptography")

    if encrypted[:3] == b"v10":
        # v10: 3B prefix + 12B nonce + ciphertext (ostatnie 16B to tag GCM)
        nonce = encrypted[3:15]
        ciphertext = encrypted[15:]
        aesgcm = AESGCM(master_key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)

        # Chrome 127+ App-Bound Encryption: strip 32-byte context prefix.
        # Verify by checking whether bytes after offset 32 are all printable ASCII.
        if len(plaintext) > _CHROME_APP_BOUND_PREFIX_LEN:
            candidate = plaintext[_CHROME_APP_BOUND_PREFIX_LEN:]
            if all(0x20 <= b <= 0x7E for b in candidate):
                return candidate.decode("ascii")

        return plaintext.decode("utf-8", errors="replace")
    else:
        # Starszy format — DPAPI
        try:
            import win32crypt  # type: ignore
            data = win32crypt.CryptUnprotectData(encrypted, None, None, None, 0)
            return data[1].decode("utf-8", errors="replace")
        except Exception:
            return ""


def _get_chrome_master_key(user_data_dir: str | Path) -> Optional[bytes]:
    """Pobierz klucz szyfrowania AES z Local State Chrome (Windows DPAPI)."""
    local_state_path = Path(user_data_dir) / "Local State"
    if not local_state_path.exists():
        return None
    try:
        import base64
        import win32crypt  # type: ignore
        with open(local_state_path, encoding="utf-8") as f:
            local_state = json.load(f)
        encrypted_key_b64 = local_state["os_crypt"]["encrypted_key"]
        encrypted_key = base64.b64decode(encrypted_key_b64)[5:]  # pomiń prefix DPAPI
        master_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
        return master_key
    except Exception as e:
        logger.warning("Nie można pobrać master key Chrome: %s", e)
        return None


def load_cookies_from_chrome_sqlite(
    profile_dir: str | Path,
    domains: Optional[list[str]] = None,
) -> list[dict]:
    """Wczytaj i odszyfruj ciasteczka z Chrome SQLite (Windows).

    Args:
        profile_dir: Katalog profilu Chrome (zawiera plik 'Cookies' lub 'Network/Cookies')
        domains:     Lista domen do filtrowania (None = wszystkie)
    """
    profile_dir = Path(profile_dir)
    # Chrome >= 96 przeniosło Cookies do podkatalogu Network/
    candidates = [
        profile_dir / "Network" / "Cookies",
        profile_dir / "Cookies",
    ]
    db_path = next((p for p in candidates if p.exists()), None)
    if db_path is None:
        raise FileNotFoundError(f"Nie znaleziono pliku Cookies w: {profile_dir}")

    # Klucz do deszyfrowania AES (Windows)
    # user_data_dir to katalog NADRZĘDNY profilu
    user_data_dir = profile_dir.parent
    master_key = _get_chrome_master_key(user_data_dir)

    # SQLite może być zablokowane przez Chrome — kopiujemy do temp
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as tmp:
        tmp_path = tmp.name
    shutil.copy2(db_path, tmp_path)

    cookies: list[dict] = []
    try:
        con = sqlite3.connect(tmp_path)
        con.row_factory = sqlite3.Row
        # Chrome >= 96: is_secure; starsze: secure — próbujemy obu nazw
        col_info = {r[1] for r in con.execute("PRAGMA table_info(cookies)").fetchall()}
        secure_col = "is_secure" if "is_secure" in col_info else "secure"
        cur = con.execute(
            f"SELECT host_key, name, value, encrypted_value, path, "
            f"{secure_col} AS is_secure, is_httponly, samesite, expires_utc FROM cookies"
        )
        for row in cur:
            host = row["host_key"]
            if domains and not any(host.endswith(d.lstrip(".")) or host == d for d in domains):
                continue
            value = row["value"]
            if not value and row["encrypted_value"] and master_key:
                value = _decrypt_chrome_cookie_win(bytes(row["encrypted_value"]), master_key)
            # Chrome expires_utc: mikrosekund od 1601-01-01 → unix timestamp
            expires_utc = row["expires_utc"]
            if expires_utc:
                expires = (expires_utc / 1_000_000) - 11644473600
            else:
                expires = -1
            same_site_map = {-1: "None", 0: "None", 1: "Lax", 2: "Strict"}
            cookies.append(_normalize_cookie({
                "name": row["name"],
                "value": value,
                "domain": host,
                "path": row["path"],
                "secure": bool(row["is_secure"]),
                "httpOnly": bool(row["is_httponly"]),
                "sameSite": same_site_map.get(row["samesite"], "Lax"),
                "expires": expires,
            }))
        con.close()
    finally:
        # Zamknij połączenie przed usunięciem — Windows blokuje otwarty plik
        try:
            os.unlink(tmp_path)
        except PermissionError:
            pass  # plik zostanie usunięty przez system przy ponownym uruchomieniu

    logger.info("Wczytano %d ciasteczek z Chrome SQLite: %s", len(cookies), db_path)
    return cookies


# ── C: Generyczny JSON (array lub storage_state) ───────────────────────────

def load_cookies_from_json(path: str | Path) -> list[dict]:
    """Wczytaj ciasteczka z pliku JSON (array lub storage_state Playwright)."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Plik JSON nie istnieje: {path}")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        raw_list = data
    elif isinstance(data, dict) and "cookies" in data:
        raw_list = data["cookies"]
    else:
        raise ValueError("Nieznany format JSON — oczekiwano tablicy lub {cookies: [...]}")
    cookies = [_normalize_cookie(c) for c in raw_list]
    logger.info("Wczytano %d ciasteczek z JSON: %s", len(cookies), path)
    return cookies


# ── Wstrzykiwanie do Playwright BrowserContext ──────────────────────────────

def inject_cookies(context, cookies: list[dict]) -> int:
    """Wstrzyknij ciasteczka do Playwright BrowserContext (sync API).

    Args:
        context:  playwright.sync_api.BrowserContext
        cookies:  Lista znormalizowanych ciasteczek

    Returns:
        Liczba wstrzykniętych ciasteczek
    """
    if not cookies:
        logger.warning("Brak ciasteczek do wstrzyknięcia.")
        return 0

    # Filtruj puste wartości — Playwright odrzuci nieprawidłowe wpisy
    valid = [c for c in cookies if c.get("name") and c.get("domain")]
    skipped = len(cookies) - len(valid)
    if skipped:
        logger.debug("Pominięto %d pustych/nieprawidłowych ciasteczek.", skipped)

    context.add_cookies(valid)
    logger.info("Wstrzyknięto %d ciasteczek do BrowserContext.", len(valid))
    return len(valid)


def save_cookies_to_json(cookies: list[dict], path: str | Path) -> None:
    """Zapisz ciasteczka do pliku JSON (format Playwright array)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cookies, f, ensure_ascii=False, indent=2)
    logger.info("Zapisano %d ciasteczek do: %s", len(cookies), path)


def export_storage_state_from_context(context, path: str | Path) -> None:
    """Eksportuj pełny storage_state (cookies + localStorage) z kontekstu Playwright."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    context.storage_state(path=str(path))
    logger.info("Zapisano storage_state do: %s", path)

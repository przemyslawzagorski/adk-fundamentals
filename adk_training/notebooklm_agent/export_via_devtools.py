"""export_via_devtools.py — Eksport cookies przez DevTools (F12) → Copy as cURL.

Architektura:
  1. Chrome startuje z prawdziwym profilem (BeyondCorp OK)
  2. Otwiera NotebookLM automatycznie
  3. Użytkownik robi 4 kliknięcia w DevTools: Network → Ctrl+R → Copy as cURL
  4. Python czyta schowek i parsuje cookies (w tym HTTPOnly)
  5. Zapisuje cookies.json

Wymaganie: Zamknij Chrome przed uruchomieniem.
"""
from __future__ import annotations
import os, sys, re, json, subprocess, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from notebooklm_agent.config import CONFIG

CHROME_USER_DATA = Path(os.environ["LOCALAPPDATA"]) / "Google" / "Chrome" / "User Data"
CHROME_EXE = Path(os.environ.get("PROGRAMFILES", r"C:\Program Files")) / "Google" / "Chrome" / "Application" / "chrome.exe"
OUT = Path(CONFIG.data_dir) / "cookies.json"
TARGET_URL = CONFIG.default_notebook_url or "https://notebooklm.google.com"


def read_clipboard() -> str:
    """Czyta schowek przez PowerShell."""
    r = subprocess.run(
        ["powershell", "-NoProfile", "-Command", "Get-Clipboard"],
        capture_output=True, text=True, timeout=10,
    )
    return r.stdout.strip()


def parse_curl_cookies(curl_text: str) -> list[dict]:
    """Parsuje 'Copy as cURL (bash lub cmd)' i zwraca listę cookies."""
    preview = curl_text[:200].replace("\n", "↵").replace("\r", "")
    print(f"  [DEBUG] cURL preview: {preview}")

    # 1. Normalizuj format CMD (Windows): ^" → "  i  ^<newline> → spacja
    clean = curl_text
    clean = re.sub(r'\^"', '"', clean)          # CMD escaped quote
    clean = re.sub(r'\^\s*\n\s*', ' ', clean)  # CMD line continuation
    clean = re.sub(r'\\\s*\n\s*', ' ', clean)  # bash line continuation
    clean = clean.replace("^", "")              # pozostałe ^ (np. ^^ → ^)

    # 2. Szukaj nagłówka cookie w różnych formatach
    patterns = [
        r'''-H\s+'[Cc]ookie:\s*([^']+)' ''',   # bash: -H 'cookie: ...'
        r'''-H\s+"[Cc]ookie:\s*([^"]+)"''',    # cmd/bash: -H "cookie: ..."
        r'''(?:--cookie|-b)\s+'([^']+)' ''',   # -b 'cookie...'
        r'''(?:--cookie|-b)\s+"([^"]+)"''',    # -b "cookie..."
    ]
    cookie_str = None
    for pat in patterns:
        m = re.search(pat.strip(), clean, re.IGNORECASE)
        if m:
            cookie_str = m.group(1)
            print(f"  [DEBUG] Cookie header znaleziony ({len(cookie_str)} znaków)")
            break

    if not cookie_str:
        print("  [DEBUG] Brak nagłówka Cookie — prawdopodobnie ten request nie miał cookies.")
        print("  [DEBUG] Użyj filtra 'Doc' w DevTools żeby łatwiej znaleźć główny dokument.")
        return []

    # 3. Domena z URL
    url_match = re.search(r"https://([^/\"\s]+)", clean)
    host = url_match.group(1) if url_match else "notebooklm.google.com"
    parts = host.split(".")
    domain = "." + ".".join(parts[-2:]) if len(parts) >= 2 else "." + host

    cookies = []
    for part in cookie_str.split(";"):
        part = part.strip()
        if "=" not in part:
            continue
        name, _, value = part.partition("=")
        cookies.append({
            "name": name.strip(),
            "value": value.strip(),
            "domain": domain,
            "path": "/",
            "expires": -1,
            "httpOnly": False,
            "secure": True,
            "sameSite": "None",
        })
    return cookies


def export_via_devtools(out: Path = OUT) -> bool:
    print("=" * 60)
    print("  Eksport cookies przez DevTools (Copy as cURL)")
    print("=" * 60)

    # Zamknij Chrome, usuń lock
    subprocess.run(["taskkill", "/F", "/IM", "chrome.exe", "/T"], capture_output=True)
    time.sleep(2)
    for lock in [CHROME_USER_DATA / "SingletonLock", CHROME_USER_DATA / "SingletonSocket"]:
        lock.unlink(missing_ok=True)

    # Uruchom Chrome z prawdziwym profilem
    args = [
        str(CHROME_EXE),
        "--profile-directory=Default",
        f"--user-data-dir={CHROME_USER_DATA}",
        "--disable-features=DevToolsDebuggingRestrictions",
        "--disable-blink-features=AutomationControlled",
        "--no-first-run",
        "--no-default-browser-check",
        "--hide-crash-restore-bubble",
        TARGET_URL,
    ]
    subprocess.Popen(args)
    print(f"\n  🚀 Chrome uruchomiony → {TARGET_URL}")
    print(f"\n  Poczekaj aż NotebookLM się załaduje, potem wykonaj:")
    print()
    print("  ┌─ INSTRUKCJA (4 kroki) ────────────────────────────────────────┐")
    print("  │  1. F12  →  DevTools  →  zakładka 'Network'                  │")
    print("  │  2. Ctrl+R  →  przeładuj stronę                              │")
    print("  │  3. Przewiń listę na GÓRĘ, znajdź request Type = 'document'  │")
    print("  │     (to najdłuższa nazwa, zaczyna się od ID notebooka)        │")
    print("  │  4. Kliknij PRAWYM → Copy → Copy as cURL (bash)              │")
    print("  └───────────────────────────────────────────────────────────────┘")
    print()

    input("  Naciśnij ENTER gdy cURL jest już w schowku... ")

    curl_text = read_clipboard()
    if not curl_text.startswith("curl "):
        print(f"  ❌ Schowek nie zawiera cURL (zaczyna się od: '{curl_text[:40]}')")
        print("     Upewnij się że kliknąłeś 'Copy as cURL (bash)' w Network tab.")
        return False

    print(f"  ✅ Odczytano cURL ({len(curl_text)} znaków)")
    cookies = parse_curl_cookies(curl_text)
    if not cookies:
        print("  ❌ Nie znaleziono cookies w cURL.")
        print("     Sprawdź czy request miał nagłówek Cookie.")
        return False

    # Zapisz jako storage_state
    state = {"cookies": cookies, "origins": []}
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

    google = [c for c in cookies if "google" in c["domain"]]
    print(f"  📊 Cookies: {len(cookies)} (w tym {len(google)} Google)")
    print(f"\n  ✅ SUKCES → {out}")
    print(f"  Następny krok: python notebooklm_agent/_test_cookie_auth.py")
    return True


if __name__ == "__main__":
    ok = export_via_devtools()
    sys.exit(0 if ok else 1)

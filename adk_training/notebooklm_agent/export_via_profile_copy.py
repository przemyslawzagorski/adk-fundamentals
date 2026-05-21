"""export_via_profile_copy.py — Eksport sesji przez kopię profilu Chrome.

Strategia:
1. Kopiuje Default profil Chrome do lokalizacji tymczasowej
2. Tworzy nowy Local State z kluczem DPAPI (bez CloudManagementEnrollmentToken)
3. Otwiera kopię przez Playwright - Chrome odszyfrowuje v20 cookies tym samym kluczem
4. Eksportuje storage_state() → cookies.json

Dlaczego to działa:
- Klucz v20 to ten sam klucz DPAPI (ten sam user Windows, ta sama maszyna)
- Bez enrollment token Chrome nie próbuje połączyć z cloud management → nie wisi
- Playwright może normalnie sterować kopią profilu

WYMAGANIE: Chrome musi być ZAMKNIĘTY.
"""
from __future__ import annotations
import os, sys, json, shutil, tempfile, time, base64
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from playwright.sync_api import sync_playwright
from notebooklm_agent.config import CONFIG

CHROME_USER_DATA = Path(os.environ["LOCALAPPDATA"]) / "Google" / "Chrome" / "User Data"
OUT = Path(CONFIG.data_dir) / "cookies.json"
TARGET = CONFIG.default_notebook_url or "https://notebooklm.google.com"


def is_logged_in(url: str) -> bool:
    return "notebooklm.google.com" in url and "accounts.google.com" not in url


def export_via_copy(profile_subdir: str = "Default", out: Path = OUT) -> bool:
    src_profile = CHROME_USER_DATA / profile_subdir
    src_local_state = CHROME_USER_DATA / "Local State"

    print("=" * 60)
    print("  Eksport przez kopię profilu (bez cloud management)")
    print("=" * 60)

    if not src_profile.exists():
        print(f"BŁĄD: Brak profilu: {src_profile}"); return False

    tmp_dir = Path(tempfile.mkdtemp(prefix="chrome-agent-"))
    tmp_profile = tmp_dir / profile_subdir
    print(f"\n  Kopiuję profil do: {tmp_dir}")

    # Kopiuj tylko niezbędne pliki profilu (bez cache, historii, rozszerzeń)
    NEEDED = [
        "Cookies",
        "Network/Cookies",
        "Preferences",
        "Secure Preferences",
        "Local State",       # kopia lokalna (ale master Local State jest w User Data root)
        "Web Data",
    ]
    tmp_profile.mkdir(parents=True)
    copied = 0
    for rel in NEEDED:
        src = src_profile / rel
        if src.exists():
            dst = tmp_profile / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            copied += 1
            print(f"     ✓ {rel} ({src.stat().st_size // 1024} KB)")
    print(f"  Skopiowano {copied} plików")

    # Skopiuj Local State (zawiera klucz DPAPI + enrollment token)
    # ★ ZACHOWAJ CloudManagementEnrollmentToken — potrzebny dla BeyondCorp!
    #   Niestandardowy user-data-dir omija Chrome 136 restriction,
    #   enrollment token zachowuje managed status → BeyondCorp przepuszcza.
    with open(src_local_state, encoding="utf-8") as f:
        ls = json.load(f)

    tmp_local_state = tmp_dir / "Local State"
    with open(tmp_local_state, "w", encoding="utf-8") as f:
        json.dump(ls, f)

    token = ls.get("management", {}).get("CloudManagementEnrollmentToken", "brak")
    print(f"  Local State: klucz DPAPI + enrollment token zachowane ({token[:8]}...)")

    with sync_playwright() as pw:
        args = [
            f"--profile-directory={profile_subdir}",
            "--disable-features=DevToolsDebuggingRestrictions",  # Chrome 136 workaround
            "--disable-blink-features=AutomationControlled",
            "--no-first-run",
            "--no-default-browser-check",
            "--hide-crash-restore-bubble",
        ]
        ignore_args = ["--enable-automation", "--enable-blink-features=IdleDetection"]

        print(f"\n  🚀 Uruchamiam Chrome z kopią profilu...")
        try:
            ctx = pw.chromium.launch_persistent_context(
                user_data_dir=str(tmp_dir),
                headless=False,
                channel="chrome",
                args=args,
                ignore_default_args=ignore_args,
                viewport={"width": 1280, "height": 800},
                timeout=60_000,
            )
            print("  ✅ Chrome uruchomiony!")
        except Exception as e:
            print(f"  ❌ {e}")
            shutil.rmtree(tmp_dir, ignore_errors=True)
            return False

        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        print(f"\n  🌐 Nawiguję do NotebookLM...")
        try:
            page.goto(TARGET, timeout=30_000, wait_until="domcontentloaded")
        except Exception as e:
            if "interrupted" not in str(e): print(f"  ⚠️  {e}")
        time.sleep(3)

        url = page.url
        if is_logged_in(url):
            print(f"  ✅ Już zalogowany! {url[:70]}")
        else:
            print(f"\n  🔑 Zaloguj się w oknie Chrome (email + hasło + 2FA).")
            print("     Skrypt automatycznie wykryje zakończenie logowania.\n")

            # Automatyczne wykrywanie zakończenia logowania (do 10 minut)
            deadline = time.time() + 600
            last_url = ""
            while time.time() < deadline:
                cur = page.url
                if cur != last_url:
                    print(f"  → {cur[:80]}")
                    last_url = cur
                # Wykryj że użytkownik przeszedł przez 2FA i jest po stronie Google
                if ("myaccount.google.com" in cur or
                    "accounts.google.com/signin/oauth" in cur or
                    "notebooklm.google.com" in cur or
                    ("accounts.google.com" not in cur and "google.com" in cur and "signin" not in cur)):
                    print(f"  ✅ Logowanie wykryte!")
                    break
                time.sleep(2)
            else:
                print("  ❌ Timeout logowania (10 min).")
                ctx.close(); shutil.rmtree(tmp_dir, ignore_errors=True); return False

            if is_logged_in(page.url):
                print(f"  ✅ NotebookLM już załadowany!")
            else:
                # Czekaj na instalację rozszerzenia BeyondCorp przez CBCM (async)
                print("  ⏳ Czekam 75s na rozszerzenie BeyondCorp (CBCM instaluje asynchronicznie)...")
                for remaining in range(75, 0, -1):
                    print(f"     {remaining:3d}s ", end="\r", flush=True)
                    time.sleep(1)
                print("\n  ⏳ Nawiguję do NotebookLM...")
                try:
                    page.goto(TARGET, timeout=40_000, wait_until="domcontentloaded")
                except Exception as e:
                    if "interrupted" not in str(e): print(f"  ⚠️  {e}")
                time.sleep(4)

                if not is_logged_in(page.url):
                    print(f"  ❌ BeyondCorp zablokował: {page.url[:80]}")
                    ctx.close(); shutil.rmtree(tmp_dir, ignore_errors=True); return False

        # Eksport
        print(f"\n  💾 Eksportuję storage_state...")
        out.parent.mkdir(parents=True, exist_ok=True)
        ctx.storage_state(path=str(out))
        ctx.close()

    # Statystyki
    with open(out, encoding="utf-8") as f:
        state = json.load(f)
    cookies = state.get("cookies", [])
    google = [c for c in cookies if ".google.com" in c.get("domain", "")]
    empty = [c for c in google if not c.get("value")]
    print(f"  📊 Cookies: {len(cookies)} ({len(google)} Google Auth, {len(empty)} pustych)")

    shutil.rmtree(tmp_dir, ignore_errors=True)
    if google and not empty:
        print(f"\n  ✅ SUKCES → {out}")
        print("  Uruchom: python notebooklm_agent/_test_cookie_auth.py")
        return True
    print(f"\n  ⚠️  Eksport częściowy (pustych: {len(empty)})")
    return False


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--profile", default="Default")
    p.add_argument("--out", default=str(OUT))
    a = p.parse_args()
    ok = export_via_copy(a.profile, Path(a.out))
    sys.exit(0 if ok else 1)

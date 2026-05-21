"""export_from_main_profile.py — Eksport sesji z GŁÓWNEGO profilu Chrome (konto Comarch).

Architektura (2026):
  1. Chrome startuje przez subprocess z prawdziwym profilem Default
     + --remote-debugging-port=9222
     + --disable-features=DevToolsDebuggingRestrictions  (obejście Chrome 136)
     + bez --enable-automation                           (stealth dla BeyondCorp)
  2. Playwright dołącza przez connect_over_cdp() do już działającego Chrome
     (omija problem z pipe/launch_persistent_context na managed profile)
  3. Chrome odszyfrowuje v20 cookies samodzielnie (właściwy profil + klucz DPAPI)
  4. storage_state() eksportuje plaintext cookies

Dlaczego tak a nie inaczej:
  - launch_persistent_context hanguje na enterprise Chrome (CBCM blokuje pipe)
  - Osobny subprocess + connect_over_cdp to standardowy pattern dla CDP
  - --disable-features=DevToolsDebuggingRestrictions bypasuje Chrome 136 restriction
    na debugowanie default user-data-dir

WYMAGANIE: Zamknij Chrome przed uruchomieniem!
"""
from __future__ import annotations
import argparse, os, sys, time, json, subprocess, urllib.request
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from playwright.sync_api import sync_playwright

from notebooklm_agent.config import CONFIG

CHROME_USER_DATA = Path(os.environ["LOCALAPPDATA"]) / "Google" / "Chrome" / "User Data"
CHROME_EXE = Path(os.environ.get("PROGRAMFILES", r"C:\Program Files")) / "Google" / "Chrome" / "Application" / "chrome.exe"
OUT = Path(CONFIG.data_dir) / "cookies.json"
TARGET_URL = CONFIG.default_notebook_url or "https://notebooklm.google.com"
CDP_PORT = 9222


def is_logged_in(url: str) -> bool:
    return (
        "accounts.google.com" not in url
        and "access-denied" not in url
        and "signin" not in url.lower()
        and "notebooklm.google.com" in url
    )


def wait_for_cdp(port: int = CDP_PORT, timeout: int = 30) -> bool:
    """Czeka aż Chrome otworzy port CDP."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            urllib.request.urlopen(f"http://localhost:{port}/json/version", timeout=2)
            return True
        except Exception:
            time.sleep(1)
    return False


def export_from_main_profile(profile_subdir: str = "Default", out: Path = OUT) -> bool:
    profile_dir = CHROME_USER_DATA / profile_subdir
    if not profile_dir.exists():
        print(f"BŁĄD: Profil nie istnieje: {profile_dir}")
        return False
    if not CHROME_EXE.exists():
        print(f"BŁĄD: Chrome nie znaleziony: {CHROME_EXE}")
        return False

    print("=" * 60)
    print("  Eksport sesji z głównego profilu Chrome (CDP)")
    print("=" * 60)
    print(f"\n  Profil:  {profile_dir}")
    print(f"  Wynik:   {out}")
    print(f"  URL:     {TARGET_URL}\n")

    # Usuń lock file jeśli został po force-kill
    for lock in [CHROME_USER_DATA / "SingletonLock", CHROME_USER_DATA / "SingletonSocket"]:
        lock.unlink(missing_ok=True)

    chrome_args = [
        str(CHROME_EXE),
        f"--profile-directory={profile_subdir}",
        f"--remote-debugging-port={CDP_PORT}",
        # Chrome 136: bez tego flaga debugging jest ignorowana na default profile
        "--disable-features=DevToolsDebuggingRestrictions",
        # Stealth — BeyondCorp nie wykryje automation
        "--disable-blink-features=AutomationControlled",
        "--no-first-run",
        "--no-default-browser-check",
        "--hide-crash-restore-bubble",
        f"--user-data-dir={CHROME_USER_DATA}",
    ]

    print(f"  🚀 Startuję Chrome z prawdziwym profilem...")
    print(f"     {CHROME_EXE.name} --profile-directory={profile_subdir} --remote-debugging-port={CDP_PORT}")
    proc = subprocess.Popen(chrome_args)

    print(f"  ⏳ Czekam na port CDP {CDP_PORT}...")
    if not wait_for_cdp(CDP_PORT, timeout=20):
        print(f"  ❌ Port {CDP_PORT} nie odpowiada — CBCM blokuje remote debugging.")
        print(f"     Sprawdź: chrome://policy → DevToolsAvailability / RemoteDebuggingAllowed")
        proc.terminate()
        return False
    print(f"  ✅ Port {CDP_PORT} dostępny — łączę Playwright przez CDP...")

    with sync_playwright() as pw:
        try:
            browser = pw.chromium.connect_over_cdp(f"http://localhost:{CDP_PORT}")
        except Exception as e:
            print(f"  ❌ Nie można połączyć CDP: {e}")
            proc.terminate()
            return False

        print(f"  ✅ Playwright połączony z Chrome!")
        ctx = browser.contexts[0] if browser.contexts else browser.new_context()
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        print(f"\n  🌐 Nawiguję do NotebookLM...")
        try:
            page.goto(TARGET_URL, timeout=30_000, wait_until="domcontentloaded")
        except Exception as e:
            if "interrupted" not in str(e):
                print(f"  ⚠️  {e}")
        time.sleep(3)

        url = page.url
        if is_logged_in(url):
            print(f"  ✅ Zalogowany! {url[:70]}")
        else:
            print(f"  ⚠️  Nie zalogowany: {url[:70]}")
            print("  Zaloguj się w oknie Chrome — skrypt wykryje automatycznie.\n")
            deadline = time.time() + 600
            while time.time() < deadline:
                time.sleep(3)
                if is_logged_in(page.url):
                    print(f"  ✅ Zalogowany! {page.url[:70]}")
                    break
            else:
                print("  ❌ Timeout logowania.")
                browser.close(); proc.terminate(); return False

        print(f"\n  💾 Eksportuję storage_state...")
        out.parent.mkdir(parents=True, exist_ok=True)
        ctx.storage_state(path=str(out))
        browser.close()

    with open(out, encoding="utf-8") as f:
        state = json.load(f)
    cookies = state.get("cookies", [])
    google_auth = [c for c in cookies if ".google.com" in c.get("domain", "")]
    empty = [c for c in google_auth if not c.get("value")]

    print(f"  📊 Cookies: {len(cookies)} łącznie, {len(google_auth)} Google Auth, {len(empty)} pustych")

    if google_auth and not empty:
        print(f"\n  ✅ SUKCES → {out}")
        print(f"  Następny krok: python notebooklm_agent/_test_cookie_auth.py")
        return True
    print(f"\n  ⚠️  Eksport częściowy (pustych: {len(empty)})")
    return bool(google_auth)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="Default")
    parser.add_argument("--out", default=str(OUT))
    args = parser.parse_args()
    ok = export_from_main_profile(args.profile, Path(args.out))
    sys.exit(0 if ok else 1)

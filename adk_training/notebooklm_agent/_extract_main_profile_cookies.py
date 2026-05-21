"""Wyciągnij ciasteczka z głównego profilu Chrome (Default = konto Comarch).

WYMAGANIE: Chrome musi być ZAMKNIĘTY (plik Cookies jest zablokowany gdy Chrome działa).
Skrypt skopiuje Cookies do temp, odszyfruje DPAPI, zapisze do cookies.json.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from notebooklm_agent.cookie_manager import (
    load_cookies_from_chrome_sqlite,
    save_cookies_to_json,
    GOOGLE_AUTH_DOMAINS,
)

CHROME_USER_DATA = Path(os.environ["LOCALAPPDATA"]) / "Google" / "Chrome" / "User Data"
PROFILE = CHROME_USER_DATA / "Default"  # konto Comarch
OUT = Path.home() / ".notebooklm-agent" / "cookies.json"

print("=" * 60)
print("  Ekstrakcja ciasteczek z głównego profilu Chrome")
print("=" * 60)
print(f"\n  Profil źródłowy: {PROFILE}")
print(f"  Plik wynikowy:   {OUT}")
print()

# Sprawdź czy Chrome jest zamknięty (próba skopiowania)
import shutil, tempfile
db_candidates = [
    PROFILE / "Network" / "Cookies",
    PROFILE / "Cookies",
]
db = next((p for p in db_candidates if p.exists()), None)
if db is None:
    print("BŁĄD: Nie znaleziono pliku Cookies!")
    sys.exit(1)

print(f"  Plik Cookies: {db}")
with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as tmp:
    tmp_path = tmp.name
try:
    shutil.copy2(db, tmp_path)
    print("  Kopia pliku Cookies: OK (Chrome zamknięty ✓)")
except PermissionError:
    print("  BŁĄD: Chrome jest otwarty — zamknij Chrome i spróbuj ponownie!")
    sys.exit(1)
finally:
    try:
        os.unlink(tmp_path)
    except Exception:
        pass

# Wyciągnij ciasteczka
print("\n  Odczytuję i odszyfrowuję ciasteczka...")
cookies = load_cookies_from_chrome_sqlite(PROFILE)
print(f"  Łącznie: {len(cookies)} ciasteczek")

# Statystyki
google = [c for c in cookies if any(
    c["domain"].endswith(d.lstrip(".")) or c["domain"] == d
    for d in GOOGLE_AUTH_DOMAINS
)]
notebooklm = [c for c in cookies if "notebooklm" in c.get("domain", "")]
empty = [c for c in google if not c.get("value")]

print(f"  Google Auth: {len(google)} (pustych: {len(empty)})")
print(f"  NotebookLM: {len(notebooklm)} ciasteczek")

for c in notebooklm:
    val = c["value"][:30] if c["value"] else "(puste)"
    print(f"    🍪 {c['name']:25s} = {val}")

if empty:
    print(f"\n  UWAGA: {len(empty)} ciasteczek bez wartości (DPAPI problem?)")
    for c in empty[:3]:
        print(f"    - {c['name']} ({c['domain']})")
else:
    print("\n  ✅ Wszystkie ciasteczka odszyfrowane poprawnie!")

# Zapisz
save_cookies_to_json(cookies, OUT)
print(f"\n  ✅ Zapisano {len(cookies)} ciasteczek do: {OUT}")
print()
print("  Następny krok — test cookie-based auth:")
print("    python notebooklm_agent/_test_cookie_auth.py")

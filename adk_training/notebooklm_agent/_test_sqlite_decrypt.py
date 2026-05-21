"""Test odczytu i deszyfrowania Chrome SQLite (DPAPI) → zapis cookies.json."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from notebooklm_agent.cookie_manager import (
    load_cookies_from_chrome_sqlite,
    load_cookies_from_json,
    save_cookies_to_json,
    GOOGLE_AUTH_DOMAINS,
)

profile_dir = Path.home() / ".notebooklm-agent" / "browser-profile" / "Default"
print("=== Odczyt i deszyfrowanie Chrome SQLite (DPAPI) ===")
print(f"Profil: {profile_dir}")
print()

cookies = load_cookies_from_chrome_sqlite(profile_dir)
print(f"Lacznie wczytano: {len(cookies)} ciasteczek")

# Filtruj Google Auth
google = [
    c for c in cookies
    if any(
        c["domain"].endswith(d.lstrip(".")) or c["domain"] == d
        for d in GOOGLE_AUTH_DOMAINS
    )
]
print(f"Google Auth: {len(google)} ciasteczek")
print()

header = f"{'Domena':40s}  {'Nazwa':30s}  {'Wartosc[:20]':22s}  OK?"
print(header)
print("-" * len(header))
empty_count = 0
for c in google:
    val = c["value"]
    ok = "✓" if val else "✗ (brak wartosci)"
    preview = val[:20] if val else "(puste)"
    print(f"{c['domain']:40s}  {c['name']:30s}  {preview:22s}  {ok}")
    if not val:
        empty_count += 1

print()
print(f"Odszyfrowane poprawnie: {len(google) - empty_count}/{len(google)}")

# Zapisz do cookies.json
out = Path.home() / ".notebooklm-agent" / "cookies.json"
save_cookies_to_json(cookies, out)
print(f"\nZapisano {len(cookies)} ciasteczek do: {out}")

# Weryfikacja pliku (save_cookies_to_json zapisuje jako array → load_cookies_from_json)
loaded_back = load_cookies_from_json(out)
assert len(loaded_back) == len(cookies), "Niezgodnosc po zapisie!"
print(f"Weryfikacja zapisu: OK ({len(loaded_back)} ciasteczek)")

if empty_count > 0:
    print(f"\nUWAGA: {empty_count} ciasteczek ma pusta wartosc.")
    print("  Mozliwe przyczyny: profil nie jest zalogowany lub DPAPI nie moze odszyfrowac.")
else:
    print("\n=== SUKCES: Wszystkie ciasteczka odszyfrowane poprawnie ===")

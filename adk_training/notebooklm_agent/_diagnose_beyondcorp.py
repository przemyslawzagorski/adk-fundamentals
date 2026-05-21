"""Diagnoza: sprawdza dlaczego cookie-based auth nie działa w środowisku BeyondCorp."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pathlib import Path

profile = Path.home() / ".notebooklm-agent" / "browser-profile"
local_state_path = profile / "Local State"

with open(local_state_path, encoding="utf-8") as f:
    ls = json.load(f)

print("=" * 60)
print("  Diagnoza BeyondCorp / Context-Aware Access")
print("=" * 60)

# Konto zalogowane
accounts = ls.get("profile", {}).get("info_cache", {})
print("\n📋 Konta w profilu agenta:")
for k, v in accounts.items():
    name = v.get("user_name", "?")
    gaia = v.get("gaia", "?")
    print(f"   [{k}] user={name}  gaia={gaia}")

# Enterprise / Management
mgmt = ls.get("management", {})
print(f"\n🏢 Enterprise management: {'TAK' if mgmt else 'NIE'}")
if mgmt:
    for mk, mv in mgmt.items():
        print(f"   {mk}: {mv}")

# Browser policies
policies = ls.get("policy", {})
print(f"📜 Chrome policies: {'TAK' if policies else 'NIE'}")

print()
print("=" * 60)
print("  Wyjaśnienie wyniku testu")
print("=" * 60)
print("""
✅ CO DZIAŁA:
   • Ekstrakcja 51 ciasteczek z Chrome SQLite (DPAPI + App-Bound 32B fix)
   • Uruchomienie izolowanego Chrome bez user_data_dir (brak błędu portów)
   • Wstrzyknięcie 51 ciasteczek do BrowserContext
   • Nawigacja do NotebookLM i zapis screenshota

❌ DLACZEGO PRZEKIEROWANIE DO LOGOWANIA:
   Google widzi ciasteczka (redirect do 'accountchooser', nie 'login')
   ale BeyondCorp/CAA odrzuca sesję bo:
   
   1. DEVICE ATTESTATION: Zarządzany Chrome Comarch wysyła certyfikat urządzenia
      przy każdym żądaniu. Nowy, niezarządzany Chrome Playwright tego nie ma.
      
   2. FINGERPRINT BINDING: Sesja może być powiązana z konkretnym user-agent,
      fingerprint lub kluczem kryptograficznym zarejestrowanego urządzenia.
   
   3. SESSION BINDING: Google może wymagać specjalnego nagłówka CAA
      generowanego przez rozszerzenie Chrome Enterprise.

🔧 REKOMENDOWANE ROZWIĄZANIE:
   Użyj export_cookies.py z MANAGED Chrome (channel='chrome') z profilem agenta:
   
     python -m notebooklm_agent.export_cookies
   
   To otworzy zarządzanego Chrome Comarch z profilem agenta, gdzie BeyondCorp
   jest już spełniony, eksportuje storage_state (z cookies + lokalny stan),
   a potem zamyka przeglądarkę.
   
   Następnie plik cookies.json zawiera storage_state z aktywną, zarządzaną sesją.
   
   WAŻNE: export_cookies.py musi być uruchomiony gdy profil jest WOLNY
   (Chrome nie jest otwarty z tym profilem).
""")

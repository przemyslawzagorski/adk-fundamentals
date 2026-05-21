"""Znajdź główny profil Chrome z zalogowanym kontem Comarch."""
import json, sqlite3, shutil, tempfile, os
from pathlib import Path

CHROME_USER_DATA = Path(os.environ["LOCALAPPDATA"]) / "Google" / "Chrome" / "User Data"

print(f"Chrome User Data: {CHROME_USER_DATA}")
print(f"Istnieje: {CHROME_USER_DATA.exists()}")
print()

if not CHROME_USER_DATA.exists():
    print("BRAK głównej instalacji Chrome!")
    exit(1)

# Local State — lista profili i zalogowanych kont
local_state_path = CHROME_USER_DATA / "Local State"
with open(local_state_path, encoding="utf-8") as f:
    ls = json.load(f)

profiles = ls.get("profile", {}).get("info_cache", {})
print(f"{'Profil':15s}  {'Email':45s}  {'Cookies Google':>14s}  {'OSID':>6s}")
print("-" * 90)

for profile_name, info in profiles.items():
    email = info.get("user_name", "?")
    profile_dir = CHROME_USER_DATA / profile_name

    # Policz ciasteczka Google
    google_count = 0
    osid_found = False
    for cookies_path in [
        profile_dir / "Network" / "Cookies",
        profile_dir / "Cookies",
    ]:
        if not cookies_path.exists():
            continue
        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as tmp:
            tmp_path = tmp.name
        shutil.copy2(cookies_path, tmp_path)
        try:
            con = sqlite3.connect(tmp_path)
            google_count = con.execute(
                "SELECT COUNT(*) FROM cookies WHERE host_key LIKE '%.google.com' OR host_key LIKE '%.googleapis.com'"
            ).fetchone()[0]
            osid_row = con.execute(
                "SELECT name FROM cookies WHERE name='OSID' AND host_key='notebooklm.google.com'"
            ).fetchone()
            osid_found = osid_row is not None
            con.close()
        except Exception:
            pass
        finally:
            try:
                os.unlink(tmp_path)
            except PermissionError:
                pass
        break

    osid_str = "TAK ✓" if osid_found else "NIE"
    print(f"{profile_name:15s}  {email:45s}  {google_count:>14}  {osid_str:>6s}")

print()
print("WSKAZÓWKA: Użyj profilu z OSID=TAK i emailem Comarch.")
print(f"Ścieżka: {CHROME_USER_DATA} / <nazwa_profilu>")

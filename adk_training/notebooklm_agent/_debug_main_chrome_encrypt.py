"""Diagnostyka formatu szyfrowania w głównym profilu Chrome."""
import os, sys, json, sqlite3, shutil, tempfile, base64
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pathlib import Path
from collections import Counter
import win32crypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

CHROME_USER_DATA = Path(os.environ["LOCALAPPDATA"]) / "Google" / "Chrome" / "User Data"
PROFILE = CHROME_USER_DATA / "Default"
DB = PROFILE / "Network" / "Cookies"

# Master key
with open(CHROME_USER_DATA / "Local State", encoding="utf-8") as f:
    ls = json.load(f)
key_b64 = ls["os_crypt"]["encrypted_key"]
key_bytes = base64.b64decode(key_b64)[5:]
master_key = win32crypt.CryptUnprotectData(key_bytes, None, None, None, 0)[1]
print(f"Master key: {len(master_key)} B  hex={master_key[:8].hex()}...")

# Kopiuj DB
with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as tmp:
    tmp_path = tmp.name
shutil.copy2(DB, tmp_path)

con = sqlite3.connect(tmp_path)
rows = con.execute(
    "SELECT name, host_key, encrypted_value FROM cookies "
    "WHERE host_key IN ('notebooklm.google.com', '.google.com', 'accounts.google.com') "
    "LIMIT 20"
).fetchall()
con.close()
try:
    os.unlink(tmp_path)
except Exception:
    pass

# Zlicz prefiksy
prefix_counter = Counter()
print(f"\n{'Cookie':30s}  {'Domain':30s}  {'Prefix':6s}  {'Len':>5s}")
print("-" * 80)
for name, host, enc_val in rows:
    enc = bytes(enc_val)
    prefix = enc[:3]
    prefix_str = prefix.decode("ascii", errors="replace")
    prefix_counter[prefix_str] += 1
    print(f"{name:30s}  {host:30s}  {prefix_str!r:6s}  {len(enc):>5d}")

    # Próba v10 dekrypcji
    if prefix == b"v10":
        try:
            nonce = enc[3:15]
            plaintext = AESGCM(master_key).decrypt(nonce, enc[15:], None)
            # Skup się na ASCII po 32B prefix
            if len(plaintext) > 32:
                candidate = plaintext[32:].decode("ascii", errors="replace")
                printable = all(0x20 <= b <= 0x7E for b in plaintext[32:])
                print(f"  v10 decrypt: {'OK' if printable else 'PARTIAL'} → {candidate[:40]!r}")
            else:
                print(f"  v10 decrypt: {plaintext.decode('utf-8', errors='replace')[:40]!r}")
        except Exception as e:
            print(f"  v10 decrypt FAIL: {e}")
    elif prefix == b"v20":
        print(f"  v20 = App-Bound Encryption (Chrome 127+, wymaga Chrome binary)")
    else:
        print(f"  nieznany prefix hex={prefix.hex()}")

print(f"\nPodsumowanie prefiksów: {dict(prefix_counter)}")

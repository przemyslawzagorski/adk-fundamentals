"""Debug: analiza formatu odszyfrowanych wartości ciasteczek Chrome 127+."""
import sqlite3, shutil, tempfile, os, json, base64
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import win32crypt

profile_root = Path.home() / ".notebooklm-agent" / "browser-profile"
with open(profile_root / "Local State", encoding="utf-8") as f:
    ls = json.load(f)
key_bytes = base64.b64decode(ls["os_crypt"]["encrypted_key"])[5:]
master_key = win32crypt.CryptUnprotectData(key_bytes, None, None, None, 0)[1]

db = profile_root / "Default" / "Network" / "Cookies"
with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as tmp:
    tmp_path = tmp.name
shutil.copy2(db, tmp_path)

con = sqlite3.connect(tmp_path)
rows = con.execute(
    "SELECT name, host_key, value, encrypted_value FROM cookies "
    "WHERE host_key IN ('.google.com', 'notebooklm.google.com') "
    "ORDER BY name LIMIT 8"
).fetchall()
con.close()
try:
    os.unlink(tmp_path)
except PermissionError:
    pass

print("=== Analiza struktury odszyfrowanych wartości ===\n")
for name, host, value, enc_val in rows:
    enc = bytes(enc_val)
    prefix = enc[:3]
    if prefix == b"v10":
        nonce = enc[3:15]
        ct = enc[15:]
        plaintext = AESGCM(master_key).decrypt(nonce, ct, None)
        print(f"Cookie: {name} ({host})")
        print(f"  Plaintext len: {len(plaintext)}")
        print(f"  Hex (pełny): {plaintext.hex()}")
        # Znajdź pierwszy printable ASCII byte
        ascii_start = 0
        for i, b in enumerate(plaintext):
            if 0x20 <= b <= 0x7E:
                ascii_start = i
                break
        binary_prefix_len = ascii_start
        text_part = plaintext[ascii_start:].decode("utf-8", errors="replace")
        print(f"  Binary prefix: {binary_prefix_len} bajtów")
        print(f"  ASCII value:   {text_part}")
        print()

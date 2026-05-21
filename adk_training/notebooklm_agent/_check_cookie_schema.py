"""Narzędzie diagnostyczne — sprawdza schemat tabeli cookies w Chrome SQLite."""
import sqlite3, shutil, tempfile, os
from pathlib import Path

db = Path.home() / ".notebooklm-agent" / "browser-profile" / "Default" / "Network" / "Cookies"
print(f"DB: {db}")

with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as tmp:
    tmp_path = tmp.name
shutil.copy2(db, tmp_path)

con = sqlite3.connect(tmp_path)
try:
    schema = con.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='cookies'").fetchone()
    print("\nSchema:")
    print(schema[0])
    print()
    cols = con.execute("PRAGMA table_info(cookies)").fetchall()
    print(f"{'cid':4s}  {'name':40s}  {'type':15s}  notnull  dflt")
    print("-" * 80)
    for c in cols:
        print(f"{c[0]:<4}  {c[1]:40s}  {c[2]:15s}  {c[3]}       {c[4]}")
finally:
    con.close()
    os.unlink(tmp_path)

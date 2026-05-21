"""export_via_extension.py — Eksport cookies przez Chrome Extension.

Architektura:
  1. Python uruchamia lokalny HTTP server na porcie 8765
  2. Chrome startuje z prawdziwym profilem + --load-extension (nasz exporter)
  3. Chrome otwiera NotebookLM normalnie (BeyondCorp happy — prawdziwy profil)
  4. Extension czyta WSZYSTKIE cookies (w tym HTTPOnly) przez chrome.cookies API
  5. Extension POSTuje cookies do Python serwera → zapisuje cookies.json
  6. Brak CDP, brak Playwright, brak pipe — czyste rozwiązanie

Wymaganie: Chrome MUSI być zamknięty przed uruchomieniem.
"""
from __future__ import annotations
import os, sys, json, subprocess, threading, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

from notebooklm_agent.config import CONFIG

CHROME_USER_DATA = Path(os.environ["LOCALAPPDATA"]) / "Google" / "Chrome" / "User Data"
CHROME_EXE = Path(os.environ.get("PROGRAMFILES", r"C:\Program Files")) / "Google" / "Chrome" / "Application" / "chrome.exe"
EXTENSION_DIR = Path(__file__).parent / "cookie_exporter_extension"
OUT = Path(CONFIG.data_dir) / "cookies.json"
TARGET_URL = CONFIG.default_notebook_url or "https://notebooklm.google.com"
PORT = 8765


class _CookieHandler(BaseHTTPRequestHandler):
    """Prosty HTTP handler — odbiera cookies z extension i sygnalizuje gotowość."""

    received: list = []
    done: threading.Event = threading.Event()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        cookies = json.loads(body)
        _CookieHandler.received.extend(cookies)
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(b'{"ok":true}')
        _CookieHandler.done.set()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, *_):
        pass


def export_via_extension(profile_subdir: str = "Default", out: Path = OUT) -> bool:
    if not CHROME_EXE.exists():
        print(f"BŁĄD: Chrome nie znaleziony: {CHROME_EXE}"); return False
    if not EXTENSION_DIR.exists():
        print(f"BŁĄD: Extension nie znaleziona: {EXTENSION_DIR}"); return False

    print("=" * 60)
    print("  Eksport cookies przez Chrome Extension")
    print("=" * 60)
    print(f"  Profil:    {CHROME_USER_DATA / profile_subdir}")
    print(f"  Extension: {EXTENSION_DIR}")
    print(f"  Wynik:     {out}\n")

    # Usuń lock files
    for lock in [CHROME_USER_DATA / "SingletonLock", CHROME_USER_DATA / "SingletonSocket"]:
        lock.unlink(missing_ok=True)

    # Uruchom HTTP server
    server = HTTPServer(("localhost", PORT), _CookieHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    print(f"  ✅ Serwer HTTP nasłuchuje na porcie {PORT}")

    # Uruchom Chrome z extension
    args = [
        str(CHROME_EXE),
        f"--profile-directory={profile_subdir}",
        f"--user-data-dir={CHROME_USER_DATA}",
        f"--load-extension={EXTENSION_DIR}",
        "--disable-features=DevToolsDebuggingRestrictions",
        "--disable-blink-features=AutomationControlled",
        "--no-first-run",
        "--no-default-browser-check",
        "--hide-crash-restore-bubble",
        TARGET_URL,   # Chrome otwiera NotebookLM od razu
    ]
    print(f"  🚀 Startuję Chrome z extension...")
    print(f"     --load-extension={EXTENSION_DIR.name}")
    proc = subprocess.Popen(args)

    print(f"\n  ⏳ Czekam na cookies z extension (maks 5 min)...")
    print(f"     Chrome powinien otworzyć NotebookLM automatycznie.")
    print(f"     Jeśli nie — wpisz ręcznie: {TARGET_URL}\n")

    if _CookieHandler.done.wait(timeout=300):
        cookies = _CookieHandler.received
        print(f"  ✅ Otrzymano {len(cookies)} cookies!")
        server.shutdown()

        # Konwertuj do formatu storage_state
        storage_state = {
            "cookies": [
                {
                    "name": c.get("name", ""),
                    "value": c.get("value", ""),
                    "domain": c.get("domain", ""),
                    "path": c.get("path", "/"),
                    "expires": c.get("expirationDate", -1),
                    "httpOnly": c.get("httpOnly", False),
                    "secure": c.get("secure", False),
                    "sameSite": c.get("sameSite", "Lax"),
                }
                for c in cookies
            ],
            "origins": [],
        }
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(storage_state, f, indent=2)

        google = [c for c in cookies if ".google.com" in c.get("domain", "")]
        empty = [c for c in google if not c.get("value")]
        print(f"  📊 Google Auth: {len(google)}, pustych: {len(empty)}")

        if google and not empty:
            print(f"\n  ✅ SUKCES → {out}")
            print(f"  Następny krok: python notebooklm_agent/_test_cookie_auth.py")
            return True
        print(f"  ⚠️  Eksport częściowy")
        return bool(google)
    else:
        print("  ❌ Timeout — extension nie wysłała cookies.")
        print("     Możliwe przyczyny:")
        print("     1. Enterprise blokuje --load-extension")
        print("     2. NotebookLM się nie załadował (BeyondCorp block)")
        print("     3. Extension nie ma uprawnień do localhost")
        server.shutdown()
        return False


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--profile", default="Default")
    p.add_argument("--out", default=str(OUT))
    a = p.parse_args()
    ok = export_via_extension(a.profile, Path(a.out))
    sys.exit(0 if ok else 1)

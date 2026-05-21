"""export_from_cdp.py — Eksport sesji z działającego Chrome przez CDP.

Podłącza się do Chrome uruchomionego przez start_chrome_cdp.ps1,
eksportuje storage_state (cookies plaintext — Chrome odszyfrowuje v20 sam)
i zapisuje do cookies.json.

Chrome uruchomiony przez CDP NIE ma flagi automatyzacji → BeyondCorp działa!

Użycie:
  1. Uruchom Chrome z CDP:
       .\\notebooklm_agent\\start_chrome_cdp.ps1
  2. Zaloguj się do NotebookLM w otwartym Chrome
  3. Uruchom ten skrypt:
       python notebooklm_agent/export_from_cdp.py
"""
from __future__ import annotations
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from playwright.sync_api import sync_playwright

from notebooklm_agent.config import CONFIG

CDP_URL  = os.getenv("CHROME_CDP_URL", "http://localhost:9222")
OUT      = Path(CONFIG.data_dir) / "cookies.json"
TARGET   = CONFIG.default_notebook_url or "https://notebooklm.google.com"


def is_logged_in(url: str) -> bool:
    return "notebooklm.google.com" in url and "accounts.google.com" not in url


def export_from_cdp(cdp_url: str = CDP_URL, out: Path = OUT) -> bool:
    print("=" * 60)
    print("  Eksport cookies przez Chrome DevTools Protocol (CDP)")
    print("=" * 60)
    print(f"\n  CDP:   {cdp_url}")
    print(f"  Wynik: {out}")
    print()

    with sync_playwright() as pw:
        # Połącz z działającym Chrome (NIE otwiera nowego okna)
        print("  🔌 Łączę z Chrome przez CDP...")
        try:
            browser = pw.chromium.connect_over_cdp(cdp_url)
        except Exception as e:
            print(f"  ❌ Brak połączenia: {e}")
            print()
            print("  Uruchom Chrome z CDP:")
            print("    .\\notebooklm_agent\\start_chrome_cdp.ps1")
            print("  Zaloguj się do NotebookLM, a potem uruchom ten skrypt ponownie.")
            return False

        contexts = browser.contexts
        if not contexts:
            print("  ❌ Brak kontekstów przeglądarki!")
            browser.close()
            return False

        ctx = contexts[0]
        print(f"  ✅ Połączono. Konteksty: {len(contexts)}, strony: {len(ctx.pages)}")

        # Sprawdź czy NotebookLM jest otwarty
        notebooklm_page = None
        for page in ctx.pages:
            if "notebooklm.google.com" in page.url:
                notebooklm_page = page
                break

        if notebooklm_page and is_logged_in(notebooklm_page.url):
            print(f"  ✅ NotebookLM otwarty i zalogowany: {notebooklm_page.url[:70]}")
        else:
            # Otwórz NotebookLM w nowej karcie (w istniejącym kontekście)
            print(f"  🌐 Nawiguję do NotebookLM: {TARGET}")
            page = ctx.new_page()
            try:
                page.goto(TARGET, timeout=30_000, wait_until="domcontentloaded")
            except Exception as e:
                if "interrupted" not in str(e):
                    print(f"  ⚠️  {e}")
            time.sleep(3)

            url = page.url
            if not is_logged_in(url):
                print(f"  ⚠️  Przekierowanie do: {url[:80]}")
                print()
                print("  Zaloguj się w oknie Chrome (BeyondCorp powinien działać")
                print("  bo Chrome uruchomiony BEZ flagi automatyzacji).")
                print("  Po zalogowaniu naciśnij ENTER tutaj...")
                input("\n  [Naciśnij ENTER po zalogowaniu] ")
                time.sleep(2)
                url = page.url
                if not is_logged_in(url):
                    print(f"  ❌ Nadal nie zalogowany ({url[:60]})")
                    browser.close()
                    return False

            print(f"  ✅ Zalogowany! URL: {page.url[:70]}")

        # Eksport storage_state — Chrome odszyfrowuje v20 automatycznie
        print(f"\n  💾 Eksportuję storage_state (Chrome odszyfrowuje v20)...")
        out.parent.mkdir(parents=True, exist_ok=True)
        ctx.storage_state(path=str(out))

        # Weryfikacja
        with open(out, encoding="utf-8") as f:
            state = json.load(f)
        cookies = state.get("cookies", [])
        google = [c for c in cookies if ".google.com" in c.get("domain", "")]
        notebooklm_c = [c for c in cookies if "notebooklm" in c.get("domain", "")]
        empty = [c for c in google if not c.get("value")]

        print(f"  📊 Łącznie: {len(cookies)} cookies")
        print(f"  🔑 Google Auth: {len(google)} (pustych: {len(empty)})")
        print(f"  🗒️  NotebookLM: {len(notebooklm_c)}")
        for c in notebooklm_c:
            val = c.get("value", "")[:40]
            ok = "✓" if val else "✗"
            print(f"     {ok} {c['name']:25s} = {val}")

        browser.close()

    success = len(google) > 0 and len(empty) == 0
    if success:
        print(f"\n  ✅ SUKCES — cookies.json gotowy: {out}")
        print()
        print("  Uruchom test:")
        print("    python notebooklm_agent/_test_cookie_auth.py")
    else:
        print(f"\n  ⚠️  Eksport zakończony. Pustych ciasteczek: {len(empty)}")
    return success


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--cdp", default=CDP_URL, help=f"URL CDP (domyślnie: {CDP_URL})")
    parser.add_argument("--out", default=str(OUT), help=f"Plik wyjściowy")
    a = parser.parse_args()
    ok = export_from_cdp(a.cdp, Path(a.out))
    sys.exit(0 if ok else 1)

"""setup_auth.py — jednorazowe logowanie Google w dedykowanym profilu agenta.

TRYB KORPORACYJNY (BeyondCorp / Context-Aware Access):
- Używa zainstalowanego Chrome (channel='chrome') z OSOBNYM profilem agenta
- Profil agenta NIE koliduje z otwartym Chrome użytkownika
- Po jednorazowym logowaniu sesja jest zapisana — agent startuje bez pytania

Użycie:
    python -m notebooklm_agent.setup_auth
    python notebooklm_agent/setup_auth.py
"""

from __future__ import annotations

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from playwright.sync_api import sync_playwright

from notebooklm_agent.config import CONFIG

TARGET_URL = CONFIG.default_notebook_url or "https://notebooklm.google.com"
AGENT_PROFILE = Path(CONFIG.chrome_profile_dir)


def is_logged_in(url: str) -> bool:
    return (
        "accounts.google.com" not in url
        and "access-denied" not in url
        and "signin" not in url.lower()
        and "notebooklm.google.com" in url
    )


def setup_auth() -> None:
    AGENT_PROFILE.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("  NotebookLM Agent — Jednorazowe logowanie Google")
    print("=" * 60)
    print(f"\n📁 Profil agenta: {AGENT_PROFILE}")
    print(f"🌐 Cel: {TARGET_URL}")
    print()
    print("ℹ️  Otworzy się OSOBNE okno Chrome (niezależne od Twojego Chrome).")
    print("   Zaloguj się w nim na konto Comarch — email powinien być wpisany.")
    print("   Po zalogowaniu skrypt automatycznie wykryje sukces i zamknie okno.\n")

    with sync_playwright() as pw:
        args = [
            "--disable-blink-features=AutomationControlled",
            "--no-first-run",
            "--no-default-browser-check",
        ]

        # Uruchom zarządzanego Chrome z osobnym profilem agenta
        for channel in ("chrome", None):
            try:
                label = "zarządzanego Chrome" if channel else "Chromium (fallback)"
                print(f"🚀 Uruchamiam {label}...")
                ctx = pw.chromium.launch_persistent_context(
                    user_data_dir=str(AGENT_PROFILE),
                    headless=False,
                    channel=channel,
                    args=args,
                    viewport={"width": 1280, "height": 800},
                )
                print(f"   ✅ Przeglądarka uruchomiona.")
                break
            except Exception as e:
                if channel:
                    print(f"   ⚠️  Chrome niedostępny ({e}), próbuję Chromium...")
                else:
                    print(f"\n❌ Nie można uruchomić przeglądarki: {e}")
                    sys.exit(1)

        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        print(f"\n🌐 Nawiguję do NotebookLM...")
        try:
            page.goto(TARGET_URL, timeout=30_000, wait_until="domcontentloaded")
        except Exception as e:
            if "interrupted" not in str(e):
                print(f"   ⚠️  {e}")
        time.sleep(3)

        url = page.url
        if is_logged_in(url):
            print(f"\n✅ Już zalogowany — sesja aktywna!")
        elif "access-denied" in url:
            print(f"\n❌ BeyondCorp zablokował dostęp: {url[:80]}")
            print("   Upewnij się że masz zainstalowany zarządzany Chrome Comarch.")
            ctx.close()
            sys.exit(1)
        else:
            print(f"\n🔐 Strona logowania. Zaloguj się w otwartym oknie Chrome.")
            print(f"   (email powinien być wstępnie wpisany — kliknij Dalej i podaj hasło)\n")

            for elapsed in range(0, 300, 2):
                time.sleep(2)
                url = page.url
                if is_logged_in(url):
                    print(f"\n✅ Zalogowano pomyślnie!")
                    break
                if "access-denied" in url:
                    print(f"\n❌ BeyondCorp zablokował dostęp.")
                    ctx.close()
                    sys.exit(1)
                if elapsed % 30 == 28:
                    print(f"   ⏳ Czekam na zalogowanie... ({elapsed+2}s / 300s)")
            else:
                print("\n❌ Timeout (5 min) — spróbuj ponownie.")
                ctx.close()
                sys.exit(1)

        print(f"\n💾 Sesja zapisana w: {AGENT_PROFILE}")
        print("\n🎉 Gotowe! Możesz teraz uruchomić agenta:")
        print("   adk web notebooklm_agent")
        print("\n   (Twój normalny Chrome może być otwarty — agent używa osobnego profilu)\n")
        ctx.close()


if __name__ == "__main__":
    setup_auth()

"""export_cookies.py — Jednorazowy eksport sesji Google z profilu agenta do pliku JSON.

Otwiera istniejący profil Playwright (np. ~/.notebooklm-agent/browser-profile),
nawiguje do NotebookLM aby "odświeżyć" ciasteczka sesji, a następnie eksportuje
pełny storage_state do pliku JSON.

Plik JSON może być potem użyty przez PlaywrightComputer w trybie cookie-based
(COOKIES_PATH=~/.notebooklm-agent/cookies.json) — bez potrzeby otwierania profilu.

Użycie:
    python -m notebooklm_agent.export_cookies
    python notebooklm_agent/export_cookies.py [--out ŚCIEŻKA]
"""

from __future__ import annotations

import argparse
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from playwright.sync_api import sync_playwright

from notebooklm_agent.config import CONFIG
from notebooklm_agent.cookie_manager import (
    export_storage_state_from_context,
    save_cookies_to_json,
    load_cookies_from_storage_state,
    GOOGLE_AUTH_DOMAINS,
)

DEFAULT_OUT = Path(CONFIG.data_dir) / "cookies.json"
TARGET_URL = CONFIG.default_notebook_url or "https://notebooklm.google.com"
AGENT_PROFILE = Path(CONFIG.chrome_profile_dir)


def is_logged_in(url: str) -> bool:
    return (
        "accounts.google.com" not in url
        and "access-denied" not in url
        and "signin" not in url.lower()
        and "notebooklm.google.com" in url
    )


def export_cookies(out_path: Path) -> bool:
    """Eksportuj ciasteczka z profilu agenta do pliku JSON.

    Returns:
        True jeśli eksport się powiódł i użytkownik był zalogowany.
    """
    if not AGENT_PROFILE.exists():
        print(f"\n❌ Profil agenta nie istnieje: {AGENT_PROFILE}")
        print("   Uruchom najpierw: python -m notebooklm_agent.setup_auth")
        return False

    print("=" * 60)
    print("  NotebookLM Agent — Eksport ciasteczek sesji")
    print("=" * 60)
    print(f"\n📁 Profil źródłowy: {AGENT_PROFILE}")
    print(f"🌐 URL: {TARGET_URL}")
    print(f"💾 Plik wynikowy: {out_path}")
    print()

    with sync_playwright() as pw:
        args = [
            "--disable-blink-features=AutomationControlled",
            "--no-first-run",
            "--no-default-browser-check",
        ]

        print("🚀 Otwieram profil agenta...")
        for channel in ("chrome", None):
            try:
                ctx = pw.chromium.launch_persistent_context(
                    user_data_dir=str(AGENT_PROFILE),
                    headless=False,
                    channel=channel,
                    args=args,
                    viewport={"width": 1280, "height": 800},
                )
                label = "Chrome" if channel else "Chromium"
                print(f"   ✅ {label} uruchomiony.")
                break
            except Exception as e:
                if channel:
                    print(f"   ⚠️  Chrome niedostępny ({e}), próbuję Chromium...")
                else:
                    print(f"\n❌ Nie można uruchomić przeglądarki: {e}")
                    return False

        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        print(f"\n🌐 Nawiguję do NotebookLM...")
        try:
            page.goto(TARGET_URL, timeout=30_000, wait_until="domcontentloaded")
        except Exception as e:
            if "interrupted" not in str(e):
                print(f"   ⚠️  {e}")
        time.sleep(3)

        url = page.url
        logged_in = is_logged_in(url)

        if not logged_in:
            if "accounts.google.com" in url:
                print(f"\n⚠️  Nie jesteś zalogowany ({url[:60]}).")
                print("   Zaloguj się w otwartym oknie, następnie naciśnij ENTER.")
                input("\n   [Naciśnij ENTER po zalogowaniu] ")
                time.sleep(2)
                url = page.url
                logged_in = is_logged_in(url)
            if not logged_in:
                print(f"\n❌ Nie udało się zalogować. Eksport przerwany.")
                ctx.close()
                return False

        print(f"\n✅ Zalogowany — URL: {url[:70]}")

        # Eksportuj pełny storage_state
        print(f"\n💾 Eksportuję storage_state...")
        export_storage_state_from_context(ctx, out_path)

        # Pokaż statystyki
        cookies = load_cookies_from_storage_state(out_path)
        google_cookies = [c for c in cookies if any(
            c.get("domain", "").endswith(d.lstrip(".")) or c.get("domain") == d
            for d in GOOGLE_AUTH_DOMAINS
        )]
        print(f"   📊 Łącznie: {len(cookies)} ciasteczek")
        print(f"   🔑 Google Auth: {len(google_cookies)} ciasteczek")

        ctx.close()

    print(f"\n🎉 Gotowe! Plik ciasteczek: {out_path}")
    print("\nAby użyć trybu cookie-based, ustaw w .env:")
    print(f"   COOKIES_PATH={out_path}")
    print("\nLub uruchom test:")
    print(f"   python notebooklm_agent/_test_cookie_auth.py")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Eksport ciasteczek sesji Google z profilu agenta.")
    parser.add_argument("--out", type=str, default=str(DEFAULT_OUT),
                        help=f"Ścieżka pliku wynikowego (domyślnie: {DEFAULT_OUT})")
    args = parser.parse_args()

    success = export_cookies(Path(args.out))
    sys.exit(0 if success else 1)

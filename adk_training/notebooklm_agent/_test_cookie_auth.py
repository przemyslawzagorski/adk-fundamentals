"""Test weryfikujący mechanizm uwierzytelniania przez ciasteczka.

Przepływ:
  1. [Opcjonalnie] Eksport storage_state z istniejącego profilu agenta
  2. Uruchom izolowaną przeglądarkę (bez user_data_dir) z PlaywrightComputer cookie-based
  3. Wstrzyknij ciasteczka
  4. Nawiguj do NotebookLM — sprawdź URL i screenshot
  5. Weryfikuj: brak przekierowania na accounts.google.com
  6. [Opcjonalnie] Odśwież snapshot sesji

Użycie:
    # Krok 1 — eksport ciasteczek (jednorazowo, gdy profil NIE jest zablokowany):
    python notebooklm_agent/export_cookies.py

    # Krok 2 — test cookie-based auth:
    python notebooklm_agent/_test_cookie_auth.py

    # Lub podaj ścieżkę ręcznie:
    python notebooklm_agent/_test_cookie_auth.py --cookies /ścieżka/cookies.json
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

from pathlib import Path

from notebooklm_agent.config import CONFIG
from notebooklm_agent.computer.playwright_computer import PlaywrightComputer
from notebooklm_agent.cookie_manager import load_cookies_from_json, load_cookies_from_storage_state

# ── Pomocnicze ──────────────────────────────────────────────────────────────

DEFAULT_COOKIES = Path(CONFIG.data_dir) / "cookies.json"
TARGET_URL = CONFIG.default_notebook_url or "https://notebooklm.google.com"
SCREENSHOT_OUT = Path(__file__).parent / "test_cookie_screenshot.png"
REFRESHED_COOKIES_OUT = Path(CONFIG.data_dir) / "cookies_refreshed.json"


def _check_logged_in(url: str) -> bool:
    return (
        "accounts.google.com" not in url
        and "access-denied" not in url
        and "signin" not in url.lower()
        and ("notebooklm.google.com" in url or "google.com" in url)
    )


def _print_section(title: str) -> None:
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}")


# ── Główna funkcja testowa ──────────────────────────────────────────────────

async def run_test(cookies_path: Path, refresh: bool = False) -> bool:
    """Uruchom pełny test uwierzytelniania cookie-based.

    Returns:
        True jeśli test zakończony sukcesem.
    """
    _print_section("Test 1: Weryfikacja pliku ciasteczek")
    if not cookies_path.exists():
        print(f"  ❌ Plik ciasteczek nie istnieje: {cookies_path}")
        print(f"  Uruchom najpierw: python notebooklm_agent/export_cookies.py")
        return False

    # load_cookies_from_json obsługuje oba formaty: JSON array i storage_state dict
    cookies = load_cookies_from_json(cookies_path)
    google_cookies = [c for c in cookies if ".google.com" in c.get("domain", "")]
    print(f"  ✅ Wczytano {len(cookies)} ciasteczek ({len(google_cookies)} Google Auth)")
    for c in google_cookies[:5]:
        print(f"     🍪 {c['name'][:30]:30s}  domain={c['domain']}")

    _print_section("Test 2: Uruchomienie przeglądarki (cookie-based, bez profilu)")
    computer = PlaywrightComputer(
        cookies_path=str(cookies_path),
        headless=False,
    )
    try:
        t0 = time.perf_counter()
        await computer.initialize()
        elapsed = time.perf_counter() - t0
        print(f"  ✅ Przeglądarka gotowa w {elapsed:.1f}s")
        print(f"     Tryb: cookie-based (bez user_data_dir, bez CDP)")

        _print_section("Test 3: Nawigacja do NotebookLM")
        print(f"  🌐 URL docelowy: {TARGET_URL}")
        state = await computer.navigate(TARGET_URL)
        print(f"  📍 Aktualny URL: {state.url}")

        logged_in = _check_logged_in(state.url)
        if logged_in:
            print(f"  ✅ ZALOGOWANY — brak przekierowania do accounts.google.com!")
        else:
            print(f"  ❌ NIE ZALOGOWANY — przekierowanie na stronę logowania.")
            print(f"     Możliwe przyczyny:")
            print(f"     • Ciasteczka wygasły — uruchom ponownie export_cookies.py")
            print(f"     • Brak wymaganych ciasteczek Google Auth")
            print(f"     • BeyondCorp/CAA wymaga zarządzanego urządzenia")

        _print_section("Test 4: Zrzut ekranu")
        state2 = await computer.current_state()
        with open(SCREENSHOT_OUT, "wb") as f:
            f.write(state2.screenshot)
        print(f"  📸 Screenshot zapisany: {SCREENSHOT_OUT}")
        print(f"  📏 Rozmiar: {len(state2.screenshot) / 1024:.1f} KB")

        if logged_in and refresh:
            _print_section("Test 5: Odświeżenie snapshotu sesji")
            await computer.save_session(str(REFRESHED_COOKIES_OUT))
            # save_session używa Playwright storage_state() → format dict → load_cookies_from_storage_state
            refreshed = load_cookies_from_storage_state(REFRESHED_COOKIES_OUT)
            print(f"  ✅ Nowy snapshot: {len(refreshed)} ciasteczek → {REFRESHED_COOKIES_OUT}")

        return logged_in

    finally:
        print("\n  🔒 Zamykam przeglądarkę...")
        await computer.close()


async def main(cookies_path: Path, refresh: bool) -> None:
    print("=" * 60)
    print("  NotebookLM Agent — Test Cookie-Based Authentication")
    print("=" * 60)
    print(f"\n  Plik ciasteczek: {cookies_path}")
    print(f"  URL:             {TARGET_URL}")
    print(f"  Profil Chrome:   (brak — izolowana instancja)")
    print(f"  Odśwież snapshot: {'tak' if refresh else 'nie'}")

    success = await run_test(cookies_path, refresh=refresh)

    _print_section("Podsumowanie")
    if success:
        print("  ✅ TEST ZALICZONY — uwierzytelnianie przez ciasteczka DZIAŁA!")
        print()
        print("  Następne kroki:")
        print(f"  1. Ustaw COOKIES_PATH={cookies_path} w pliku .env")
        print("  2. Usuń lub zignoruj CHROME_PROFILE_DIR (nieużywane w trybie cookie)")
        print("  3. Uruchom agenta: adk web notebooklm_agent")
    else:
        print("  ❌ TEST NIEZALICZONY — sesja nieważna lub BeyondCorp blokuje dostęp.")
        print()
        print("  Działania naprawcze:")
        print("  • Zaloguj się przez: python -m notebooklm_agent.setup_auth")
        print("  • Wyeksportuj sesję: python -m notebooklm_agent.export_cookies")
        print("  • Sprawdź czy Chrome Comarch jest zainstalowany (BeyondCorp)")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test uwierzytelniania przez ciasteczka.")
    parser.add_argument(
        "--cookies",
        type=str,
        default=str(DEFAULT_COOKIES),
        help=f"Ścieżka do pliku cookies.json (domyślnie: {DEFAULT_COOKIES})",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        default=False,
        help="Po pomyślnym teście odśwież snapshot sesji (zapisz nowy plik cookies).",
    )
    a = parser.parse_args()
    asyncio.run(main(Path(a.cookies), refresh=a.refresh))

"""CLI do uruchamiania ADK Web Tester."""

from __future__ import annotations

import asyncio
import logging
import os
import sys

# Dodaj parent do path (aby importy działały z poziomu katalogu modułu)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from module_21_adk_tester.agent import AgentTesterSystem, ProTesterSystem
from module_21_adk_tester.config import CONFIG
from module_21_adk_tester.tools.test_scenarios import ALL_MODULES, get_available_modules, set_fast_mode


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


async def run_tests(
    module_ids: list[str],
    headless: bool = False,
    model: str | None = None,
    adk_url: str | None = None,
) -> None:
    """Uruchom testy dla podanych modułów."""

    print("=" * 70)
    print("  ADK Web Tester — Automatyczne testowanie agentów")
    print("=" * 70)
    print(f"  Model:      {model or CONFIG.computer_use_model}")
    print(f"  ADK Web:    {adk_url or CONFIG.adk_web_url}")
    print(f"  Headless:   {headless}")
    print(f"  Moduły:     {', '.join(module_ids)}")
    print(f"  Raporty:    {CONFIG.reports_dir}")
    from module_21_adk_tester.tools.test_scenarios import _fast_mode
    if _fast_mode:
        print(f"  Tryb:       FAST (1 scenariusz/moduł)")
    print("=" * 70)
    print()

    system = AgentTesterSystem(
        model=model,
        headless=headless,
        adk_web_url=adk_url,
    )

    try:
        print("Inicjalizuję agenta testera (uruchamiam przeglądarkę)...")
        await system.initialize()
        print("Agent gotowy!\n")

        print(f"Rozpoczynam testy {len(module_ids)} modułów...")
        print("=" * 70)
        result = await system.test_modules(module_ids)
        print()
        print("─" * 70)
        print(result if result else "(brak odpowiedzi od agenta)")
        print("─" * 70)

    except KeyboardInterrupt:
        print("\n\nPrzerwano przez użytkownika.")
    except Exception as e:
        print(f"\n❌ Błąd: {e}")
        logging.exception("Test error")
    finally:
        print("\nZamykam agenta testera...")
        video_path = await system.close()
        if video_path:
            print(f"🎬 Nagranie testu: {video_path}")
        print("Zakończono.")


async def interactive_session(
    headless: bool = False,
    model: str | None = None,
    adk_url: str | None = None,
) -> None:
    """Tryb interaktywny — użytkownik podaje komendy."""

    print("=" * 70)
    print("  ADK Web Tester — Tryb interaktywny")
    print("=" * 70)
    print(f"  Model:      {model or CONFIG.computer_use_model}")
    print(f"  ADK Web:    {adk_url or CONFIG.adk_web_url}")
    print(f"  Headless:   {headless}")
    print("=" * 70)
    print()
    print("Komendy:")
    print("  /quit, /exit     — zakończ sesję")
    print("  /modules         — pokaż dostępne moduły")
    print("  /test 01 02      — przetestuj moduły 01 i 02")
    print("  /test all        — przetestuj wszystkie moduły")
    print("  (tekst)          — wyślij dowolną instrukcję do agenta")
    print()

    system = AgentTesterSystem(
        model=model,
        headless=headless,
        adk_web_url=adk_url,
    )

    try:
        print("Inicjalizuję agenta testera...")
        await system.initialize()
        print("Agent gotowy!\n")

        while True:
            try:
                user_input = input("\n🧪 Tester> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n")
                break

            if not user_input:
                continue

            if user_input.startswith("/"):
                parts = user_input.split()
                cmd = parts[0].lower()

                if cmd in ("/quit", "/exit"):
                    break
                elif cmd == "/modules":
                    print(get_available_modules())
                    continue
                elif cmd == "/test":
                    ids = parts[1:]
                    if not ids:
                        print("  Użycie: /test 01 02 lub /test all")
                        continue
                    if "all" in ids:
                        ids = list(ALL_MODULES.keys())
                    invalid = [i for i in ids if i not in ALL_MODULES]
                    if invalid:
                        print(f"  Nieznane moduły: {invalid}. Dostępne: {list(ALL_MODULES.keys())}")
                        continue
                    print(f"  Testuję moduły: {ids}")
                    result = await system.test_modules(ids)
                    print("\n" + "─" * 60)
                    print(result if result else "(brak odpowiedzi)")
                    print("─" * 60)
                    continue
                else:
                    print(f"  Nieznana komenda: {cmd}")
                    continue

            # Dowolna instrukcja dla agenta
            print("\n🤖 Agent pracuje...")
            try:
                result = await system.run_test(user_input)
                print("\n" + "─" * 60)
                print(result if result else "(brak odpowiedzi)")
                print("─" * 60)
            except Exception as e:
                print(f"\n  ❌ Błąd: {e}")
                logging.exception("Agent error")

    finally:
        print("\nZamykam agenta testera...")
        video_path = await system.close()
        if video_path:
            print(f"🎬 Nagranie sesji: {video_path}")
        print("Do widzenia!")


# ── PRO mode ────────────────────────────────────────────────────────────────


async def pro_discover_and_test(
    app_url: str,
    headless: bool = False,
    model: str | None = None,
    discover_only: bool = False,
    profile_path: str | None = None,
) -> None:
    """Tryb PRO: discovery + testy dowolnej web aplikacji."""

    mode_label = "Discovery Only" if discover_only else (
        "Test from Profile" if profile_path else "Full (Discovery → Test → Report)"
    )

    print("=" * 70)
    print("  ADK Web Tester — Tryb PRO")
    print("=" * 70)
    print(f"  Mode:       {mode_label}")
    print(f"  App URL:    {app_url}")
    print(f"  Model:      {model or CONFIG.computer_use_model}")
    print(f"  Headless:   {headless}")
    if profile_path:
        print(f"  Profile:    {profile_path}")
    print("=" * 70)
    print()

    system = ProTesterSystem(
        model=model,
        headless=headless,
        app_url=app_url,
    )

    try:
        print("Inicjalizuję PRO testera...")
        await system.initialize()
        print("PRO tester gotowy!\n")

        if discover_only:
            print("Faza: DISCOVERY — eksploracja UI...")
            result = await system.discover_only(app_url)
        elif profile_path:
            print("Faza: TEST z gotowego profilu...")
            result = await system.test_from_profile(profile_path)
        else:
            print("Faza: FULL CYCLE — discovery → testy → raport...")
            result = await system.discover_and_test(app_url)

        print("\n" + "─" * 70)
        print(result if result else "(brak odpowiedzi od agenta)")
        print("─" * 70)

    except KeyboardInterrupt:
        print("\n\nPrzerwano przez użytkownika.")
    except Exception as e:
        print(f"\n❌ Błąd: {e}")
        logging.exception("PRO test error")
    finally:
        print("\nZamykam PRO testera...")
        video_path = await system.close()
        if video_path:
            print(f"🎬 Nagranie testu: {video_path}")
        print("Zakończono.")


async def pro_interactive_session(
    app_url: str,
    headless: bool = False,
    model: str | None = None,
) -> None:
    """Tryb PRO interaktywny — swobodne komendy do pro testera."""

    print("=" * 70)
    print("  ADK Web Tester — Tryb PRO Interaktywny")
    print("=" * 70)
    print(f"  App URL:    {app_url}")
    print(f"  Model:      {model or CONFIG.computer_use_model}")
    print(f"  Headless:   {headless}")
    print("=" * 70)
    print()
    print("Komendy:")
    print("  /quit, /exit          — zakończ sesję")
    print("  /discover             — uruchom discovery UI")
    print("  /test                 — pełny cykl (discovery + testy + raport)")
    print("  /profile <ścieżka>   — załaduj profil i testuj")
    print("  /profiles             — pokaż zapisane profile")
    print("  (tekst)               — wyślij instrukcję do agenta PRO")
    print()

    system = ProTesterSystem(
        model=model,
        headless=headless,
        app_url=app_url,
    )

    try:
        print("Inicjalizuję PRO testera...")
        await system.initialize()
        print("PRO tester gotowy!\n")

        while True:
            try:
                user_input = input("\n🔬 PRO> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n")
                break

            if not user_input:
                continue

            if user_input.startswith("/"):
                parts = user_input.split(maxsplit=1)
                cmd = parts[0].lower()

                if cmd in ("/quit", "/exit"):
                    break
                elif cmd == "/discover":
                    print("🔍 Discovery UI...")
                    result = await system.discover_only(app_url)
                    print("\n" + "─" * 60)
                    print(result if result else "(brak odpowiedzi)")
                    print("─" * 60)
                    continue
                elif cmd == "/test":
                    print("🧪 Pełny cykl: discovery → testy → raport...")
                    result = await system.discover_and_test(app_url)
                    print("\n" + "─" * 60)
                    print(result if result else "(brak odpowiedzi)")
                    print("─" * 60)
                    continue
                elif cmd == "/profile":
                    if len(parts) < 2:
                        print("  Użycie: /profile <ścieżka_do_profilu.json>")
                        continue
                    print(f"📋 Test z profilu: {parts[1]}")
                    result = await system.test_from_profile(parts[1])
                    print("\n" + "─" * 60)
                    print(result if result else "(brak odpowiedzi)")
                    print("─" * 60)
                    continue
                elif cmd == "/profiles":
                    from module_21_adk_tester.tools.pro_report import list_saved_profiles as lsp
                    print(lsp())
                    continue
                else:
                    print(f"  Nieznana komenda: {cmd}")
                    continue

            print("\n🤖 PRO agent pracuje...")
            try:
                result = await system.run_command(user_input)
                print("\n" + "─" * 60)
                print(result if result else "(brak odpowiedzi)")
                print("─" * 60)
            except Exception as e:
                print(f"\n  ❌ Błąd: {e}")
                logging.exception("PRO agent error")

    finally:
        print("\nZamykam PRO testera...")
        video_path = await system.close()
        if video_path:
            print(f"🎬 Nagranie sesji: {video_path}")
        print("Do widzenia!")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="ADK Web Tester — testowanie agentów ADK przez przeglądarkę")
    subparsers = parser.add_subparsers(dest="mode", help="Tryb pracy")

    # == Standard mode (domyślny — kompatybilność wsteczna) ==
    std = subparsers.add_parser("standard", aliases=["std"], help="Standardowy tryb ADK web")
    std.add_argument("--module", "-m", nargs="+", default=None, help="ID modułów (np. 01 02 04 12)")
    std.add_argument("--interactive", "-i", action="store_true", help="Tryb interaktywny")
    std.add_argument("--headless", action="store_true", default=False, help="Headless (bez okna)")
    std.add_argument("--fast", "-f", action="store_true", help="1 scenariusz na moduł")
    std.add_argument("--model", help="Model Gemini")
    std.add_argument("--adk-url", help="URL ADK web (domyślnie localhost:8000)")
    std.add_argument("--verbose", "-v", action="store_true", help="Verbose")

    # == PRO mode ==
    pro = subparsers.add_parser("pro", help="Tryb PRO — discovery + testy dowolnej web aplikacji")
    pro.add_argument("url", help="URL web aplikacji do testowania")
    pro.add_argument("--discover-only", "-d", action="store_true", help="Tylko discovery (bez testów)")
    pro.add_argument("--profile", "-p", help="Ścieżka do profilu JSON (pomiń discovery)")
    pro.add_argument("--interactive", "-i", action="store_true", help="Tryb interaktywny PRO")
    pro.add_argument("--headless", action="store_true", default=False, help="Headless (bez okna)")
    pro.add_argument("--model", help="Model Gemini")
    pro.add_argument("--verbose", "-v", action="store_true", help="Verbose")

    args = parser.parse_args()

    # Domyślnie: standard interactive (kompatybilność wsteczna)
    if args.mode is None:
        # Stary tryb — sprawdź czy są flagi starych argumentów
        parser_compat = argparse.ArgumentParser()
        parser_compat.add_argument("--module", "-m", nargs="+", default=None)
        parser_compat.add_argument("--interactive", "-i", action="store_true")
        parser_compat.add_argument("--headless", action="store_true", default=False)
        parser_compat.add_argument("--fast", "-f", action="store_true")
        parser_compat.add_argument("--model", default=None)
        parser_compat.add_argument("--adk-url", default=None)
        parser_compat.add_argument("--verbose", "-v", action="store_true")
        args = parser_compat.parse_args()
        args.mode = "standard"

    verbose = getattr(args, "verbose", False)
    setup_logging(verbose)

    if args.mode in ("standard", "std"):
        if getattr(args, "fast", False):
            set_fast_mode(True)

        if getattr(args, "interactive", False) or not getattr(args, "module", None):
            asyncio.run(interactive_session(
                headless=args.headless,
                model=args.model,
                adk_url=getattr(args, "adk_url", None),
            ))
        else:
            module_ids = args.module
            if "all" in module_ids:
                module_ids = list(ALL_MODULES.keys())

            invalid = [i for i in module_ids if i not in ALL_MODULES]
            if invalid:
                print(f"Nieznane moduły: {invalid}")
                print(f"Dostępne: {list(ALL_MODULES.keys())}")
                sys.exit(1)

            asyncio.run(run_tests(
                module_ids=module_ids,
                headless=args.headless,
                model=args.model,
                adk_url=getattr(args, "adk_url", None),
            ))

    elif args.mode == "pro":
        if args.interactive:
            asyncio.run(pro_interactive_session(
                app_url=args.url,
                headless=args.headless,
                model=args.model,
            ))
        else:
            asyncio.run(pro_discover_and_test(
                app_url=args.url,
                headless=args.headless,
                model=args.model,
                discover_only=args.discover_only,
                profile_path=args.profile,
            ))


if __name__ == "__main__":
    main()

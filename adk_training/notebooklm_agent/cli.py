"""Interaktywny CLI do testowania NotebookLM Agent V2."""

from __future__ import annotations

import asyncio
import logging
import os
import sys
import uuid
from datetime import datetime

# Dodaj parent do path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from notebooklm_agent.agent import NotebookLMAgentSystem
from notebooklm_agent.config import CONFIG


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    # Wycisz zbędne logi
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


async def interactive_session(
    notebook_url: str | None = None,
    headless: bool = False,
    model: str | None = None,
) -> None:
    """Prowadź interaktywną konwersację z NotebookLM."""

    conversation_id = f"conv-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    session_id = conversation_id

    print("=" * 70)
    print("  NotebookLM Agent V2 — Interaktywna sesja")
    print("=" * 70)
    print(f"  Model:          {model or CONFIG.computer_use_model}")
    print(f"  Notebook URL:   {notebook_url or CONFIG.default_notebook_url or '(brak)'}")
    print(f"  Headless:       {headless}")
    print(f"  Conversation:   {conversation_id}")
    print(f"  Zapis:          {CONFIG.conversations_dir}")
    print("=" * 70)
    print()
    print("Komendy:")
    print("  /quit, /exit     — zakończ sesję")
    print("  /save            — eksportuj konwersację do Markdown")
    print("  /history         — pokaż historię konwersacji")
    print("  /notebooks       — pokaż bibliotekę notebooków")
    print("  /select <id>     — wybierz notebook")
    print("  /status          — pokaż status agenta")
    print()

    agent_system = NotebookLMAgentSystem(
        model=model,
        headless=headless,
        notebook_url=notebook_url,
    )

    try:
        print("Inicjalizuję agenta (uruchamiam przeglądarkę)...")
        await agent_system.initialize()

        # Sprawdź logowanie
        logged_in = await agent_system.ensure_logged_in()
        if not logged_in:
            print("Nie udało się zalogować. Zamykam.")
            return

        print("Agent gotowy!\n")

        turn = 0
        while True:
            try:
                question = input("\n🧑 Ty: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n")
                break

            if not question:
                continue

            # Komendy
            if question.startswith("/"):
                cmd = question.lower().split()
                if cmd[0] in ("/quit", "/exit"):
                    break
                elif cmd[0] == "/save":
                    md = agent_system.conversations.export_markdown(conversation_id)
                    if md:
                        path = os.path.join(CONFIG.conversations_dir, f"{conversation_id}.md")
                        with open(path, "w", encoding="utf-8") as f:
                            f.write(md)
                        print(f"  Zapisano: {path}")
                    else:
                        print("  Brak konwersacji do zapisu.")
                    continue
                elif cmd[0] == "/history":
                    convs = agent_system.conversations.list_conversations()
                    if convs:
                        for c in convs[:10]:
                            print(f"  {c['id']} — {c['turns']} tur, {c.get('updated_at', '?')}")
                    else:
                        print("  Brak zapisanych konwersacji.")
                    continue
                elif cmd[0] == "/notebooks":
                    print(f"  {agent_system.library.describe_for_prompt()}")
                    continue
                elif cmd[0] == "/select" and len(cmd) > 1:
                    try:
                        entry = agent_system.library.select(cmd[1])
                        print(f"  Aktywny notebook: {entry.name} ({entry.url})")
                    except ValueError as e:
                        print(f"  Błąd: {e}")
                    continue
                elif cmd[0] == "/status":
                    print(f"  Model: {agent_system.model}")
                    print(f"  Initialized: {agent_system._initialized}")
                    print(f"  Turns: {turn}")
                    active = agent_system.library.get_active()
                    if active:
                        print(f"  Active notebook: {active.name} (uses={active.use_count})")
                    continue
                else:
                    print(f"  Nieznana komenda: {question}")
                    continue

            # Pytanie do agenta
            turn += 1
            print(f"\n🤖 Agent (tura {turn})...")
            print("  [Przeglądarka pracuje — agent widzi ekran i wchodzi w interakcję z NotebookLM]")

            try:
                answer = await agent_system.ask(
                    question=question,
                    session_id=session_id,
                    conversation_id=conversation_id,
                )
                print()
                print("─" * 60)
                print(answer if answer else "(brak odpowiedzi)")
                print("─" * 60)
            except Exception as e:
                print(f"\n  ❌ Błąd: {e}")
                logging.exception("Agent error")

    finally:
        print("\nZamykam agenta...")
        await agent_system.close()

        # Auto-save
        md = agent_system.conversations.export_markdown(conversation_id)
        if md:
            path = os.path.join(CONFIG.conversations_dir, f"{conversation_id}.md")
            with open(path, "w", encoding="utf-8") as f:
                f.write(md)
            print(f"Konwersacja zapisana: {path}")

        print("Do widzenia!")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="NotebookLM Agent V2 — CLI")
    parser.add_argument("--notebook-url", "-u", help="URL notebooka NotebookLM")
    parser.add_argument("--headless", action="store_true", default=False, help="Tryb headless (bez okna)")
    parser.add_argument("--model", "-m", help="Model Gemini do użycia")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    args = parser.parse_args()

    setup_logging(args.verbose)
    asyncio.run(interactive_session(
        notebook_url=args.notebook_url,
        headless=args.headless,
        model=args.model,
    ))


if __name__ == "__main__":
    main()

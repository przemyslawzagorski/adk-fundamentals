"""Test: wieloturowa rozmowa z NotebookLM → raport Markdown.

Uruchomienie:
    python notebooklm_agent/_test_conversation_report.py
"""

from __future__ import annotations

import asyncio
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

QUESTIONS = [
    "Jaki jest temat / tytuł tego notebooka? O czym ogólnie traktuje?",
    "Jakie są główne źródła dołączone do tego notebooka? Wymień je.",
    "Jakie są kluczowe wnioski lub najważniejsze informacje z tego notebooka?",
    "Czy są jakieś ciekawe fakty, liczby lub statystyki wspomniane w źródłach?",
    "Dla kogo ten materiał jest przeznaczony i do czego może być przydatny?",
]

NOTEBOOK_URL = "https://notebooklm.google.com/notebook/643d114f-b4ba-4817-9cb9-b569df97429b"
TIMEOUT_PER_QUESTION = 300  # sekund


# ─── ask z verbose logowaniem zdarzeń + timeout ──────────────────────────────

async def ask_with_timeout(system, question: str, session_id: str) -> str:
    """Pyta agenta z timeoutem i loguje każde zdarzenie ADK."""
    from google.genai.types import Content, Part

    active = system.library.get_active()
    notebook_url = system._notebook_url
    if active:
        notebook_url = active.url

    user_message = (
        f"Otwórz notebook pod adresem {notebook_url} i zadaj mu pytanie:\n\n"
        f"{question}\n\n"
        f"Odczytaj pełną odpowiedź z NotebookLM i zwróć ją dosłownie."
    )

    session = await system._session_service.get_session(
        app_name="notebooklm_agent", user_id="user", session_id=session_id,
    )
    if session is None:
        session = await system._session_service.create_session(
            app_name="notebooklm_agent", user_id="user", session_id=session_id,
        )

    user_content = Content(role="user", parts=[Part(text=user_message)])

    response_text = ""
    step = 0

    async def _run():
        nonlocal response_text, step
        async for event in system.runner.run_async(
            user_id="user",
            session_id=session_id,
            new_message=user_content,
        ):
            step += 1
            author = getattr(event, "author", "?")
            is_final = event.is_final_response()
            has_text = bool(event.content and event.content.parts
                            and any(p.text for p in event.content.parts))
            has_fc = bool(event.content and event.content.parts
                          and any(hasattr(p, "function_call") and p.function_call
                                  for p in event.content.parts))
            print(f"     step {step:03d} | author={author} | final={is_final} "
                  f"| text={has_text} | tool_call={has_fc}")

            if is_final and has_text:
                response_text = "\n".join(
                    p.text for p in event.content.parts if p.text
                )

    await asyncio.wait_for(_run(), timeout=TIMEOUT_PER_QUESTION)
    return response_text


# ─── Główna logika ───────────────────────────────────────────────────────────

async def run_conversation() -> list[dict]:
    from notebooklm_agent.agent import NotebookLMAgentSystem

    print("=" * 65)
    print("  NotebookLM — Automatyczna rozmowa + raport")
    print("=" * 65)
    print(f"  Notebook:  {NOTEBOOK_URL}")
    print(f"  Pytań:     {len(QUESTIONS)}")
    print(f"  Timeout:   {TIMEOUT_PER_QUESTION}s / pytanie")
    print()

    system = NotebookLMAgentSystem(notebook_url=NOTEBOOK_URL)
    await system.initialize()

    turns = []
    session_id = f"report-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    for i, question in enumerate(QUESTIONS, 1):
        print(f"\n[{i}/{len(QUESTIONS)}] 🧑 {question}")
        t0 = asyncio.get_event_loop().time()
        try:
            answer = await ask_with_timeout(system, question, session_id)
            elapsed = asyncio.get_event_loop().time() - t0
            turns.append({"question": question, "answer": answer or "[brak tekstu w odpowiedzi]"})
            preview = (answer[:100] + "…") if len(answer) > 100 else answer
            print(f"     ✅ {elapsed:.0f}s | {len(answer)} znaków | {preview}")
        except asyncio.TimeoutError:
            elapsed = asyncio.get_event_loop().time() - t0
            print(f"     ⏰ TIMEOUT po {elapsed:.0f}s — przechodzę do następnego pytania")
            turns.append({"question": question, "answer": "[TIMEOUT — agent nie zwrócił odpowiedzi]"})
        except Exception as e:
            print(f"     ❌ Błąd: {e}")
            turns.append({"question": question, "answer": f"[BŁĄD: {e}]"})

    await system.computer.close()
    return turns


# ─── Raport ──────────────────────────────────────────────────────────────────

def build_report(turns: list[dict]) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# Raport z NotebookLM", "",
        f"**Notebook:** {NOTEBOOK_URL}  ",
        f"**Data:** {now}  ",
        f"**Pytań:** {len(turns)}", "",
        "---", "",
    ]
    for i, t in enumerate(turns, 1):
        lines += [f"## {i}. {t['question']}", "", t["answer"], "", "---", ""]
    lines.append("*Raport wygenerowany automatycznie przez NotebookLM Agent.*")
    return "\n".join(lines)


def save_report(content: str) -> Path:
    out_dir = Path.home() / ".notebooklm-agent" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    fname = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    path = out_dir / fname
    path.write_text(content, encoding="utf-8")
    return path


async def main():
    turns = await run_conversation()
    print("\n" + "=" * 65)
    report = build_report(turns)
    path = save_report(report)
    print(f"  ✅ Raport → {path}")
    print("─" * 65)
    print(report)
    print("─" * 65)


if __name__ == "__main__":
    asyncio.run(main())

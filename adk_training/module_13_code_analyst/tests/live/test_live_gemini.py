"""
Live smoke test - PRAWDZIWY Gemini przez Vertex AI.

Pomijany automatycznie gdy:
  - GOOGLE_CLOUD_PROJECT nie jest ustawione, LUB
  - ENV RUN_LIVE_TESTS != "1"

Uruchomienie:
    $env:RUN_LIVE_TESTS="1"
    $env:GOOGLE_CLOUD_PROJECT="twoj-projekt"
    $env:GOOGLE_GENAI_USE_VERTEXAI="1"
    python -m pytest tests/live -v -m live

UWAGA: koszty API! Kazdy test = 1-3 wywolania Gemini.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool
from google.genai import types

from file_tools import list_project_files, read_project_file


pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        os.environ.get("RUN_LIVE_TESTS") != "1",
        reason="Live tests wylaczone. Ustaw RUN_LIVE_TESTS=1 aby uruchomic.",
    ),
    pytest.mark.skipif(
        not os.environ.get("GOOGLE_CLOUD_PROJECT"),
        reason="Brak GOOGLE_CLOUD_PROJECT - live test wymaga Vertex AI.",
    ),
]


APP_NAME = "live_smoke"
USER_ID = "tester"
MODEL = os.environ.get("CODE_ANALYST_LLM_MODEL", "gemini-2.0-flash")


def _make_tools(repo_path: str) -> list[FunctionTool]:
    def read_file(file_path: str) -> dict:
        """Read a file from the project repository."""
        return read_project_file(repo_path, file_path)

    def list_files(pattern: str = "") -> dict:
        """List files in the project repository."""
        return list_project_files(repo_path, pattern or None)

    return [FunctionTool(func=read_file), FunctionTool(func=list_files)]


@pytest.fixture()
def sample_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "calculator.py").write_text(
        "def add(a: int, b: int) -> int:\n"
        "    '''Sumuje dwie liczby calkowite.'''\n"
        "    return a + b\n"
        "\n"
        "def multiply(a: int, b: int) -> int:\n"
        "    '''Mnozy dwie liczby.'''\n"
        "    return a * b\n",
        encoding="utf-8",
    )
    (repo / "README.md").write_text(
        "# Calculator\nProsty modul do arytmetyki.\n", encoding="utf-8"
    )
    return repo


async def _run(runner: Runner, user_text: str) -> tuple[str, list[str]]:
    session = await runner.session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID
    )
    final = ""
    tool_calls: list[str] = []
    content = types.Content(role="user", parts=[types.Part(text=user_text)])
    async for event in runner.run_async(
        user_id=USER_ID, session_id=session.id, new_message=content
    ):
        if getattr(event, "content", None) and event.content.parts:
            for p in event.content.parts:
                fc = getattr(p, "function_call", None)
                if fc is not None:
                    tool_calls.append(fc.name)
        if event.is_final_response() and event.content and event.content.parts:
            txt = "".join(
                (p.text or "") for p in event.content.parts if hasattr(p, "text")
            )
            if txt.strip():
                final = txt.strip()
    return final, tool_calls


async def test_live_gemini_should_answer_simple_question():
    """Sanity: Gemini odpowiada na proste pytanie (bez tooli)."""
    agent = LlmAgent(
        name="simple_agent",
        model=MODEL,
        instruction="Jestes asystentem. Odpowiadaj krotko, po polsku.",
    )
    runner = Runner(
        agent=agent, app_name=APP_NAME,
        session_service=InMemorySessionService(),
    )
    final, _ = await _run(runner, "Ile to 2+2? Odpowiedz jedna liczba.")
    assert final, "Brak odpowiedzi z modelu"
    assert "4" in final, f"Oczekiwano '4' w odpowiedzi, dostalem: {final!r}"


async def test_live_gemini_should_call_real_tool(sample_repo: Path):
    """Gemini powinien wywolac list_files, gdy pytam o zawartosc repo."""
    agent = LlmAgent(
        name="code_analyst",
        model=MODEL,
        instruction=(
            "Jestes analitykiem kodu. Zeby odpowiedziec o strukturze repo, "
            "UZYJ narzedzia list_files. Nie zgaduj."
        ),
        tools=_make_tools(str(sample_repo)),
    )
    runner = Runner(
        agent=agent, app_name=APP_NAME,
        session_service=InMemorySessionService(),
    )
    final, tool_calls = await _run(
        runner, "Jakie pliki sa w tym projekcie?"
    )
    assert "list_files" in tool_calls, f"Gemini nie wywolal list_files, tylko: {tool_calls}"
    # W finalnej odpowiedzi powinno byc co najmniej jedno z nazw plikow
    low = final.lower()
    assert "calculator" in low or "readme" in low, \
        f"Odpowiedz nie wspomina o realnych plikach: {final!r}"


async def test_live_sequential_agent_pipeline(sample_repo: Path):
    """SequentialAgent z dwoma realnymi Gemini - oba musza wypowiedziec sie."""
    analyst = LlmAgent(
        name="code_analyst",
        model=MODEL,
        instruction=(
            "Przeanalizuj plik calculator.py (uzyj read_file). "
            "Krotko (max 3 zdania) opisz co robi."
        ),
        tools=_make_tools(str(sample_repo)),
    )
    architect = LlmAgent(
        name="solution_architect",
        model=MODEL,
        instruction=(
            "Na podstawie analizy poprzedniego agenta zaproponuj "
            "JEDNO ulepszenie (max 2 zdania). Nie pisz kodu."
        ),
    )
    pipeline = SequentialAgent(
        name="analyze_then_recommend", sub_agents=[analyst, architect]
    )
    runner = Runner(
        agent=pipeline, app_name=APP_NAME,
        session_service=InMemorySessionService(),
    )
    final, tool_calls = await _run(
        runner, "Przeanalizuj modul calculator.py i daj rekomendacje."
    )
    assert "read_file" in tool_calls, f"Analyst nie czytal pliku: {tool_calls}"
    assert final, "Brak finalnej odpowiedzi architekta"
    # Architect powinien napisac cos sensownego (minimum kilka slow)
    assert len(final.split()) >= 3, f"Zbyt krotka odpowiedz: {final!r}"

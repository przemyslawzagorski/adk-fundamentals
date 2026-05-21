"""
Demo: pokaz co agent faktycznie robi w teście agentowym (FakeLlm + real ADK).

Uruchomienie:
    python demo_agent_trace.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Dodaj katalog modulu do sys.path (analogicznie jak conftest testow)
_MODULE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_MODULE_DIR))

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool
from google.genai import types

from file_tools import list_project_files, read_project_file, write_project_file
from tests.agent.fake_llm import FakeLlm, call, say


APP_NAME = "demo"
USER_ID = "demo_user"


def _make_tools(repo_path: str) -> list[FunctionTool]:
    def read_file(file_path: str) -> dict:
        """Odczytaj plik z repo."""
        return read_project_file(repo_path, file_path)

    def list_files(pattern: str = "") -> dict:
        """Lista plikow w repo."""
        return list_project_files(repo_path, pattern or None)

    def write_file(file_path: str, content: str) -> dict:
        """Zapisz plik w repo."""
        return write_project_file(repo_path, file_path, content)

    return [FunctionTool(func=read_file), FunctionTool(func=list_files), FunctionTool(func=write_file)]


def _setup_sample_repo(tmp: Path) -> Path:
    repo = tmp / "sample"
    repo.mkdir(parents=True, exist_ok=True)
    (repo / "main.py").write_text(
        "def greet(name):\n    return f'Czesc, {name}!'\n", encoding="utf-8"
    )
    (repo / "utils.py").write_text("PI = 3.14159\n", encoding="utf-8")
    (repo / "README.md").write_text("# Sample repo\n", encoding="utf-8")
    return repo


async def main() -> None:
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        repo = _setup_sample_repo(Path(td))

        analyst_llm = FakeLlm(
            model="fake-analyst", name="analyst",
            script=[
                call("read_file", file_path="main.py"),
                say("Plik main.py zawiera funkcje greet(name) ktora zwraca sformatowane powitanie."),
            ],
        )
        architect_llm = FakeLlm(
            model="fake-architect", name="architect",
            script=[
                say("Rekomendacje: dodac testy jednostkowe dla greet() oraz type hinty."),
            ],
        )

        tools = _make_tools(str(repo))
        analyst = LlmAgent(
            name="code_analyst", model=analyst_llm,
            instruction="Analityk kodu.", tools=tools,
        )
        architect = LlmAgent(
            name="solution_architect", model=architect_llm,
            instruction="Architekt rozwiazan.", tools=tools,
        )
        pipeline = SequentialAgent(name="pipeline", sub_agents=[analyst, architect])

        runner = Runner(
            agent=pipeline, app_name=APP_NAME,
            session_service=InMemorySessionService(),
        )
        session = await runner.session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID
        )

        user_msg = "Przeanalizuj main.py i daj rekomendacje."
        print("=" * 70)
        print(f"USER: {user_msg}")
        print("=" * 70)

        content = types.Content(role="user", parts=[types.Part(text=user_msg)])
        step = 0
        async for ev in runner.run_async(
            user_id=USER_ID, session_id=session.id, new_message=content
        ):
            step += 1
            author = getattr(ev, "author", "?") or "?"
            if ev.content and ev.content.parts:
                for p in ev.content.parts:
                    fc = getattr(p, "function_call", None)
                    fr = getattr(p, "function_response", None)
                    txt = getattr(p, "text", None)
                    if fc is not None:
                        print(f"\n[{step:02d}] 🔧 {author} WOLA NARZEDZIE:")
                        print(f"     -> {fc.name}({dict(fc.args or {})})")
                    elif fr is not None:
                        resp = dict(fr.response or {})
                        # skroc dlugie pola
                        short = {k: (v if not isinstance(v, str) or len(v) < 120 else v[:120] + "…") for k, v in resp.items()}
                        print(f"\n[{step:02d}] 📦 TOOL '{fr.name}' ZWROCIL:")
                        print(f"     {short}")
                    elif txt and txt.strip():
                        marker = "✅ FINAL" if ev.is_final_response() else "💬"
                        print(f"\n[{step:02d}] {marker} {author}: {txt.strip()}")
        print("\n" + "=" * 70)
        print("KONIEC")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())

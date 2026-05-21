"""
Live demo: pokaz co PRAWDZIWY Gemini (Vertex AI) odpowiada.

Wymaga tych samych ENV co live testy:
    $env:RUN_LIVE_TESTS="1"  (nieobowiazkowe tutaj - demo nie ma gatingu)
    $env:GOOGLE_CLOUD_PROJECT="adk-training-pz"
    $env:GOOGLE_CLOUD_LOCATION="us-central1"
    $env:GOOGLE_GENAI_USE_VERTEXAI="1"

Uruchom:
    python demo_live_trace.py
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

_MODULE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_MODULE_DIR))

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool
from google.genai import types

from file_tools import list_project_files, read_project_file


APP_NAME = "live_demo"
USER_ID = "demo"
MODEL = os.environ.get("CODE_ANALYST_LLM_MODEL", "gemini-2.0-flash")


def _make_tools(repo_path: str) -> list[FunctionTool]:
    def read_file(file_path: str) -> dict:
        """Read a file from the repository."""
        return read_project_file(repo_path, file_path)

    def list_files(pattern: str = "") -> dict:
        """List files in the repository."""
        return list_project_files(repo_path, pattern or None)

    return [FunctionTool(func=read_file), FunctionTool(func=list_files)]


def _setup_repo(tmp: Path) -> Path:
    repo = tmp / "calc"
    repo.mkdir(parents=True, exist_ok=True)
    (repo / "calculator.py").write_text(
        "def add(a: int, b: int) -> int:\n"
        "    '''Sumuje dwie liczby calkowite.'''\n"
        "    return a + b\n\n"
        "def divide(a, b):\n"
        "    # UWAGA: brak walidacji b != 0\n"
        "    return a / b\n",
        encoding="utf-8",
    )
    (repo / "README.md").write_text("# Calculator\nMaly modul.\n", encoding="utf-8")
    return repo


async def main() -> None:
    if not os.environ.get("GOOGLE_CLOUD_PROJECT"):
        print("Brak GOOGLE_CLOUD_PROJECT - ustaw ENV i sprobuj ponownie.")
        return

    import tempfile

    with tempfile.TemporaryDirectory() as td:
        repo = _setup_repo(Path(td))
        tools = _make_tools(str(repo))

        analyst = LlmAgent(
            name="code_analyst",
            model=MODEL,
            instruction=(
                "Jestes analitykiem kodu. Najpierw ZAWSZE uzyj narzedzia "
                "list_files aby zobaczyc co jest w repo, potem read_file "
                "aby obejrzec calculator.py. Na koniec opisz PO POLSKU w 2-3 zdaniach "
                "co robi ten kod i jakie znalazles problemy."
            ),
            tools=tools,
        )
        architect = LlmAgent(
            name="solution_architect",
            model=MODEL,
            instruction=(
                "Jestes architektem. Na podstawie analizy z poprzedniego kroku "
                "wypisz 2-3 konkretne rekomendacje refaktoringu PO POLSKU, numerowane."
            ),
        )
        pipeline = SequentialAgent(name="pipeline", sub_agents=[analyst, architect])

        runner = Runner(
            agent=pipeline,
            app_name=APP_NAME,
            session_service=InMemorySessionService(),
        )
        session = await runner.session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID
        )

        user_msg = "Przeanalizuj moj modul calculator.py i daj rekomendacje."
        print("=" * 72)
        print(f"MODEL: {MODEL}")
        print(f"PROJECT: {os.environ.get('GOOGLE_CLOUD_PROJECT')}")
        print(f"LOCATION: {os.environ.get('GOOGLE_CLOUD_LOCATION', '(default)')}")
        print("=" * 72)
        print(f"USER: {user_msg}")
        print("=" * 72)

        content = types.Content(role="user", parts=[types.Part(text=user_msg)])
        step = 0
        async for ev in runner.run_async(
            user_id=USER_ID, session_id=session.id, new_message=content
        ):
            step += 1
            author = getattr(ev, "author", "?") or "?"
            if not ev.content or not ev.content.parts:
                continue
            for p in ev.content.parts:
                fc = getattr(p, "function_call", None)
                fr = getattr(p, "function_response", None)
                txt = getattr(p, "text", None)
                if fc is not None:
                    print(f"\n[{step:02d}] 🔧 {author} WOLA: {fc.name}({dict(fc.args or {})})")
                elif fr is not None:
                    resp = dict(fr.response or {})
                    short = {
                        k: (v if not isinstance(v, str) or len(v) < 200 else v[:200] + "…")
                        for k, v in resp.items()
                    }
                    print(f"\n[{step:02d}] 📦 TOOL '{fr.name}' ZWROCIL: {short}")
                elif txt and txt.strip():
                    marker = "✅ FINAL" if ev.is_final_response() else "💬"
                    print(f"\n[{step:02d}] {marker} {author}:\n{txt.strip()}")
        print("\n" + "=" * 72)
        print("KONIEC")
        print("=" * 72)


if __name__ == "__main__":
    asyncio.run(main())

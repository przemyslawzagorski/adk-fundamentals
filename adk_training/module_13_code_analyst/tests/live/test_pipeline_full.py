"""
Live test: pelny pipeline (_build_sequential_agent) — produkcyjna sciezka.

Weryfikuje:
  - _build_sequential_agent tworzy poprawny SequentialAgent z callbackami telemetrii.
  - analyst + (solution_architect|senior_developer) faktycznie sie komunikuja.
  - telemetria SQLite dostaje wpisy po przejsciu.

UWAGA: koszty API (2 agenty x kilka turn).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# import web.app (Flask-less)
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from code_indexer import CodeIndexer  # noqa: E402

# wazne: importujemy web.app *po* ustawieniu env, bo settings czytane raz
os.environ.setdefault("CODE_ANALYST_API_KEY", "test-live-key")


pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        os.environ.get("RUN_LIVE_TESTS") != "1",
        reason="Live tests wylaczone.",
    ),
    pytest.mark.skipif(
        not os.environ.get("GOOGLE_CLOUD_PROJECT"),
        reason="Brak GOOGLE_CLOUD_PROJECT.",
    ),
]


@pytest.fixture()
def small_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "calc.py").write_text(
        '"""Prosty kalkulator."""\n\n'
        "def add(a: int, b: int) -> int:\n"
        "    return a + b\n\n"
        "def divide(a, b):\n"  # brak type hints + brak walidacji b=0
        "    return a / b\n",
        encoding="utf-8",
    )
    return repo


async def test_live_full_pipeline_analysis_mode(small_repo: Path, tmp_path: Path):
    """Pelny SequentialAgent: analyst -> architect, z telemetria."""
    from web import app as webapp  # noqa: WPS433

    # Podmien sciezke telemetrii na tmp, zeby nie zaburzyc prod bazy
    tel_db = tmp_path / "telemetry.db"
    from telemetry import TelemetryCollector
    webapp.telemetry = TelemetryCollector(db_path=str(tel_db))

    idx_dir = tmp_path / "idx"
    indexer = CodeIndexer(
        project_dir=str(small_repo),
        persist_dir=str(idx_dir),
    )
    indexer.index_project()

    agent = webapp._build_sequential_agent(
        indexer, str(small_repo), mode="analysis"
    )
    assert agent.name.startswith("code_pipeline")
    assert len(agent.sub_agents) == 2
    assert agent.sub_agents[0].name == "code_analyst"
    assert agent.sub_agents[1].name == "solution_architect"

    runner = Runner(
        agent=agent, app_name="full_live",
        session_service=InMemorySessionService(),
    )
    session = await runner.session_service.create_session(
        app_name="full_live", user_id="tester",
    )
    result = await webapp._run_agent_pipeline(
        runner=runner,
        session_id=session.id,
        user_message="Przeanalizuj calc.py i zaproponuj poprawki.",
    )
    assert result["final_response"], result
    assert not result["had_error"], f"Pipeline had_error: {result}"
    # Analyst powinien wywolac read_file/search_code
    tool_calls = [s for s in result["steps"] if s["action"] == "tool_call"]
    assert len(tool_calls) >= 1, f"Brak tool-calli: {result['steps']}"

    # Telemetria: min 2 wpisy (analyst + architect)
    summary = webapp.telemetry.summary(since_hours=1)
    assert summary["total_calls"] >= 2, summary
    agents = {row["agent"] for row in summary["by_agent"]}
    assert "code_analyst" in agents
    assert "solution_architect" in agents

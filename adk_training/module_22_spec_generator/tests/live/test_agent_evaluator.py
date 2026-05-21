"""Live test: ewaluacja Spec Generatora przez oficjalny ADK AgentEvaluator.

Koncepcja (https://adk.dev/evaluate/):
  - `AgentEvaluator.evaluate()` imporotuje moduł (`agent_for_eval`), który udostepnia
    `root_agent`, i uruchamia go na kazdym przypadku z pliku `*.test.json` N razy
    (num_runs). Porownuje `finalResponse` do oczekiwanej odpowiedzi per metryka
    z `test_config.json`.
  - Uzywamy tylko **response_match_score** (ROUGE-1, lokalne, bez LLM judge),
    z bardzo niskim progiem (0.05) - sprawdzamy tylko, ze pipeline zwraca
    niepusta, strukturalnie spojna odpowiedz zawierajaca slowa kluczowe
    (epics, acceptance_criteria, dependencies).
  - `num_runs=1` zeby nie mnozyc kosztow (jeden pelny pipeline ~3 min na Gemini 2.5 Pro).

GATING:
  RUN_LIVE_TESTS=1 + GOOGLE_CLOUD_PROJECT. Bez tego test jest pomijany.

Uruchomienie:
  $env:RUN_LIVE_TESTS="1"; python -m pytest tests/live/test_agent_evaluator.py -v -s -m live
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        os.environ.get("RUN_LIVE_TESTS") != "1",
        reason="Live tests wylaczone (ustaw RUN_LIVE_TESTS=1).",
    ),
    pytest.mark.skipif(
        not os.environ.get("GOOGLE_CLOUD_PROJECT"),
        reason="Brak GOOGLE_CLOUD_PROJECT.",
    ),
]


@pytest.mark.asyncio
async def test_spec_generator_matches_eval_set():
    """Uruchamia AgentEvaluator na spec_gen_basic.test.json.

    Wykorzystuje `agent_for_eval` (wrapper z ustalona konfiguracja: bez NotebookLM,
    max_critique_iterations=1). Wszystkie asercje progowe sa w test_config.json.
    """
    # Import lokalny - pomaga uniknac importu heavy modules podczas collection offline.
    from google.adk.evaluation.agent_evaluator import AgentEvaluator

    eval_dir = Path(__file__).resolve().parents[1] / "eval"
    test_file = eval_dir / "spec_gen_basic.test.json"
    assert test_file.is_file(), f"Brak pliku ewaluacyjnego: {test_file}"

    await AgentEvaluator.evaluate(
        agent_module="agent_for_eval.agent",
        eval_dataset_file_path_or_dir=str(test_file),
        num_runs=1,
        print_detailed_results=True,
    )

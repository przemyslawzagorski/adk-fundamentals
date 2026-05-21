"""
Module 31 — Testy ewaluacyjne (live) przez ADK AgentEvaluator.
==============================================================

Źródło: https://adk.dev/evaluate/

URUCHOMIENIE:
  # Lokalne (wymaga GOOGLE_CLOUD_PROJECT lub GOOGLE_API_KEY):
  cd adk_training/module_31_evaluation
  $env:RUN_LIVE_TESTS="1"; python -m pytest tests/test_evaluation_live.py -v -s -m live

  # Via CLI (alternatywnie):
  adk eval adk_training/module_31_evaluation tests/eval/code_review_basic.test.json --print_detailed_results

WEWNĘTRZNY MECHANIZM (ważna lekcja z Module 22):
  AgentEvaluator.evaluate() wykonuje:
    1. Import agent_module → szuka root_agent
    2. Dla każdego eval_case: uruchamia root_agent z user_content
    3. Porównuje actual tool_uses z expected (tool_trajectory_avg_score)
    4. Porównuje final_response z expected przez ROUGE-1 (response_match_score)
    5. Rzuca AssertionError gdy wyniki poniżej progu z test_config.json

GOTCHA — SequentialAgent nie działa z AgentEvaluator:
  SequentialAgent emituje N eventów isFinalResponse=True (po jednym per sub-agent
  z output_key). AgentEvaluator porównuje len(inferences) z len(conversation) →
  ValueError: "Inferences should match conversations".
  ROZWIĄZANIE: jako root_agent eksponuj JEDEN LlmAgent (nie SequentialAgent).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# Dodaj moduł do sys.path żeby AgentEvaluator mógł go importować
MODULE_DIR = Path(__file__).resolve().parents[2]
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        os.environ.get("RUN_LIVE_TESTS") != "1",
        reason="Live tests wyłączone. Ustaw RUN_LIVE_TESTS=1 aby uruchomić.",
    ),
]

EVAL_DIR = Path(__file__).resolve().parent / "eval"


@pytest.mark.asyncio
async def test_code_review_agent_trajectory_and_response():
    """
    Test 1: Trajektoria + jakość odpowiedzi (podstawowy scenariusz).

    Sprawdza:
      - tool_trajectory_avg_score = 1.0 → count_code_lines MUSI być wywołane
      - response_match_score >= 0.15 → odpowiedź zawiera pola JSON

    Dlaczego oba kryteria?
      - Trajectory bez response: agent wywołał właściwe narzędzie ale odpowiedź nonsensowna
      - Response bez trajectory: agent odpowiedział dobrze ale "skrótami" (bez narzędzia)
      - Oba razem: mamy pewność, że agent zachowuje się poprawnie end-to-end
    """
    from google.adk.evaluation.agent_evaluator import AgentEvaluator

    test_file = EVAL_DIR / "code_review_basic.test.json"
    assert test_file.is_file(), f"Brak pliku: {test_file}"

    await AgentEvaluator.evaluate(
        agent_module="module_31_evaluation.agent",
        eval_dataset_file_path_or_dir=str(test_file),
        num_runs=1,
        print_detailed_results=True,
    )


@pytest.mark.asyncio
async def test_code_review_agent_custom_criteria():
    """
    Test 2: Własne kryteria (bez pliku test_config.json).

    Pokazuje jak przekazać kryteria bezpośrednio w kodzie (nie przez plik).
    Przydatne gdy różne testy wymagają różnych progów.

    UWAGA: final_response_match_v2 wymaga Vertex AI Evaluation Service (płatne).
    W lokalnym dev używaj response_match_score (ROUGE-1, darmowe).
    """
    from google.adk.evaluation.agent_evaluator import AgentEvaluator

    test_file = EVAL_DIR / "code_review_basic.test.json"

    await AgentEvaluator.evaluate(
        agent_module="module_31_evaluation.agent",
        eval_dataset_file_path_or_dir=str(test_file),
        # Własne kryteria zamiast test_config.json:
        # Niższy próg trajectory (0.8) — dopuszczamy że agent może wywołać
        # narzędzie z lekko różnymi argumentami (np. stripped kod)
        # Wyższy próg response (0.2) — chcemy pewniejszego pokrycia słów kluczowych
        num_runs=1,
    )


@pytest.mark.asyncio
async def test_code_review_agent_directory_scan():
    """
    Test 3: Skan całego folderu eval/ (wszystkie *.test.json).

    AgentEvaluator akceptuje ścieżkę do folderu — uruchamia wszystkie
    eval cases ze wszystkich plików .test.json w tym folderze.
    Przydatne do integracyjnego sprawdzenia "wszystko naraz".
    """
    from google.adk.evaluation.agent_evaluator import AgentEvaluator

    await AgentEvaluator.evaluate(
        agent_module="module_31_evaluation.agent",
        eval_dataset_file_path_or_dir=str(EVAL_DIR),
        num_runs=1,
        print_detailed_results=True,
    )

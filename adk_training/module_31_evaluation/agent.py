"""
Module 31 — ADK Evaluation: Agent przeznaczony do ewaluacji
============================================================

WAŻNA ZASADA (zweryfikowana w Module 22, 17.04.2026):
  AgentEvaluator wymaga, żeby root_agent był JEDNYM LlmAgent (nie SequentialAgent).
  SequentialAgent emituje N eventów isFinalResponse=True (jeden per sub-agent
  z output_key) → ValueError: "Inferences should match conversations".

  Dlatego TEN moduł eksponuje pojedynczego LlmAgent skupionego na ONE task —
  co jest też dobrą praktyką (ewaluuj jeden stage na raz, resztę pokryj e2e).

AGENT: code_review_agent
  Przyjmuje snippet kodu, identyfikuje issues i zwraca JSON z findings.
  Idealny do ewaluacji bo:
    - Ma deterministyczne narzędzie (count_code_lines)
    - Zwraca strukturalny JSON → łatwa ocena ROUGE-1 i trajectory
    - Jedno wywołanie = jedno narzędzie = prosta trajectoria do walidacji

UŻYCIE Z AgentEvaluator:
  await AgentEvaluator.evaluate(
      agent_module="adk_training.module_31_evaluation.agent",
      eval_dataset_file_path_or_dir="adk_training/module_31_evaluation/tests/eval/",
      num_runs=1,
  )
"""
from __future__ import annotations

import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

load_dotenv()
MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")


# =============================================================================
# NARZĘDZIE — deterministyczne (nie LLM), łatwe do walidacji trajektorii
# =============================================================================

def count_code_lines(code_snippet: str) -> dict:
    """
    Analizuje snippet kodu i zwraca statystyki.
    Narzędzie deterministyczne → idealne do trajectory evaluation.

    Args:
        code_snippet: Kod źródłowy do analizy

    Returns:
        dict z: total_lines, code_lines, comment_lines, blank_lines, has_todos
    """
    lines = code_snippet.splitlines()
    blank = sum(1 for l in lines if not l.strip())
    comments = sum(1 for l in lines if l.strip().startswith(("#", "//", "/*", "*")))
    todos = sum(1 for l in lines if "TODO" in l or "FIXME" in l or "HACK" in l)
    code = len(lines) - blank - comments

    return {
        "total_lines": len(lines),
        "code_lines": code,
        "comment_lines": comments,
        "blank_lines": blank,
        "has_todos": todos > 0,
        "todo_count": todos,
    }


# =============================================================================
# ROOT AGENT — pojedynczy LlmAgent (wymóg AgentEvaluator)
# =============================================================================

root_agent = LlmAgent(
    name="code_review_agent",
    model=MODEL,
    description=(
        "Recenzent kodu. Przyjmuje snippet, wywołuje count_code_lines() "
        "i zwraca JSON z oceną jakości. Zoptymalizowany pod ewaluację ADK."
    ),
    instruction="""Jesteś recenzentem kodu. Twoje zadanie:

1. ZAWSZE wywołaj narzędzie count_code_lines() na dostarczonym kodzie.
2. Na podstawie wyników oceń jakość kodu.
3. Zwróć TYLKO JSON (bez markdown, bez komentarza):

{
  "quality_score": <0-10>,
  "issues": [
    {"type": "naming|complexity|documentation|style", "description": "...", "severity": "high|medium|low"}
  ],
  "has_todos": <true|false>,
  "line_stats": {
    "total": <int>,
    "code": <int>,
    "comments": <int>
  },
  "recommendation": "approve|request_changes|major_changes_required"
}

Zasady oceny:
- quality_score >= 8: dobry kod, mała liczba issues
- quality_score 5-7: przeciętny, kilka issues
- quality_score < 5: poważne problemy, refaktoryzacja wymagana
- has_todos = true → zawsze dodaj issue o type="documentation"
- Brak komentarzy przy złożonym kodzie → issue documentation
""",
    tools=[FunctionTool(func=count_code_lines)],
)

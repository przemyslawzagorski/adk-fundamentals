"""
Module 25 — ADK v2: Workflows (Deterministic Pipelines)
========================================================

PRAWDZIWE ADK v2 API (od 2026):
  Zapomnij o SequentialAgent / LoopAgent / ParallelAgent.
  Wszystko zastępuje jeden prymityw: Workflow(edges=[...])

  SEKWENCJA — tuple w edges:
    edges=[("START", node_a, node_b, node_c)]
    └─ node_a → node_b → node_c (gwarantowana kolejność)

  PĘTLA — route wskazujący na wcześniejszy węzeł:
    edges=[
        ("START", draft, evaluate, check_route),
        (check_route, {"retry": draft, "done": finalize}),  # ← pętla!
    ]

  WĘZŁY GRAFU — może być:
    - Agent(...)         → LLM agent z output_key i template {key}
    - def fn(input):     → zwykła funkcja Pythona yield Event(state={...})
    - async def fn():    → async funkcja
    - @node klasa        → dla dynamic/rerun nodes (Module 30)

  PRZEKAZYWANIE DANYCH:
    - Agent(output_key="k") → wynik trafia do stanu jako state["k"]
    - {k} w instruction     → odczyt ze stanu (template substitution)
    - {k?} → opcjonalne (nie błęduje gdy brak)
    - yield Event(state={"key": "value"}) → w funkcji-węźle

PRZYKŁAD PRODUKCYJNY (Module 23 — AI Code Concierge):
  PR Review pipeline: recon → review → report
  + Quality Loop: draft → check → (retry → draft) | (ok → done)

TODO dla dewelopera:
  [ ] Podmień Mock tools na prawdziwe wywołania Auggie (module_23/tools.py)
  [ ] Dodaj output_schema=PydanticModel do Agent zamiast "zwróć JSON w tekście"
  [ ] Przetestuj pipeline wklejając diff PR do adk web
  [ ] Zmień quality loop max na 5 iteracji i obserwuj kiedy się kończy
  [ ] Porównaj liczbę tokenów: stary LlmAgent dispatcher vs. Workflow pipeline
"""

from __future__ import annotations

import os
from typing import Literal

from dotenv import load_dotenv
from google.adk import Agent, Event, Workflow
from pydantic import BaseModel, Field

load_dotenv()
MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")


# =============================================================================
# WORKFLOW A: SEKWENCJA — PR Code Review Pipeline
# =============================================================================
# Architektura: START → init → recon → reviewer → reporter
# Każdy węzeł-funkcja inicjuje state; każdy Agent czyta/pisze przez output_key.

def init_pr_context(node_input: str):
    """Węzeł-funkcja: ustawia wejściowy opis PR w stanie sesji."""
    yield Event(state={"pr_description": node_input})


recon_agent = Agent(
    name="pr_recon",
    model=MODEL,
    instruction="""Analizujesz pull request na podstawie opisu: "{pr_description}"

Wyciągnij:
- Liczbę zmienionych plików (jeśli wspomniana)
- Obszary ryzyka: security, performance, breaking changes
- Szacowany wpływ: LOW / MEDIUM / HIGH

Odpowiedź w 5-7 zdaniach. Zakończ linią: RISK_LEVEL: [LOW|MEDIUM|HIGH]""",
    output_key="recon_report",  # → state["recon_report"]
)

reviewer_agent = Agent(
    name="pr_reviewer",
    model=MODEL,
    instruction="""Jesteś senior code reviewerem.

OPIS PR: "{pr_description}"
RAPORT REKON: "{recon_report}"

Na podstawie powyższego:
1. Wskaż 3 najważniejsze issues (critical/major/minor)
2. Zaproponuj konkretne poprawki
3. Decyzja: APPROVE / REQUEST_CHANGES / NEEDS_DISCUSSION""",
    output_key="review_result",
)

reporter_agent = Agent(
    name="pr_reporter",
    model=MODEL,
    instruction="""Tworzysz finalny raport PR.

REKON: "{recon_report}"
REVIEW: "{review_result}"

## PR Review Summary
**Decision**: [APPROVE | BLOCK | DISCUSS]
**Risk**: [LOW | MEDIUM | HIGH]
**Critical Issues**: (lista lub "none")
**Next Steps**: (konkretne akcje)""",
)

# edges-tuple = sekwencja deterministyczna (lewa → prawa)
pr_review_pipeline = Workflow(
    name="pr_review_pipeline",
    edges=[("START", init_pr_context, recon_agent, reviewer_agent, reporter_agent)],
)


# =============================================================================
# WORKFLOW B: PĘTLA — Quality Loop przez route wskazujący wstecz
# =============================================================================
# Architektura grafu (pętla):
#   START → init → draft → evaluate → check_route
#                   ↑            ↓ route="retry"
#                   └────────────┘
#                                ↓ route="done"
#                              finalize

class QualityGrade(BaseModel):
    grade: Literal["ok", "retry"] = Field(
        description="'ok' jeśli kod spełnia kryteria, 'retry' jeśli wymaga poprawek."
    )
    feedback: str = Field(
        description="Jeśli retry: konkretne wskazówki. Jeśli ok: pusty string."
    )


def init_quality_context(node_input: str):
    """Inicjuje stan dla pętli quality loop."""
    yield Event(state={"code_to_review": node_input, "feedback": ""})


quality_draft = Agent(
    name="quality_draft",
    model=MODEL,
    instruction="""Jesteś code reviewerem. Przejrzyj kod:
"{code_to_review}"

Jeśli są uwagi od poprzedniej iteracji: "{feedback?}"
Uwzględnij feedback w swojej ocenie.

Napisz zwięzły raport z issues (max 5 punktów) lub "Kod spełnia kryteria jakości." """,
    output_key="quality_draft",
)

quality_evaluator = Agent(
    name="quality_evaluator",
    model=MODEL,
    instruction="""Oceń raport reviewera: "{quality_draft}"

Czy raport jest kompletny i kod spełnia podstawowe kryteria:
- brak oczywistych bugów, poprawna obsługa błędów, czytelne nazwy?

Odpowiedz TYLKO schematem JSON (grade + feedback).""",
    output_schema=QualityGrade,
    output_key="quality_check",
)


def route_quality(node_input: QualityGrade):
    """Router: kontynuuje pętlę (retry) lub wychodzi (done)."""
    yield Event(route=node_input.grade, state={"feedback": node_input.feedback})


def quality_done():
    """Węzeł końcowy — potwierdza zakończenie pętli."""
    yield Event(message="✅ Quality loop zakończony — kod spełnia kryteria.")


quality_loop = Workflow(
    name="quality_loop",
    edges=[
        ("START", init_quality_context, quality_draft, quality_evaluator, route_quality),
        (route_quality, {"retry": quality_draft, "done": quality_done}),
        # ↑ "retry" cofa do quality_draft → to jest PĘTLA w ADK v2
    ],
)


# =============================================================================
# ROOT AGENT — eksponowany przez adk web (używamy prostszego PR pipeline)
# =============================================================================

root_agent = Workflow(
    name="root_agent",
    edges=[("START", init_pr_context, recon_agent, reviewer_agent, reporter_agent)],
)

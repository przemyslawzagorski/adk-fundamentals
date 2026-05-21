"""
Module 23 — AI Code Concierge (ADK v2)
========================================

MODERNIZACJA ADK v2: dispatcher → Workflow + @node dynamic orchestrator.

PRZED (ADK1):
  Single LlmAgent z 9 tools ZAWSZE w kontekście → długi prompt, wyższy koszt.
  LLM decyduje który tool wywołać → niedeterministyczne, trudne do testowania.

PO (ADK v2):
  Workflow(edges=[START → intake → @node dispatch → aggregator])

  1. intake_agent       — rozumie intencję, tworzy IntakeRequest (structured)
  2. @node dispatch     — TYLKO potrzebne węzły przez ctx.run_node()
     ├── code_review_node     (jeśli diff/PR w request)
     ├── codebase_node        (jeśli analiza repo)
     ├── implementation_node  (jeśli generacja kodu)
     ├── refactor_node        (jeśli refactor)
     ├── security_node        (jeśli security audit)
     ├── specialist_node      (jeśli generic pytanie)
     └── diagnostics_node     (jeśli zdrowie/koszt systemu)
  3. aggregator          — składa wyniki w czytelną odpowiedź

KLUCZOWA KORZYŚĆ:
  Każdy węzeł ma TYLKO jeden tool w kontekście → krótszy prompt → niższy koszt.
  Tylko potrzebne węzły są uruchamiane → dynamizm bez BaseAgent boilerplate.

ZACHOWANO:
  tools.py, auggie_factory.py — bez zmian (kompatybilna warstwa Auggie SDK).

TODO dla dewelopera:
  [ ] Zmierz koszt tokenów: stary dispatch (9 tools) vs. nowy (1 tool per węzeł)
  [ ] Dodaj output_schema=PydanticModel do każdego węzła zamiast JSON w stringu
  [ ] Ustaw AUGGIE_SDK_KEY w .env i przetestuj na prawdziwym diff
  [ ] Dodaj parallel execution: asyncio.gather(code_review, security) gdy oba potrzebne
  [ ] Zintegruj z Module 32 (A2A): wystaw każdy węzeł jako RemoteA2aAgent
"""

from __future__ import annotations

import logging
import os
import pathlib
import sys
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Załaduj .env — z modułu i z katalogu nadrzędnego (fallback)
_HERE = pathlib.Path(__file__).parent
load_dotenv(_HERE / ".env")
load_dotenv(_HERE.parent / ".env", override=False)

# Dodaj katalog modułu do sys.path → umożliwia `from tools import ...`
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

from google.adk import Agent, Context, Event, Workflow  # noqa: E402
from google.adk.workflow import node                    # noqa: E402

from tools import (  # noqa: E402  (po load_dotenv i sys.path)
    analyze_codebase,
    ask_specialist,
    auggie_cost_report,
    auggie_health,
    auggie_telemetry,
    code_review_pr,
    generate_implementation,
    refactor_workflow,
    security_audit,
)

MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")


# =============================================================================
# PYDANTIC SCHEMA — wynik intake (IntakeRequest)
# =============================================================================

class IntakeRequest(BaseModel):
    """Ustrukturyzowana interpretacja żądania użytkownika."""
    intent: Literal[
        "code_review", "codebase_analysis", "implementation",
        "refactor", "security_audit", "specialist_question", "diagnostics", "other"
    ] = Field(description="Główna intencja żądania.")
    has_diff: bool = Field(False, description="Czy wiadomość zawiera diff/patch kodu?")
    needs_security: bool = Field(False, description="Czy wymagana analiza bezpieczeństwa?")
    needs_implementation: bool = Field(False, description="Czy wymagana generacja kodu?")
    needs_refactor: bool = Field(False, description="Czy wymagany refactoring?")
    needs_diagnostics: bool = Field(False, description="Czy wymagana diagnostyka (health/cost/telemetry)?")
    summary: str = Field(description="Streszczenie żądania (1-2 zdania).")
    raw_input: str = Field(description="Oryginalne żądanie użytkownika.")


# =============================================================================
# NODE 1: INTAKE — rozumie intencję użytkownika
# =============================================================================

def init_concierge(node_input: str):
    """Inicjuje state z surowym żądaniem użytkownika."""
    yield Event(state={"user_request": node_input})


intake_agent = Agent(
    name="intake_agent",
    model=MODEL,
    instruction="""Analizujesz żądanie użytkownika i klasyfikujesz je.

Żądanie: "{user_request}"

Wygeneruj IntakeRequest zgodnie ze schematem:
- intent: główna intencja (code_review | codebase_analysis | implementation | refactor | security_audit | specialist_question | diagnostics | other)
- has_diff: True jeśli wiadomość zawiera diff, patch, "git diff" lub zmiany kodu
- needs_security: True dla słów: security, podatność, CVE, hack, OWASP, audit, sekrety
- needs_implementation: True dla: napisz, wygeneruj, implementuj, utwórz funkcję/klasę
- needs_refactor: True dla: zrefaktoruj, przepisz, popraw strukturę, clean up
- needs_diagnostics: True dla: health, koszt, cost, telemetry, status, ile kosztuje
- summary: 1-2 zdania opisujące co użytkownik chce osiągnąć
- raw_input: dokładna kopia żądania użytkownika""",
    output_schema=IntakeRequest,
    output_key="intake",
)


# =============================================================================
# WYSPECJALIZOWANE WĘZŁY — każdy ma JEDEN tool
# =============================================================================

code_review_node = Agent(
    name="code_review_node",
    model=MODEL,
    instruction="""Wykonujesz code review diffa.

Żądanie: "{user_request}"

Wyciągnij diff z wiadomości i wywołaj code_review_pr().
Jeśli nie ma diffu, poproś użytkownika o jego wklejenie.""",
    tools=[code_review_pr],
    output_key="code_review_result",
)

codebase_node = Agent(
    name="codebase_analysis_node",
    model=MODEL,
    instruction="""Analizujesz strukturę codebase.

Żądanie: "{user_request}"

Wywołaj analyze_codebase() z odpowiednimi parametrami.
Skoncentruj się na katalogach/plikach wymienionych w żądaniu.""",
    tools=[analyze_codebase],
    output_key="codebase_result",
)

implementation_node = Agent(
    name="implementation_node",
    model=MODEL,
    instruction="""Generujesz implementację kodu według specyfikacji.

Żądanie: "{user_request}"

Wywołaj generate_implementation() z:
- spec: szczegółowy opis co ma robić kod
- language: język programowania (python domyślnie)
- must_have_csv: kryteria oddzielone średnikiem""",
    tools=[generate_implementation],
    output_key="implementation_result",
)

refactor_node = Agent(
    name="refactor_node",
    model=MODEL,
    instruction="""Refaktoryzujesz istniejący kod.

Żądanie: "{user_request}"

Wywołaj refactor_workflow() z:
- target_file: ścieżka do pliku do refaktoryzacji
- refactor_goal: cel refaktoryzacji (co poprawić)""",
    tools=[refactor_workflow],
    output_key="refactor_result",
)

security_node = Agent(
    name="security_node",
    model=MODEL,
    instruction="""Wykonujesz audit bezpieczeństwa.

Żądanie: "{user_request}"

Wywołaj security_audit() z target = ścieżka do katalogu lub pliku.
Szukaj: hardcoded secrets, podatności zależności, misconfigurations.""",
    tools=[security_audit],
    output_key="security_result",
)

specialist_node = Agent(
    name="specialist_node",
    model=MODEL,
    instruction="""Odpowiadasz na pytanie eksperckie przez Auggie (Claude Sonnet 4.5).

Pytanie: "{user_request}"

Wywołaj ask_specialist() z pełnym pytaniem.
Auggie ma dostęp do workspace i może analizować kod.""",
    tools=[ask_specialist],
    output_key="specialist_result",
)

diagnostics_node = Agent(
    name="diagnostics_node",
    model=MODEL,
    instruction="""Pobierasz diagnostykę systemu Auggie.

Żądanie: "{user_request}"

Dostępne narzędzia:
- auggie_health() — status SDK, auth, workspace
- auggie_cost_report() — koszty USD per tool/model
- auggie_telemetry() — statystyki wywołań

Wywołaj odpowiednie narzędzia na podstawie żądania.""",
    tools=[auggie_health, auggie_cost_report, auggie_telemetry],
    output_key="diagnostics_result",
)


# =============================================================================
# NODE 2: DYNAMIC DISPATCH — @node uruchamiający tylko potrzebne węzły
# =============================================================================

@node(rerun_on_resume=True)
async def dynamic_dispatch(ctx: Context, node_input: IntakeRequest) -> str:
    """
    Dynamiczny orchestrator: uruchamia TYLKO węzły potrzebne dla danego żądania.

    Wzorzec ADK v2:
    - ctx.run_node(agent) → uruchamia węzeł z aktualnym kontekstem sesji
    - yield Event(state={...}) → aktualizuje state między węzłami
    - IntakeRequest (output_schema z intake_agent) → deterministyczny routing

    KLUCZOWY ZYSK vs. ADK1 dispatcher:
    ADK1: 9 tools zawsze w kontekście → LLM może wybrać zły tool
    ADK2: deterministic routing → tylko 1 tool w kontekście → niższy koszt, pełna kontrola
    """
    intake = node_input
    results: dict[str, str] = {}

    # Routing na podstawie IntakeRequest (deterministyczny, bez LLM!)
    if intake.has_diff or intake.intent == "code_review":
        result = await ctx.run_node(code_review_node)
        results["code_review"] = result

    if intake.intent == "codebase_analysis":
        result = await ctx.run_node(codebase_node)
        results["codebase"] = result

    if intake.needs_implementation or intake.intent == "implementation":
        result = await ctx.run_node(implementation_node)
        results["implementation"] = result

    if intake.needs_refactor or intake.intent == "refactor":
        result = await ctx.run_node(refactor_node)
        results["refactor"] = result

    if intake.needs_security or intake.intent == "security_audit":
        result = await ctx.run_node(security_node)
        results["security"] = result

    if intake.needs_diagnostics or intake.intent == "diagnostics":
        result = await ctx.run_node(diagnostics_node)
        results["diagnostics"] = result

    # Fallback: generic specialist question
    if not results or intake.intent in ("specialist_question", "other"):
        result = await ctx.run_node(specialist_node)
        results["specialist"] = result

    # Zapisz wszystkie wyniki w state dla aggregatora
    yield Event(state={
        "dispatch_results": str(results),
        "active_nodes": list(results.keys()),
        "intake_summary": intake.summary,
    })

    # Zwróć skrót dla następnego węzła
    yield f"Completed: {list(results.keys())}"


# =============================================================================
# NODE 3: AGGREGATOR — łączy wyniki w czytelną odpowiedź
# =============================================================================

concierge_aggregator = Agent(
    name="concierge_aggregator",
    model=MODEL,
    instruction="""Jesteś AI Code Concierge. Składasz wyniki specjalistów w czytelną odpowiedź.

ŻĄDANIE: "{user_request}"
STRESZCZENIE INTAKE: "{intake_summary}"
AKTYWNE WĘZŁY: "{active_nodes}"
WYNIKI: "{dispatch_results}"

Zasady:
- Streść wyniki PO POLSKU, w sposób przyjazny dla developera
- Zacznij od najważniejszego (severity-first)
- Wyróżnij konkretne akcje do podjęcia
- NIE kopiuj surowego JSON — przetłumacz na język ludzki
- Jeśli jest pole "error" → wyjaśnij problem i zaproponuj alternatywę
- Na końcu: zaproponuj kolejny krok jeśli to uzasadnione""",
)


# =============================================================================
# ROOT AGENT — Workflow: intake → dispatch → aggregate
# =============================================================================

root_agent = Workflow(
    name="root_agent",
    edges=[
        (
            "START",
            init_concierge,       # fn: ustawia state["user_request"]
            intake_agent,         # Agent: IntakeRequest → state["intake"]
            dynamic_dispatch,     # @node: routing deterministyczny → ctx.run_node()
            concierge_aggregator, # Agent: ludzka odpowiedź po polsku
        ),
    ],
)

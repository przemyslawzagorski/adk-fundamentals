"""
Module 30 — ADK v2: Dynamic Graphs (@node + ctx.run_node + while loop)
=======================================================================

PRAWDZIWE ADK v2 API — Dynamic Graphs przez @node:
  Nie ma już BaseAgent z _run_async_impl dla dynamic graphs.
  Dynamizm = @node(rerun_on_resume=True) + ctx.run_node() w pętli while.

  WZORZEC z official dynamic_nodes sample:
    from google.adk import Context, Event, Workflow
    from google.adk.workflow import node

    @node(rerun_on_resume=True)
    async def orchestrate(ctx: Context, node_input: str) -> str:
        yield Event(state={"topic": node_input})

        while True:
            result = await ctx.run_node(some_agent)
            check = await ctx.run_node(evaluator, node_input=result)
            if check.grade == "done":
                yield result   # ← final output
                break

  KLUCZOWE KONCEPTY:
  1. @node(rerun_on_resume=True):
     - Węzeł może emitować Event(state={...}) i kontynuować logikę
     - "rerun_on_resume" = wywoływany ponownie gdy sesja jest wznawiana
     - Umożliwia długotrwałe procesy z wieloma round-tripami

  2. ctx.run_node(agent, node_input=...):
     - Uruchamia węzeł grafu z aktualnym kontekstem
     - Zwraca wynik agenta (string lub pydantic model jeśli output_schema)
     - Może być wywołany w pętli while lub asyncio.gather

  3. yield result / yield Event(message="..."):
     - Finalne wyjście z @node
     - Bez parametru → tekst staje się odpowiedzią agenta

  PORÓWNANIE Z V1:
    v1: BaseAgent._run_async_impl → async generator, boilerplate
    v2: @node → dekorator, czytelny, testowalny, mniej kodu

PRZYKŁAD PRODUKCYJNY (Module 23 + 24 — Adaptive Audit):
  Profiler → @node orchestrator buduje graf w runtime → aggregator
  Mały projekt: [quality]. Krytyczny: [quality, security, performance, deps].

TODO dla dewelopera:
  [ ] Zmień MAX_ITERATIONS i obserwuj kiedy pętla się kończy
  [ ] Dodaj ctx.run_node(quality_agent) + ctx.run_node(security_agent) w asyncio.gather
  [ ] Zintegruj auggie_run z Module 23 jako tool w quality_agent
  [ ] Zmierz koszt tokenów: static 4 nodes vs. dynamic 1-4 nodes
  [ ] Dodaj logging: print(f"Running iteration {i}, result: {result[:50]}")
  [ ] Przetestuj edge case: co gdy profiler zwróci "size=large, risk=critical"?
"""

from __future__ import annotations

import os
from typing import Literal

from dotenv import load_dotenv
from google.adk import Agent, Context, Event, Workflow
from google.adk.workflow import node
from pydantic import BaseModel, Field

load_dotenv()
MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")

MAX_ITERATIONS = 3  # Maksymalna liczba iteracji dynamicznej pętli


# =============================================================================
# PYDANTIC SCHEMAS — strukturalne wyjścia dla deterministycznego sterowania
# =============================================================================

class ProjectProfile(BaseModel):
    """Profil projektu — wynik project_profiler, wejście do orchestratora."""
    name: str = Field(description="Nazwa projektu.")
    size: Literal["small", "medium", "large"] = Field(description="Rozmiar projektu.")
    risk_level: Literal["low", "medium", "high", "critical"] = Field(
        description="Poziom ryzyka."
    )
    tech_stack: list[str] = Field(description="Technologie użyte w projekcie.")


class AnalysisGrade(BaseModel):
    """Wynik ewaluatora — decyduje czy analiza jest kompletna."""
    grade: Literal["complete", "needs_more"] = Field(
        description="'complete' gdy analiza jest wyczerpująca, 'needs_more' gdy brak obszarów."
    )
    missing_areas: list[str] = Field(
        description="Lista brakujących obszarów analizy (pusta gdy complete)."
    )
    feedback: str = Field(description="Wskazówki do uzupełnienia analizy.")


# =============================================================================
# WĘZŁY — agenty używane przez dynamiczny orkiestrator
# =============================================================================

quality_agent = Agent(
    name="quality_analyzer",
    model=MODEL,
    instruction="""Analizujesz jakość kodu projektu.

Profil: "{project_profile}"
Poprzednie wyniki: "{accumulated_results?}"

Sprawdź: code smells, complexity, SOLID violations, tech debt.
JSON: {{"focus": "quality", "findings": [...], "score": 0-100, "tech_debt": "low|medium|high"}}""",
)

security_agent = Agent(
    name="security_analyzer",
    model=MODEL,
    instruction="""Analizujesz bezpieczeństwo projektu.

Profil: "{project_profile}"
Poprzednie wyniki: "{accumulated_results?}"

Sprawdź: OWASP Top 10, hardcoded secrets, insecure deps, misconfigurations.
JSON: {{"focus": "security", "findings": [...], "grade": "A-F", "critical_count": 0}}""",
)

performance_agent = Agent(
    name="performance_analyzer",
    model=MODEL,
    instruction="""Analizujesz wydajność projektu.

Profil: "{project_profile}"
Poprzednie wyniki: "{accumulated_results?}"

Sprawdź: N+1 queries, blocking calls, cache misses, large payloads.
JSON: {{"focus": "performance", "bottlenecks": [...], "impact": "high|medium|low"}}""",
)

dependency_agent = Agent(
    name="dependency_analyzer",
    model=MODEL,
    instruction="""Analizujesz zależności projektu.

Profil: "{project_profile}"
Poprzednie wyniki: "{accumulated_results?}"

Sprawdź: CVE, licencje, outdated packages (>2 major versions).
JSON: {{"focus": "dependencies", "risky_packages": [...], "license_issues": [...], "update_priority": "high|medium|low"}}""",
)

completeness_evaluator = Agent(
    name="completeness_evaluator",
    model=MODEL,
    instruction="""Oceniasz kompletność analizy projektu.

Profil projektu: "{project_profile}"
Zebrane wyniki: "{accumulated_results}"

Czy analiza pokrywa wszystkie obszary adekwatne do ryzyka?
- small+low: wystarczy "quality"
- medium+medium: wymagane "quality" + "security"
- large/high/critical: wymagane wszystkie 4 obszary

Odpowiedz zgodnie ze schematem (grade + missing_areas + feedback).""",
    output_schema=AnalysisGrade,
)


# =============================================================================
# PROFILER — stały węzeł, określa profil projektu
# =============================================================================

project_profiler = Agent(
    name="project_profiler",
    model=MODEL,
    instruction="""Profilujesz projekt aby dobrać strategię analizy.

Opis projektu: "{project_description}"

Wygeneruj profil zgodny ze schematem JSON:
- name: nazwa projektu
- size: small (<10k LOC) | medium (10-100k) | large (>100k)
- risk_level: low | medium | high | critical
- tech_stack: lista technologii

Kryteria ryzyka HIGH/CRITICAL: finanse, medycyna, dane osobowe, produkcja, payment.""",
    output_schema=ProjectProfile,
    output_key="project_profile",
)


# =============================================================================
# DYNAMIC ORCHESTRATOR — @node z pętlą while i ctx.run_node
# =============================================================================

# Mapowanie: które agenty uruchamiać dla jakich kombinacji size+risk
_AGENT_MATRIX: dict[str, list] = {
    "small:low":      [quality_agent],
    "small:medium":   [quality_agent, security_agent],
    "medium:low":     [quality_agent, security_agent],
    "medium:medium":  [quality_agent, security_agent, dependency_agent],
    "medium:high":    [quality_agent, security_agent, performance_agent, dependency_agent],
    "large:low":      [quality_agent, security_agent, dependency_agent],
    "large:medium":   [quality_agent, security_agent, performance_agent, dependency_agent],
    "large:high":     [quality_agent, security_agent, performance_agent, dependency_agent],
    "large:critical": [quality_agent, security_agent, performance_agent, dependency_agent],
}


@node(rerun_on_resume=True)
async def dynamic_orchestrate(ctx: Context, node_input: ProjectProfile) -> str:
    """
    Dynamiczny orkiestrator: dobiera węzły w runtime na podstawie ProjectProfile.

    @node(rerun_on_resume=True):
    - Węzeł uruchamiany ponownie po każdym yield Event(...)
    - Umożliwia multi-turn logikę (loop, HITL, conditional execution)

    ctx.run_node(agent):
    - Uruchamia agent w kontekście aktualnej sesji
    - Zwraca wynik jako string (lub pydantic model jeśli output_schema)
    - Automatycznie aktualizuje session.state
    """
    profile = node_input

    # Dobierz zestaw węzłów na podstawie profilu
    key = f"{profile.size}:{profile.risk_level}"
    agents_to_run = _AGENT_MATRIX.get(
        key, _AGENT_MATRIX.get(f"large:{profile.risk_level}", [quality_agent])
    )

    # Zapisz info o dynamicznie dobranym grafie
    yield Event(state={
        "project_profile": profile.model_dump_json(),
        "dynamic_nodes": [a.name for a in agents_to_run],
        "accumulated_results": "",
    })

    # PĘTLA: uruchamiaj kolejne analizatory dopóki ewaluator nie powie "complete"
    accumulated = ""
    for i, agent in enumerate(agents_to_run):
        # Dynamiczne wywołanie węzła — serce wzorca dynamic graphs
        result = await ctx.run_node(agent)
        accumulated += f"\n\n--- {agent.name} ---\n{result}"

        # Aktualizuj state po każdym węźle
        yield Event(state={"accumulated_results": accumulated})

        # Po co najmniej 2 węzłach sprawdzaj kompletność
        if i >= 1:
            grade = AnalysisGrade.model_validate_json(
                await ctx.run_node(completeness_evaluator)
            ) if hasattr(AnalysisGrade, "model_validate_json") else None

            if grade and grade.grade == "complete":
                break  # ← Wyjście z pętli gdy analiza jest kompletna

    # Finalne wyjście z @node — staje się inputem do następnego węzła
    yield accumulated


# =============================================================================
# AGREGATOR — finalny raport ze wszystkich wyników
# =============================================================================

dynamic_aggregator = Agent(
    name="dynamic_aggregator",
    model=MODEL,
    instruction="""Generujesz finalny raport z dynamicznej analizy.

Profil projektu: "{project_profile}"
Uruchomione węzły: "{dynamic_nodes}"
Zebrane wyniki: "{accumulated_results}"

## Dynamic Graph Analysis Report

**Project**: (z profilu)
**Graph Size**: (ile węzłów uruchomiono)
**Risk Level**: (z profilu)

### Executive Summary
(najważniejsze ustalenia)

### Priority Actions
(top 5 działań po severity)

### Graph Efficiency
(dlaczego właśnie te węzły zostały uruchomione — uzasadnienie)""",
)


# =============================================================================
# ROOT AGENT
# =============================================================================
# Graf: START → init_fn → project_profiler → dynamic_orchestrate → aggregator
#
# dynamic_orchestrate:
#   - Przyjmuje ProfileProject (output_schema z project_profiler)
#   - Dynamicznie dobiera węzły (1-4) na podstawie size+risk
#   - Uruchamia je przez ctx.run_node() w pętli
#   - Emituje Event(state={accumulated_results}) po każdym węźle

def init_audit(node_input: str):
    """Inicjuje state z opisem projektu."""
    yield Event(state={"project_description": node_input})


root_agent = Workflow(
    name="root_agent",
    edges=[
        (
            "START",
            init_audit,              # funkcja → ustawia state["project_description"]
            project_profiler,        # Agent → ProjectProfile w output_key
            dynamic_orchestrate,     # @node → dynamic loop z ctx.run_node
            dynamic_aggregator,      # Agent → finalny raport
        ),
    ],
)

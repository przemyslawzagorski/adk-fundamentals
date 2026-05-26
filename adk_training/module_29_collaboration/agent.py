"""
Module 29 — ADK v2: Collaborative Agents (Równoległa Praca Specjalistów)
=========================================================================

PRAWDZIWE ADK v2 API — Parallel Collaboration przez @node + asyncio.gather:
  Nie ma już ParallelAgent. Równoległość osiągamy przez:

  1. @node(rerun_on_resume=True) — dekorator dla węzła orkiestratora
  2. ctx.run_node(agent) — uruchamia węzeł z aktualnym kontekstem
  3. asyncio.gather(...) — uruchamia wiele ctx.run_node() RÓWNOLEGLE

  WZORZEC:
    from google.adk import Context, Event, Workflow
    from google.adk.workflow import node

    @node(rerun_on_resume=True)
    async def run_specialists(ctx: Context, node_input: str):
        yield Event(state={"project": node_input})

        # RÓWNOLEGŁA PRACA — uruchamia wszystkich specjalistów naraz
        results = await asyncio.gather(
            ctx.run_node(quality_agent),
            ctx.run_node(security_agent),
            ctx.run_node(dependency_agent),
        )
        quality_r, security_r, dependency_r = results
        yield Event(state={
            "quality_result": quality_r,
            "security_result": security_r,
        })

  PORÓWNANIE Z V1 ParallelAgent:
    v1: ParallelAgent(sub_agents=[a, b, c]) — black box, trudne do testowania
    v2: @node + asyncio.gather — explicite, observable, testowalne

  DLACZEGO @node(rerun_on_resume=True)?
    Gdy orkiestrator emituje Event (np. po zebraniu wyników), ADK może go wznowić.
    rerun_on_resume=True = węzeł jest wywoływany ponownie po każdym resume.
    Bez tego flagi, state po yield byłby utracony.

PRZYKŁAD PRODUKCYJNY (Module 23 + 24):
  Full Security Suite: kod → równolegle (quality + security + deps) → raport

TODO dla dewelopera:
  [ ] Zmierz czas: sequential vs. asyncio.gather (oczekiwany 2-3x speedup)
  [ ] Dodaj error handling: try/except w gather dla partial results
  [ ] Zintegruj auggie_run() z Module 23 jako tool quality_agent
  [ ] Zintegruj playwright_runner z Module 24 jako tool security_agent
  [ ] Wystaw specialist agents przez A2A (Module 32) → mikroserwisy
  [ ] Dodaj fallback: jeśli security_agent zawiedzie → użyj cached result
"""

from __future__ import annotations

import asyncio
import os

from dotenv import load_dotenv
from google.adk import Agent, Context, Event, Workflow
from google.adk.tools import FunctionTool
from google.adk.workflow import node

load_dotenv()
MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")


# =============================================================================
# SPECIALIST TOOLS — każdy specjalista ma własny zestaw narzędzi
# =============================================================================

def analyze_code_quality(code_path: str, focus: str = "all") -> dict:
    """
    Analiza jakości kodu. W produkcji: wywołuje Auggie SDK (Module 23 pattern).

    Args:
        code_path: Ścieżka do pliku/katalogu
        focus: Obszar: all|security|performance|style
    Returns:
        Raport jakości z issues i score
    """
    return {
        "path": code_path,
        "focus": focus,
        "issues": [],       # TODO: auggie_factory.auggie_run()
        "score": 85,
        "note": "Mock — zintegruj z Module 23 auggie_run()",
    }


def run_security_scan(target: str, depth: str = "basic") -> dict:
    """
    Skan bezpieczeństwa. W produkcji: Module 24 playwright_runner.

    Args:
        target: URL lub ścieżka docelowa
        depth: basic|full|owasp
    Returns:
        Findings z severity
    """
    return {
        "target": target,
        "depth": depth,
        "findings": [],     # TODO: Module 24 auto_pentest()
        "severity": "none",
        "note": "Mock — zintegruj z Module 24 playwright_runner",
    }


def fetch_dependency_info(package: str, ecosystem: str = "pypi") -> dict:
    """
    Sprawdza CVE i licencje pakietu. W produkcji: OSV API.

    Args:
        package: Nazwa pakietu
        ecosystem: pypi|npm|maven
    Returns:
        CVE, licencja, wersja
    """
    return {
        "package": package,
        "ecosystem": ecosystem,
        "vulnerabilities": [],  # TODO: https://osv.dev/
        "license": "Apache-2.0",
        "note": "Mock — zintegruj z OSV API",
    }


# =============================================================================
# SPECIALIST AGENTS — każdy z własnymi narzędziami
# =============================================================================

quality_agent = Agent(
    name="quality_specialist",
    model=MODEL,
    instruction="""Jesteś ekspertem jakości kodu.

Projekt: "{project}"

Wywołaj analyze_code_quality() i na podstawie wyników:
1. Zidentyfikuj top 5 issues (code smells, complexity, tech debt)
2. Oceń maintainability score (0-100)
3. Zaproponuj refaktoryzacje z priorytetem

JSON: {{"issues": [...], "maintainability_score": 85, "tech_debt": "low|medium|high"}}""",
    output_key="quality_report",
    tools=[FunctionTool(func=analyze_code_quality)],
)

security_agent = Agent(
    name="security_specialist",
    model=MODEL,
    instruction="""Jesteś ekspertem bezpieczeństwa (AppSec).

Projekt: "{project}"

Wywołaj run_security_scan() i na podstawie wyników:
1. Zidentyfikuj podatności OWASP Top 10
2. Oceń security grade (A-F)
3. Wskaż poprawki z timeline

JSON: {{"vulnerabilities": [...], "security_grade": "B", "escalate": false}}""",
    output_key="security_report",
    tools=[FunctionTool(func=run_security_scan)],
)

dependency_agent = Agent(
    name="dependency_specialist",
    model=MODEL,
    instruction="""Jesteś ekspertem supply chain security.

Projekt: "{project}"

Wywołaj fetch_dependency_info() dla głównych zależności i:
1. Zidentyfikuj pakiety z CVE lub złą licencją
2. Wskaż outdated packages (>2 major versions)
3. Zaproponuj strategię aktualizacji

JSON: {{"risky_packages": [...], "license_issues": [...], "update_priority": "high|medium|low"}}""",
    output_key="dependency_report",
    tools=[FunctionTool(func=fetch_dependency_info)],
)


# =============================================================================
# ORCHESTRATOR NODE — @node + asyncio.gather dla równoległości
# =============================================================================

@node(rerun_on_resume=True)
async def run_specialists_parallel(ctx: Context, node_input: str):
    """
    Orkiestrator uruchamiający specjalistów RÓWNOLEGLE przez asyncio.gather.

    @node(rerun_on_resume=True) = węzeł może być wznowiony po yield Event(...)
    ctx.run_node() = uruchamia węzeł grafu z aktualnym kontekstem sesji.

    KLUCZOWY WZORZEC v2:
    asyncio.gather() → równoległa praca → wyniki zebrane po zakończeniu wszystkich
    """
    # Inicjuj state z opisem projektu
    yield Event(state={"project": node_input})

    # RÓWNOLEGŁA PRACA — wszystkie 3 specjalizacje naraz
    quality_r, security_r, dependency_r = await asyncio.gather(
        ctx.run_node(quality_agent),
        ctx.run_node(security_agent),
        ctx.run_node(dependency_agent),
    )

    # Zbierz wyniki wszystkich specjalistów w state
    yield Event(state={
        "quality_result": quality_r,
        "security_result": security_r,
        "dependency_result": dependency_r,
        "specialists_done": True,
    })


# =============================================================================
# FINALIZATOR — agreguje wyniki równoległych specjalistów
# =============================================================================

aggregator = Agent(
    name="results_aggregator",
    model=MODEL,
    instruction="""Agregujujesz wyniki trzech specjalistów w Executive Summary.

QUALITY: "{quality_result}"
SECURITY: "{security_result}"
DEPENDENCIES: "{dependency_result}"

## Full Security & Quality Report

**Overall Risk**: CRITICAL | HIGH | MEDIUM | LOW
**Immediate Actions** (do 24h): (lista)
**Short-term** (do 1 tygodnia): (lista)
**Long-term** (do 1 miesiąca): (lista)

### Cross-cutting Concerns
(problemy wpływające na wiele obszarów jednocześnie)

### Compliance Status
(OWASP, licencje, code quality standards)""",
)


# =============================================================================
# ROOT AGENT — Workflow: parallel specialists → aggregator
# =============================================================================

root_agent = Workflow(
    name="root_agent",
    edges=[
        # run_specialists_parallel uruchamia quality/security/dependency RÓWNOLEGLE
        # i zapisuje wyniki w state, następnie aggregator generuje raport
        ("START", run_specialists_parallel, aggregator),
    ],
)

"""
Module 27 — ADK v2: Data Handling (Stan, Kontekst, Przekazywanie Danych)
=========================================================================

PRAWDZIWE ADK v2 API — Data Flow:
  W v2 dane przepływają między węzłami na TRZY SPOSOBY:

  1. FUNKCJA yielding Event(state={...}):
       def parse_input(node_input: str):
           yield Event(state={"code": node_input, "lang": "python"})
     → Dane natychmiast dostępne w następnym węźle przez {key}

  2. Agent z output_key:
       Agent(output_key="analysis_result", ...)
     → Po zakończeniu agenta, jego odpowiedź trafia do state["analysis_result"]

  3. Template substitution w instruction:
       instruction="Przeanalizuj: {code}. Kontekst: {analysis_result?}"
     → {key} = wymagane (błąd jeśli brak), {key?} = opcjonalne (puste jeśli brak)

  KLUCZOWA RÓŻNICA v2 vs. v1:
    v1: dane w stringach przekazywane przez output_key + template = kruche
    v2: funkcje-węzły mogą bezpośrednio modyfikować state → czystszy przepływ
        + output_schema=PydanticModel → strukturalny output bez parsowania JSON

  TOOLS W V2:
    Tool może być po prostu argumentem tools=[fn] (auto-wrap do FunctionTool)
    Tool context (read/write state) dostępny gdy tool przyjmuje ToolContext arg

PRZYKŁAD PRODUKCYJNY:
  Pipeline: parse_input → enrich_metadata → analyze → validate → report
  Każdy węzeł wzbogaca state o nowe klucze, następne węzły je odczytują.

TODO dla dewelopera:
  [ ] Sprawdź state w ADK Web UI po każdym kroku (State tab → live view)
  [ ] Dodaj output_schema do analyze_agent zamiast "odpowiedz JSON"
  [ ] Dodaj węzeł-funkcję validate_fn() zamiast validate_agent (czysto deterministyczny)
  [ ] Zintegruj ctx.save_artifact() dla raportu PDF (google.adk.artifacts)
  [ ] Przetestuj {missing_key?} — optional template vs. {required_key} — error gdy brak
  [ ] Porównaj z Module 23: tam dane wracają jako plain text bez structured state
"""

from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from google.adk import Agent, Event, Workflow
from google.adk.tools import FunctionTool

load_dotenv()
MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")


# =============================================================================
# NARZĘDZIA — deterministyczne, nie wymagają LLM
# =============================================================================

def enrich_code_metadata(code_snippet: str, language: str = "python") -> dict[str, Any]:
    """
    Wzbogaca kod o statyczne metadane (bez LLM).
    Deterministyczne → idealne do testowania.

    Args:
        code_snippet: Kod źródłowy
        language: Język programowania

    Returns:
        Metadane: line_count, imports, complexity, flags
    """
    lines = code_snippet.strip().split("\n")
    imports = [l.strip() for l in lines if l.startswith(("import ", "from "))]
    return {
        "language": language,
        "line_count": len(lines),
        "import_count": len(imports),
        "imports": imports,
        "has_functions": "def " in code_snippet,
        "has_classes": "class " in code_snippet,
        "has_async": "async " in code_snippet,
        "estimated_complexity": (
            "high" if len(lines) > 100 else "medium" if len(lines) > 30 else "low"
        ),
    }


def validate_report(report: str) -> dict[str, Any]:
    """
    Waliduje finalny raport pod kątem wymaganych sekcji.

    Args:
        report: Tekst raportu

    Returns:
        Wynik walidacji z listą brakujących sekcji
    """
    required = ["findings", "severity", "recommendations"]
    missing = [s for s in required if s.lower() not in report.lower()]
    return {
        "valid": len(missing) == 0,
        "missing_sections": missing,
        "confidence": max(0, 100 - len(missing) * 30),
    }


# =============================================================================
# WĘZEŁ 1 (FUNKCJA): Parsowanie wejścia → ustawia state
# =============================================================================

def parse_input(node_input: str):
    """
    Węzeł-funkcja: parsuje wejście i ustawia initial state.
    Wzorzec v2: funkcja > LlmAgent dla deterministycznych operacji.
    """
    # Prosta heurystyka do wykrywania języka
    lang = "python"
    if "function " in node_input or "const " in node_input:
        lang = "javascript"
    elif "public class" in node_input or "void main" in node_input:
        lang = "java"

    yield Event(state={
        "raw_code": node_input,
        "detected_language": lang,
        "analysis_goal": "security",  # domyślnie, można nadpisać
    })


# =============================================================================
# WĘZEŁ 2 (AGENT): Enrichment — używa narzędzia deterministycznego
# =============================================================================

enrichment_agent = Agent(
    name="code_enrichment",
    model=MODEL,
    instruction="""Wzbogacasz kontekst analizy kodu.

Kod do analizy: "{raw_code}"
Wykryty język: "{detected_language}"

Wywołaj enrich_code_metadata() na dostarczonym kodzie i zwróć wynik.
Jeśli kod jest pusty lub brak, zwróć: {{"enriched": false, "reason": "no code"}}

Wynik jako JSON.""",
    output_key="code_metadata",  # → state["code_metadata"]
    tools=[FunctionTool(func=enrich_code_metadata)],
)


# =============================================================================
# WĘZEŁ 3 (AGENT): Analiza — czyta state z poprzednich węzłów
# =============================================================================

analysis_agent = Agent(
    name="code_analysis",
    model=MODEL,
    instruction="""Wykonujesz analizę kodu z pełnym kontekstem.

KOD: "{raw_code}"
METADANE: "{code_metadata}"
CEL: "{analysis_goal}"

Zidentyfikuj issues i oceń severity. Odpowiedz JSON:
{{
  "issues": [{{"type": "...", "description": "...", "severity": "high|medium|low"}}],
  "overall_severity": "critical|high|medium|low|none",
  "recommendations": ["..."],
  "findings": "podsumowanie w 1-2 zdaniach"
}}""",
    output_key="analysis_result",  # → state["analysis_result"]
)


# =============================================================================
# WĘZEŁ 4 (FUNKCJA+AGENT): Walidacja — deterministic check + LLM summary
# =============================================================================

def pre_validate(node_input: str):
    """
    Węzeł-funkcja: deterministyczna walidacja przed finalnym raportem.
    W v2 funkcja może czytać state przez node_input (wynik poprzedniego węzła)
    lub być podłączona bezpośrednio w edges.
    """
    result = validate_report(node_input)
    yield Event(state={
        "validation": result,
        "validation_passed": result["valid"],
        "confidence": result["confidence"],
    })


report_agent = Agent(
    name="final_report",
    model=MODEL,
    instruction="""Generujesz finalny raport analizy kodu.

KOD (fragment): "{raw_code:.200}"
METADANE: "{code_metadata}"
ANALIZA: "{analysis_result}"
WALIDACJA: "{validation}"

## Code Analysis Report

**Language**: (z metadata)
**Confidence**: {confidence}%
**Analysis Goal**: {analysis_goal}

### Findings
(z analysis_result — tylko jeśli validation_passed == true)

### Recommendations
(priorytetyzowane)

### Data Quality
Kompletność raportu: {confidence}%
Brakujące sekcje: (z validation)""",
)


# =============================================================================
# ROOT AGENT — Workflow z miksem funkcji i agentów jako węzłów
# =============================================================================
# Graf: START → parse_input → enrichment → analysis → pre_validate → report
#
# KLUCZOWA LEKCJA:
#   Węzły-funkcje (parse_input, pre_validate) są DETERMINISTYCZNE → testowalność
#   Węzły-Agenty (enrichment, analysis, report) używają LLM → elastyczność
#   Miksowanie obu typów = optymalne użycie zasobów

root_agent = Workflow(
    name="root_agent",
    edges=[
        (
            "START",
            parse_input,       # funkcja → ustawia state (deterministyczna)
            enrichment_agent,  # Agent → narzędzie + LLM
            analysis_agent,    # Agent → czyta state["raw_code", "code_metadata"]
            pre_validate,      # funkcja → deterministyczna walidacja
            report_agent,      # Agent → agregacja i raport
        ),
    ],
)

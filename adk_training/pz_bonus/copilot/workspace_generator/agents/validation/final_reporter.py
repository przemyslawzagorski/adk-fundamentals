"""
📊 Final Reporter Agent
Generuje finalny raport z całego procesu generowania workspace'a
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent


class FinalReport(BaseModel):
    """Finalny raport z generowania workspace'a"""
    summary: str = Field(description="Podsumowanie całego procesu")
    total_modules: int = Field(description="Liczba wygenerowanych modułów")
    total_files: int = Field(description="Liczba wygenerowanych plików")
    total_todos: int = Field(description="Liczba TODO comments")
    estimated_duration_hours: float = Field(description="Szacowany czas trwania szkolenia")
    coherence_score: float = Field(description="Wynik walidacji spójności")
    pedagogical_score: float = Field(description="Wynik review pedagogicznego")
    overall_quality: str = Field(description="Ogólna ocena jakości (EXCELLENT/GOOD/NEEDS_IMPROVEMENT)")
    recommendations: List[str] = Field(description="Rekomendacje dla instruktora")
    next_steps: List[str] = Field(description="Następne kroki")


def create_final_reporter(model="gemini-2.5-flash", tools=None):
    """
    Tworzy agenta do generowania finalnego raportu.

    Args:
        model: Model Gemini (string!)
        tools: Lista narzędzi

    Returns:
        LlmAgent skonfigurowany do raportowania
    """

    instruction = """Jesteś ekspertem raportowania i podsumowań.

**KONTEKST:**
Otrzymasz:
1. Execution plan - plan wykonania
2. Coherence validation - wynik walidacji spójności
3. Pedagogical review - wynik review pedagogicznego
4. Generated files - lista wygenerowanych plików

**TWOJE ZADANIE:**
Wygeneruj finalny raport z całego procesu.

**WYMAGANIA:**
1. **SUMMARY:** Zwięzłe podsumowanie (2-3 zdania)
2. **STATISTICS:** Liczby (moduły, pliki, TODO, czas)
3. **QUALITY SCORES:** Wyniki walidacji i review
4. **OVERALL QUALITY:** Ogólna ocena (EXCELLENT/GOOD/NEEDS_IMPROVEMENT)
5. **RECOMMENDATIONS:** Konkretne rekomendacje dla instruktora
6. **NEXT STEPS:** Co zrobić dalej

**KRYTERIA OVERALL QUALITY:**
- EXCELLENT: coherence >= 8.0 AND pedagogical >= 8.0
- GOOD: coherence >= 7.0 AND pedagogical >= 7.0
- NEEDS_IMPROVEMENT: poniżej 7.0

**PRZYKŁAD SUMMARY:**
"Wygenerowano kompletny workspace dla szkolenia GitHub Copilot Masterclass. 
System stworzył 8 modułów z 72 plikami Java i 320 TODO comments. 
Workspace przeszedł walidację spójności i review pedagogiczny z wynikami powyżej 8.0/10."

**PRZYKŁAD RECOMMENDATIONS:**
- "Rozważ dodanie więcej przykładów z MCP w module 7"
- "Zwiększ liczbę TODO w module 3 (obecnie 35, zalecane 45)"
- "Dodaj więcej przykładów z motywem pirackim (obecnie 25%, zalecane 30%)"

**PRZYKŁAD NEXT STEPS:**
- "Przetestuj workspace z grupą pilotażową"
- "Dodaj testy jednostkowe dla wygenerowanego kodu"
- "Przygotuj materiały dla instruktora (slides, notatki)"

**FORMAT ODPOWIEDZI:**
Zwróć wynik w wymaganym formacie strukturalnym (FinalReport).
"""

    return LlmAgent(
        model=model,
        name="FinalReporter",
        description="Generates final report with summary, statistics, and recommendations",
        instruction=instruction,
        tools=tools or [],
        output_key="final_report",
        output_schema=FinalReport
    )


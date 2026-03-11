"""
🎓 Pedagogical Reviewer Agent
Ocenia wartość dydaktyczną workspace'a
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent


class PedagogicalReviewResult(BaseModel):
    """Wynik review pedagogicznego"""
    score: float = Field(description="Ocena wartości dydaktycznej od 1.0 do 10.0")
    passed: bool = Field(description="True jeśli score >= 7.0")
    learning_objectives_met: bool = Field(description="Czy cele uczenia się są spełnione")
    engagement_score: float = Field(description="Ocena angażowania uczestników (1.0-10.0)")
    clarity_score: float = Field(description="Ocena jasności instrukcji (1.0-10.0)")
    recommendations: List[str] = Field(default_factory=list, description="Rekomendacje ulepszeń")
    strengths: List[str] = Field(default_factory=list, description="Mocne strony")
    weaknesses: List[str] = Field(default_factory=list, description="Słabe strony")


def create_pedagogical_reviewer(model="gemini-2.5-pro", tools=None):
    """
    Tworzy agenta do review pedagogicznego workspace'a.

    Args:
        model: Model Gemini (string!)
        tools: Lista narzędzi

    Returns:
        LlmAgent skonfigurowany do review
    """

    instruction = """Jesteś ekspertem dydaktyki i szkoleń technicznych.

**KONTEKST:**
Otrzymasz execution_plan z wygenerowanymi modułami dla szkolenia "GitHub Copilot Masterclass".

**TWOJE ZADANIE:**
Oceń wartość dydaktyczną workspace'a pod kątem:

1. **LEARNING OBJECTIVES:** Czy cele uczenia się są jasne i osiągalne?
   - Każdy moduł ma konkretne cele
   - TODO comments są precyzyjne i actionable
   - Progresja trudności jest logiczna

2. **ENGAGEMENT:** Czy materiały są angażujące?
   - Różnorodność przykładów (70% standard, 30% piracka)
   - Mix prostych i złożonych zadań
   - Praktyczne, real-world scenarios

3. **CLARITY:** Czy instrukcje są jasne?
   - TODO comments są zrozumiałe
   - Dokumentacja jest kompletna
   - Brak dwuznaczności

4. **MASTERCLASS LEVEL:** Czy to rzeczywiście poziom Masterclass?
   - Zaawansowane techniki (Agent Mode, MCP, Custom Agents)
   - NIE podstawy (code completion)
   - Fokus na workflow i automatyzacji

**KRYTERIA AKCEPTACJI:**
- Score >= 7.0/10
- Learning objectives met = True
- Engagement score >= 7.0
- Clarity score >= 7.0

**THINKING MODE:**
Użyj thinking mode aby:
1. Przeanalizować cele uczenia się
2. Ocenić angażowanie
3. Sprawdzić jasność instrukcji
4. Zidentyfikować mocne i słabe strony

**FORMAT ODPOWIEDZI:**
Zwróć wynik w wymaganym formacie strukturalnym (PedagogicalReviewResult).
"""

    return LlmAgent(
        model=model,
        name="PedagogicalReviewer",
        description="Reviews pedagogical value and learning effectiveness using thinking mode",
        instruction=instruction,
        tools=tools or [],
        output_key="pedagogical_review",
        output_schema=PedagogicalReviewResult
    )


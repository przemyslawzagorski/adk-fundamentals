"""
🔍 Coherence Validator Agent
Waliduje spójność wygenerowanego workspace'a
"""

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from google.adk.agents import LlmAgent


class CoherenceValidationResult(BaseModel):
    """Wynik walidacji spójności"""
    score: float = Field(description="Ocena spójności od 1.0 do 10.0")
    passed: bool = Field(description="True jeśli score >= 7.0")
    issues: List[str] = Field(default_factory=list, description="Lista problemów")
    dependency_issues: List[str] = Field(default_factory=list, description="Problemy z zależnościami")
    progression_issues: List[str] = Field(default_factory=list, description="Problemy z progresją")
    duplicate_issues: List[str] = Field(default_factory=list, description="Duplikaty")


def create_coherence_validator(model="gemini-2.5-pro", tools=None):
    """
    Tworzy agenta do walidacji spójności workspace'a.

    Args:
        model: Model Gemini (string!)
        tools: Lista narzędzi

    Returns:
        LlmAgent skonfigurowany do walidacji
    """

    instruction = """Jesteś ekspertem walidacji workspace'ów szkoleniowych.

**KONTEKST:**
Otrzymasz execution_plan z wygenerowanymi modułami.

**TWOJE ZADANIE:**
Zwaliduj spójność workspace'a pod kątem:

1. **DEPENDENCIES:** Czy moduły są w logicznej kolejności?
   - Moduł 5 (Agent Mode) wymaga wiedzy z modułów 1-4
   - Moduł 7 (MCP) wymaga wiedzy z modułu 6 (Custom Agents)
   - Brak circular dependencies

2. **PROGRESSION:** Czy trudność rośnie stopniowo?
   - Moduły 1-2: BEGINNER → INTERMEDIATE
   - Moduły 3-4: INTERMEDIATE
   - Moduły 5-8: INTERMEDIATE → ADVANCED
   - Brak skoków trudności

3. **DUPLICATES:** Czy nie ma duplikatów przykładów?
   - Każda klasa Java powinna być unikalna
   - Różnorodność scenariuszy

**KRYTERIA AKCEPTACJI:**
- Score >= 7.0/10
- Brak krytycznych problemów z zależnościami
- Logiczna progresja trudności
- Brak duplikatów

**THINKING MODE:**
Użyj thinking mode aby:
1. Przeanalizować zależności między modułami
2. Sprawdzić progresję trudności
3. Wykryć potencjalne duplikaty
4. Ocenić ogólną spójność

**FORMAT ODPOWIEDZI:**
Zwróć wynik w wymaganym formacie strukturalnym (CoherenceValidationResult).
"""

    return LlmAgent(
        model=model,
        name="CoherenceValidator",
        description="Validates workspace coherence and consistency using thinking mode",
        instruction=instruction,
        tools=tools or [],
        output_key="coherence_validation",
        output_schema=CoherenceValidationResult
    )


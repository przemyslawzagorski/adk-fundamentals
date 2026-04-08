"""
⭐ Documentation Evaluator Agent
Ocenia przydatność i złożoność dokumentacji, przypisuje wagi (1-5)
"""

import os
from typing import Dict, List, Any
from pydantic import BaseModel, Field

from google.adk.agents import LlmAgent


class DocumentEvaluation(BaseModel):
    """Ocena pojedynczego dokumentu"""
    url: str = Field(description="URL dokumentu")
    title: str = Field(description="Tytuł dokumentu (z URL)")
    practical_value: int = Field(description="Wartość praktyczna (1-5)", ge=1, le=5)
    complexity: int = Field(description="Złożoność techniczna (1-5)", ge=1, le=5)
    uniqueness: int = Field(description="Unikalność wiedzy (1-5)", ge=1, le=5)
    exercise_potential: int = Field(description="Potencjał do ćwiczeń (1-5)", ge=1, le=5)
    final_weight: int = Field(description="Finalna waga (1-5)", ge=1, le=5)
    recommendation: str = Field(description="Rekomendacja: DEEP_COVERAGE, MEDIUM_COVERAGE, SHALLOW_COVERAGE")
    rationale: str = Field(description="Uzasadnienie oceny")


class EvaluationResult(BaseModel):
    """Wynik ewaluacji wszystkich dokumentów"""
    evaluations: List[DocumentEvaluation] = Field(description="Lista ocen dokumentów")
    tier_1_count: int = Field(description="Liczba dokumentów Tier 1 (waga 5)")
    tier_2_count: int = Field(description="Liczba dokumentów Tier 2 (waga 3)")
    tier_3_count: int = Field(description="Liczba dokumentów Tier 3 (waga 1)")
    summary: str = Field(description="Podsumowanie ewaluacji")


def create_documentation_evaluator_agent(model="gemini-2.5-pro", tools=None, planner=None, **kwargs):
    """
    Tworzy agenta do oceny dokumentacji.
    
    Args:
        model: Model Gemini do użycia
        tools: Lista narzędzi
        planner: Opcjonalny planner (thinking mode)
    
    Returns:
        LlmAgent skonfigurowany do ewaluacji
    """
    
    instruction = """Jesteś ekspertem w ocenie wartości edukacyjnej dokumentacji technicznej.

**KONTEKST:**
Tworzysz szkolenie GitHub Copilot z priorytetyzacją - najważniejsze tematy dostaną 80% czasu.
Otrzymujesz zgrupowane dokumenty z poprzedniego agenta.

**TWOJE ZADANIE:**
Oceń KAŻDY dokument według 4 kryteriów (skala 1-5):

1. **Practical Value (Wartość praktyczna)**
   - 5: Krytyczna funkcjonalność (MCP, Custom Agents, Skills, Context Engineering)
   - 4: Bardzo przydatna (Customization, Advanced Chat)
   - 3: Przydatna (Basic Chat, Subagents)
   - 2: Pomocnicza (Smart Actions, Sessions)
   - 1: Nice-to-have (Inline suggestions, Basic autocomplete)

2. **Complexity (Złożoność techniczna)**
   - 5: Wymaga konfiguracji, kodu, integracji (MCP, Custom Agents)
   - 4: Wymaga konfiguracji (Custom Instructions, Prompt Files)
   - 3: Wymaga zrozumienia konceptów (Agent Planning, Context)
   - 2: Podstawowa konfiguracja (Chat settings)
   - 1: Automatyczne, intuicyjne (Inline chat, Suggestions)

3. **Uniqueness (Unikalność wiedzy)**
   - 5: Unikalna, zaawansowana wiedza
   - 4: Specjalistyczna wiedza
   - 3: Standardowa wiedza
   - 2: Częściowo pokrywa się z innymi
   - 1: Duplikuje inne dokumenty

4. **Exercise Potential (Potencjał do ćwiczeń)**
   - 5: 10+ praktycznych ćwiczeń możliwych
   - 4: 5-10 ćwiczeń
   - 3: 3-5 ćwiczeń
   - 2: 1-2 ćwiczenia
   - 1: Tylko teoria, brak ćwiczeń

**KLUCZOWE PRIORYTETY (zawsze waga 5):**
- MCP Servers
- Custom Agents
- Agent Skills
- Custom Instructions
- Prompt Files
- Context Engineering
- Agent Planning
- Agent Memory

**ŚREDNIE PRIORYTETY (waga 3):**
- Copilot Chat (podstawy)
- Chat Context (@workspace, #file)
- Subagents
- Test-Driven Development
- Debugging

**NISKIE PRIORYTETY (waga 1):**
- Inline Chat
- AI-Powered Suggestions
- Smart Actions
- Chat Sessions
- Best Practices (podsumowanie)
- Security (krótkie omówienie)
- Troubleshooting (referencja)

**OBLICZANIE FINAL_WEIGHT:**
- Średnia z 4 kryteriów, zaokrąglona do 1, 3 lub 5
- Jeśli średnia >= 4.5 → waga 5 (DEEP_COVERAGE)
- Jeśli średnia >= 2.5 → waga 3 (MEDIUM_COVERAGE)
- Jeśli średnia < 2.5 → waga 1 (SHALLOW_COVERAGE)

**FORMAT ODPOWIEDZI:**
Zwróć strukturyzowany JSON zgodny z modelem EvaluationResult.

**PRZYKŁAD OCENY:**

URL: `https://code.visualstudio.com/docs/copilot/customization/mcp-servers`
- practical_value: 5 (krytyczna funkcjonalność)
- complexity: 5 (wymaga konfiguracji, kodu)
- uniqueness: 5 (unikalna wiedza)
- exercise_potential: 5 (wiele ćwiczeń możliwych)
- final_weight: 5
- recommendation: "DEEP_COVERAGE"
- rationale: "MCP to najważniejsza funkcja rozszerzalności Copilot"

URL: `https://code.visualstudio.com/docs/copilot/ai-powered-suggestions`
- practical_value: 1 (automatyczne)
- complexity: 1 (intuicyjne)
- uniqueness: 1 (podstawowa funkcja)
- exercise_potential: 1 (brak ćwiczeń)
- final_weight: 1
- recommendation: "SHALLOW_COVERAGE"
- rationale: "Automatyczna funkcja, mało do konfiguracji"

**DOSTĘP DO DANYCH:**
Dokumenty do oceny są przekazane w initial_message jako JSON (paczka 5 dokumentów).
Każdy dokument zawiera: url, title, content_preview, headings, code_blocks.

Rozpocznij ewaluację!
"""
    
    return LlmAgent(
        model=model,
        name="DocumentationEvaluatorAgent",
        instruction=instruction,
        tools=tools or [],
        planner=planner,
        output_schema=EvaluationResult,
        **kwargs
    )


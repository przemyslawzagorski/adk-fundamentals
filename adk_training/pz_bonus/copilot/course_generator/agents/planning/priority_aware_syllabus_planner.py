"""
📚 Priority-Aware Syllabus Planner Agent
Tworzy plan szkolenia z priorytetami i alokacją czasu
"""

import os
from typing import Dict, List, Any
from pydantic import BaseModel, Field

from google.adk.agents import LlmAgent


class Lesson(BaseModel):
    """Pojedyncza lekcja w module"""
    id: str = Field(description="ID lekcji (np. 'lesson_01_01')")
    title: str = Field(description="Tytuł lekcji")
    concepts: List[str] = Field(description="Koncepcje omawiane w lekcji")
    exercises: List[str] = Field(description="Lista ćwiczeń (krótkie opisy)")
    config_files: List[str] = Field(description="Pliki konfiguracyjne do utworzenia")
    estimated_time_minutes: int = Field(description="Szacowany czas w minutach")


class Module(BaseModel):
    """Moduł szkoleniowy"""
    id: str = Field(description="ID modułu (np. 'module_01')")
    name: str = Field(description="Nazwa modułu (po polsku)")
    priority: int = Field(description="Priorytet (1, 3 lub 5)", ge=1, le=5)
    estimated_hours: float = Field(description="Szacowany czas w godzinach")
    depth: str = Field(description="Głębokość pokrycia: deep, medium, shallow")
    group: str = Field(description="Grupa tematyczna (agents, customization, chat, etc.)")
    lessons: List[Lesson] = Field(description="Lista lekcji w module")
    tier: str = Field(description="Tier: tier_1_critical, tier_2_important, tier_3_nice_to_have")


class SyllabusResult(BaseModel):
    """Kompletny plan szkolenia"""
    modules: List[Module] = Field(description="Lista modułów")
    total_estimated_hours: float = Field(description="Całkowity czas szkolenia w godzinach")
    tier_1_hours: float = Field(description="Czas dla Tier 1 (80%)")
    tier_2_hours: float = Field(description="Czas dla Tier 2 (15%)")
    tier_3_hours: float = Field(description="Czas dla Tier 3 (5%)")
    summary: str = Field(description="Podsumowanie planu")


def create_priority_aware_syllabus_planner(model="gemini-2.5-pro", tools=None, planner=None, **kwargs):
    """
    Tworzy agenta do planowania sylabusa z priorytetami.
    
    Args:
        model: Model Gemini do użycia
        tools: Lista narzędzi
        planner: Opcjonalny planner (thinking mode)
    
    Returns:
        LlmAgent skonfigurowany do planowania
    """
    
    instruction = """Jesteś ekspertem w projektowaniu programów szkoleniowych z priorytetyzacją.

**KONTEKST:**
Tworzysz plan szkolenia GitHub Copilot na ~32 godziny z alokacją 80/15/5 (Tier 1/2/3).
Otrzymujesz oceny dokumentacji z poprzedniego agenta.

**TWOJE ZADANIE:**

1. **POGRUPUJ DOKUMENTY** według ocen (final_weight):
   - Tier 1 (waga 5): Agents, MCP, Customization, Skills, Context → 80% czasu (~26h)
   - Tier 2 (waga 3): Chat, Subagents, TDD, Debug → 15% czasu (~5h)
   - Tier 3 (waga 1): Inline, Suggestions, Best Practices → 5% czasu (~1h)

2. **UTWÓRZ MODUŁY** dla każdego tier:
   
   **TIER 1 - CRITICAL (5-6 modułów, ~26h):**
   - Module 01: Tryb Agent - Fundament Pracy z Copilot (8h)
     * Lekcje: Agent Overview, Planning, Memory, Tools
     * 10-15 ćwiczeń na moduł
   - Module 02: MCP Servers - Rozszerzanie Copilot (6h)
     * Lekcje: MCP Intro, Installation, Custom MCP
     * 10-12 ćwiczeń
   - Module 03: Customization - Dostosowanie do Projektu (5h)
     * Lekcje: Custom Instructions, Prompt Files, Hooks
     * 8-10 ćwiczeń
   - Module 04: Agent Skills - Rozbudowa Agentów (4h)
   - Module 05: Context Engineering - Skuteczne Prompty (3h)
   
   **TIER 2 - IMPORTANT (3-4 moduły, ~5h):**
   - Module 06: Copilot Chat - Podstawy (2h)
     * 3-5 ćwiczeń
   - Module 07: Chat Context i Subagents (1.5h)
   - Module 08: TDD i Debugging z Copilot (1.5h)
   
   **TIER 3 - NICE-TO-HAVE (2-3 moduły, ~1h):**
   - Module 09: Inline Chat i Suggestions (30min)
     * 1-2 ćwiczenia
   - Module 10: Best Practices i Security (30min)

3. **DLA KAŻDEGO MODUŁU:**
   - Podziel na 2-5 lekcji (więcej dla Tier 1)
   - Każda lekcja: tytuł, koncepcje, ćwiczenia, czas
   - Określ pliki konfiguracyjne (.github/copilot-instructions.md, .copilot/prompts/, etc.)
   - Alokuj czas proporcjonalnie do wagi

4. **ZASADY ALOKACJI CZASU:**
   - Tier 1 (waga 5): 3-8h na moduł, 10-15 ćwiczeń
   - Tier 2 (waga 3): 1-2h na moduł, 3-5 ćwiczeń
   - Tier 3 (waga 1): 0.5-1h na moduł, 1-2 ćwiczenia

5. **PRZYKŁADY ĆWICZEŃ (konkretne, praktyczne):**
   
   **Tier 1 (zaawansowane):**
   - "Użyj @workspace do analizy architektury spring-petclinic"
   - "Stwórz custom MCP server integrujący API Jira"
   - "Napisz prompt file do generowania testów zgodnych z team standards"
   
   **Tier 2 (podstawowe):**
   - "Zadaj pytanie o strukturę projektu używając @workspace"
   - "Użyj #file do analizy konkretnej klasy"
   
   **Tier 3 (minimalne):**
   - "Użyj Ctrl+I do refaktoringu metody"
   - "Przetestuj inline suggestions"

**FORMAT ODPOWIEDZI:**
Zwróć strukturyzowany JSON zgodny z modelem SyllabusResult.

**WAŻNE:**
- Wszystkie nazwy modułów i lekcji PO POLSKU
- Ćwiczenia konkretne, odnoszące się do spring-petclinic (repo Java)
- Suma godzin: ~32h (26h + 5h + 1h)
- Proporcje: 80% / 15% / 5%

**DOSTĘP DO DANYCH:**
Oceny dokumentacji są przekazane w initial_message jako JSON (EvaluationResult).

Rozpocznij planowanie!
"""
    
    return LlmAgent(
        model=model,
        name="PriorityAwareSyllabusPlannerAgent",
        instruction=instruction,
        tools=tools or [],
        planner=planner,
        output_schema=SyllabusResult,
        **kwargs
    )


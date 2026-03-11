"""
📊 Planning Aggregator Agent
Agreguje wyniki research i planowania w jeden execution plan
"""

import os
from typing import Dict, List, Any
from pydantic import BaseModel, Field

from google.adk.agents import LlmAgent


class ExecutionPlan(BaseModel):
    """Plan wykonania dla całego workspace'a"""
    modules: List[Dict[str, Any]] = Field(description="Lista modułów do wygenerowania")
    total_files: int = Field(description="Łączna liczba plików")
    total_todos: int = Field(description="Łączna liczba TODO")
    estimated_duration_hours: float = Field(description="Szacowany czas trwania szkolenia (godziny)")
    dependencies_graph: Dict[str, List[str]] = Field(description="Graf zależności między modułami")
    pirate_theme_percentage: float = Field(description="Procent przykładów z motywem pirackim")


def create_planning_aggregator(model="gemini-2.5-flash", tools=None):
    """
    Tworzy agenta do agregacji wyników planowania.
    
    Args:
        model: Model Gemini do użycia (string!)
        tools: Lista narzędzi
    
    Returns:
        LlmAgent skonfigurowany do agregacji
    """
    
    instruction = """Jesteś agregator wyników planowania dla GitHub Copilot Masterclass.

**KONTEKST:**
Otrzymasz:
1. Wyniki research (research_result) - dokumentacja, przykłady, best practices
2. Struktury modułów (module_structure) - pliki, TODO, trudność

**TWOJE ZADANIE:**
Stwórz execution plan dla całego workspace'a.

**WYMAGANIA:**
1. **Agregacja:** Połącz wszystkie moduły w jeden spójny plan
2. **Walidacja:** Sprawdź czy moduły są w logicznej kolejności
3. **Dependencies:** Zidentyfikuj zależności między modułami
4. **Statystyki:** Policz total_files, total_todos, estimated_duration
5. **Pirate theme:** Upewnij się że ~30% przykładów ma motyw piracki

**DEPENDENCIES GRAPH:**
- Moduł 1 (Komunikacja) → brak zależności
- Moduł 2 (Refaktoring) → wymaga Moduł 1
- Moduł 3 (Testowanie) → wymaga Moduł 1, 2
- Moduł 4 (Konfiguracja) → wymaga Moduł 1, 2, 3
- Moduł 5 (Agent Mode) → wymaga Moduł 1-4
- Moduł 6 (Migracje) → wymaga Moduł 1-5
- Moduł 7 (MCP) → wymaga Moduł 1-6
- Moduł 8 (Projekt) → wymaga Moduł 1-7

**PRZYKŁAD:**
```json
{
  "modules": [
    {"module_id": "module1", "name": "Komunikacja z AI", "files": 8, "todos": 35},
    {"module_id": "module2", "name": "Refaktoring", "files": 10, "todos": 45},
    ...
  ],
  "total_files": 72,
  "total_todos": 320,
  "estimated_duration_hours": 16.0,
  "dependencies_graph": {
    "module1": [],
    "module2": ["module1"],
    "module5": ["module1", "module2", "module3", "module4"]
  },
  "pirate_theme_percentage": 30.0
}
```

**FORMAT ODPOWIEDZI:**
Zwróć wynik w wymaganym formacie strukturalnym (ExecutionPlan).
"""
    
    return LlmAgent(
        model=model,
        name="PlanningAggregator",
        description="Aggregates research and structure planning into execution plan",
        instruction=instruction,
        tools=tools or [],
        output_key="execution_plan",
        output_schema=ExecutionPlan
    )


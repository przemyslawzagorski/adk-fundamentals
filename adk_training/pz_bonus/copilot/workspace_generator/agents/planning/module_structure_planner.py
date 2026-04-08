"""
📐 Module Structure Planner Agent
Projektuje strukturę plików dla każdego modułu szkolenia
"""

import os
from typing import Dict, List, Any
from enum import Enum
from pydantic import BaseModel, Field

from google.adk.agents import LlmAgent


class FileType(str, Enum):
    """Typy plików w workspace"""
    JAVA_CODE = "java_code"
    PYTHON_CODE = "python_code"
    REACT_COMPONENT = "react_component"  # ← DODANO dla modułu 8
    MARKDOWN_DOC = "markdown_doc"
    CONFIG_FILE = "config_file"
    TEST_FILE = "test_file"
    PROMPT_FILE = "prompt_file"
    MCP_SERVER = "mcp_server"


class DifficultyLevel(str, Enum):
    """Poziomy trudności"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class FileSpec(BaseModel):
    """Specyfikacja pojedynczego pliku"""
    path: str = Field(description="Ścieżka do pliku (np. src/main/java/Module5AgentMode.java)")
    file_type: FileType = Field(description="Typ pliku")
    file_name: str = Field(description="Nazwa pliku z odpowiednim rozszerzeniem (np. App.java, script.py, Dashboard.tsx)")  # ← ZMIANA z class_name
    purpose: str = Field(description="Cel dydaktyczny pliku")
    copilot_todos: int = Field(description="Liczba TODO dla Copilot (3-8)")
    difficulty: DifficultyLevel = Field(description="Poziom trudności")
    dependencies: List[str] = Field(default_factory=list, description="Zależności od innych plików")
    learning_objectives: List[str] = Field(description="Cele uczenia się")
    estimated_time_minutes: int = Field(description="Szacowany czas (minuty)")


class ModuleStructure(BaseModel):
    """Struktura modułu szkoleniowego"""
    module_id: str = Field(description="ID modułu (np. module5)")
    module_name: str = Field(description="Nazwa modułu")
    files: List[FileSpec] = Field(description="Lista plików do wygenerowania")
    total_todos: int = Field(description="Łączna liczba TODO")
    estimated_duration_minutes: int = Field(description="Szacowany czas trwania modułu")
    prerequisites: List[str] = Field(default_factory=list, description="Wymagania wstępne")
    learning_outcomes: List[str] = Field(description="Oczekiwane rezultaty nauki")


def create_module_structure_planner(model="gemini-2.5-pro", tools=None, planner=None, **kwargs):
    """
    Tworzy agenta do projektowania struktury modułów.
    
    Args:
        model: Model Gemini do użycia (string!)
        tools: Lista narzędzi
    
    Returns:
        LlmAgent skonfigurowany do planowania struktury
    """
    
    instruction = """Jesteś architektem workspace'ów szkoleniowych dla GitHub Copilot Masterclass.

**KONTEKST:**
Otrzymasz:
1. **Plan szkolenia** (training_plan) - tematy modułów wysłane do studentów
2. **Plan funkcyjny** (funkcje_plan) - mapowanie funkcji Copilota do modułów
3. Wyniki research (dokumentacja, przykłady, best practices)

**KRYTYCZNE: MUSISZ WYGENEROWAĆ WSZYSTKIE 8 MODUŁÓW!**
- Dzień 1: Moduły 1, 2, 3, 4
- Dzień 2: Moduły 5, 6, 7, 8

**TWOJE ZADANIE:**
Zaprojektuj strukturę plików dla KAŻDEGO modułu szkolenia (1-8).

**KLUCZOWE:** Każdy plik musi uczyć KONKRETNEJ FUNKCJI z planu funkcyjnego!
Przykład: Jeśli moduł 1 ma funkcje [Inline, Chat, Agent Mode, @workspace], to:
- Plik 1: Inline suggestions (TODO: Use inline completion to...)
- Plik 2: Chat mode (TODO: Use Copilot Chat to...)
- Plik 3: Agent Mode (TODO: Use Agent Mode to...)
- Plik 4: @workspace (TODO: Use @workspace to...)

**WYMAGANIA:**
1. **Liczba plików:** 5-12 plików na moduł
2. **TODO comments:** 3-8 TODO na plik (precyzyjne, actionable)
3. **Progresja trudności:** BEGINNER → INTERMEDIATE → ADVANCED
4. **Różnorodność:** Mix prostych i złożonych przykładów
5. **Domena:** 70% standard, 30% piracka (subtelnie!)

**TECHNOLOGIE (zależnie od modułu):**
- **Moduły 1-6:** Java 17+, Spring Boot 3.x, JUnit 5, Maven/Gradle
- **Moduł 7:** Python 3.10+, typing, pytest
- **Moduł 8:** React, TypeScript (.tsx), Functional Components

**DOBÓR JĘZYKA:**
Sprawdź numer modułu i dobierz odpowiednią technologię:
- Moduły 1-6: Java (pliki .java, file_type=JAVA_CODE)
- Moduł 7: Python (pliki .py, file_type=PYTHON_CODE)
- Moduł 8: React/TypeScript (pliki .tsx, file_type=REACT_COMPONENT)

**STRUKTURA PLIKU:**
- file_name: Nazwa z rozszerzeniem (np. AgentModeRefactoring.java, migration_tool.py, Dashboard.tsx)
- Package (Java): com.copilot.training.moduleX
- TODO: Konkretne zadania dla Copilot (np. "Use Agent Mode to refactor this method")

**PRZYKŁAD (Moduł 5: Agent Mode):**
- AgentModeBasics.java (BEGINNER, 3 TODO, 15 min)
- MultiFileRefactoring.java (INTERMEDIATE, 5 TODO, 25 min)
- SelfCorrectingWorkflow.java (ADVANCED, 7 TODO, 35 min)
- AgentModeWithMCP.java (EXPERT, 8 TODO, 45 min)

**FORMAT ODPOWIEDZI:**
Zwróć wynik w wymaganym formacie strukturalnym (ModuleStructure).
"""
    
    agent_params = {
        "model": model,
        "name": "ModuleStructurePlanner",
        "description": "Plans file structure for training modules with learning progression",
        "instruction": instruction,
        "tools": tools or [],
        "output_key": "module_structure",
        "output_schema": ModuleStructure
    }

    if planner:
        agent_params["planner"] = planner

    return LlmAgent(**agent_params)


"""
🏗️ Module Generator Agent
Generuje kompletny moduł szkoleniowy (kod, testy, dokumentacja, konfiguracja)
"""

import os
from typing import Dict, Any, List, AsyncGenerator
from pydantic import BaseModel, Field

from google.adk.agents import LlmAgent, LoopAgent, BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.adk.agents.callback_context import CallbackContext


# =============================================================================
# CALLBACK: Track Iteration
# =============================================================================

async def track_iteration(callback_context: CallbackContext):
    """Callback: Zlicza iteracje i dba o poprawne zmienne w stanie początkowym."""
    iteration = callback_context.state.get("iteration", 0) + 1
    callback_context.state["iteration"] = iteration

    # Zabezpieczenie przed błędem w pierwszej iteracji
    if "critique" not in callback_context.state:
        callback_context.state["critique"] = {"feedback": "To jest pierwsza iteracja. Brak uwag krytyka.", "is_approved": False}

    return None


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class CodeCritique(BaseModel):
    """Ustrukturyzowany format oceny krytyka kodu."""
    score: float = Field(description="Ocena jakości kodu od 1.0 do 10.0")
    feedback: str = Field(description="Szczegółowa krytyka, co poprawić")
    is_approved: bool = Field(description="True jeśli kod jest wystarczająco dobry (score >= 7.0)")
    errors: List[str] = Field(default_factory=list, description="Lista błędów do naprawy")


# =============================================================================
# POLYGLOT CODE AGENT (Writer) - Java/Python/React
# =============================================================================

def create_polyglot_code_agent(module_id: int, model="gemini-2.5-flash", tools=None):
    """Tworzy agenta generującego kod w różnych językach (Java/Python/React)"""

    instruction = f"""Jesteś programistą realizującym MODUŁ NR {module_id} z planu szkolenia GitHub Copilot Masterclass.

**KRYTYCZNE: TWÓJ MODUŁ TO module{module_id}!**
Nie wracaj do poprzednich modułów. Skup się WYŁĄCZNIE na module{module_id}.

**KONTEKST:**
1. Znajdź w 'execution_plan' moduł o module_id: "module{module_id}"
2. W tym module znajdziesz listę plików do wygenerowania (pole 'files')
3. Dla KAŻDEGO pliku z tej listy:
   - Wygeneruj kod zgodnie z file_spec (file_name, file_type, purpose, copilot_todos)
   - Wywołaj narzędzie 'create_file' z odpowiednią ścieżką i kodem

**FEEDBACK Z POPRZEDNIEJ ITERACJI:**
{{critique}}

Zignoruj powyższy feedback, jeśli to pierwsza iteracja.
Jeśli jest feedback - zastosuj się do niego rygorystycznie i popraw kod.

**TWOJE ZADANIE:**
Wygeneruj WSZYSTKIE pliki dla module{module_id} z TODO comments dla GitHub Copilot.

**DOBÓR JĘZYKA (na podstawie file_type):**
- JAVA_CODE → Java 17+, Spring Boot 3.x, JUnit 5
- PYTHON_CODE → Python 3.10+, typing, pytest
- REACT_COMPONENT → React, TypeScript (.tsx), Functional Components

**WYMAGANIA:**
1. **Składnia:** Poprawna dla danego języka
2. **TODO:** Precyzyjne, actionable TODO comments (// dla Java/TS, # dla Python)
3. **Jakość:** Clean code, SOLID principles
4. **Masterclass:** Zaawansowane przykłady, NIE podstawy
5. **Domena:** Mix standard i piracka (subtelnie!)

**FORMAT TODO:**
```java
// TODO: Use Copilot Agent Mode to implement multi-file refactoring
// TODO: Refactor using @workspace context for better suggestions
// TODO: Apply self-correction loop with Agent Mode
```

**PRZYKŁAD (Agent Mode):**
```java
package com.copilot.training.module5;

/**
 * Demonstrates GitHub Copilot Agent Mode for complex refactoring.
 * Learning objectives:
 * - Use Agent Mode for multi-file operations
 * - Understand self-correction loops
 * - Apply @workspace context effectively
 */
public class AgentModeWorkflow {{

    // TODO: Use Copilot Agent Mode to refactor this legacy code across multiple files
    public void processLegacyWorkflow() {{
        // Complex legacy code here...
    }}

    // TODO: Implement self-correction loop using Agent Mode feedback
    public void selfCorrectingProcess() {{
        // Implementation with error handling...
    }}
}}
```

**ZADANIE DODATKOWE (KRYTYCZNE!):**
Musisz wywołać 'create_file' TYLE RAZY, ILE PLIKÓW jest w sekcji 'files' Twojego modułu.
Jeśli w module{module_id} jest 5 plików, muszę zobaczyć 5 wywołań narzędzia 'create_file'!

Dla każdego pliku:
1. Wygeneruj pełny kod (z TODO comments)
2. Wywołaj create_file(path=file_spec.path, content=kod)
3. Przejdź do następnego pliku

Ścieżkę pliku weź z obiektu `file_spec.path` (który masz w kontekście).
Zapisuj plik w każdej iteracji - nowsza wersja po prostu nadpisze starą.

**ZWRÓĆ TYLKO KOD** (bez meta-komentarzy).
"""

    return LlmAgent(
        model=model,
        tools=tools,  # ← KLUCZOWE! Przekazujemy narzędzia (create_file, etc.)
        name=f"PolyglotCodeAgent_M{module_id}",  # ← Unikalna nazwa dla każdego modułu
        description=f"Generates code for module {module_id} (Java/Python/React) with TODO comments",
        instruction=instruction,
        output_key="generated_code",
        before_agent_callback=track_iteration
    )


# =============================================================================
# SYNTAX CRITIC (Critic)
# =============================================================================

def create_syntax_critic(model="gemini-2.5-flash"):
    """Tworzy krytyka kodu (polyglot - Java/Python/React)"""

    instruction = """Jesteś surowym krytykiem kodu (Java, Python, React).

**KOD DO OCENY:**
{generated_code}

**KRYTERIA:**
1. **Składnia:** Czy kod w docelowym języku (Java/Python/TSX) jest poprawny syntaktycznie?
2. **Język-specific:**
   - Java: Czy użyto wzorców Spring Boot? Czy kompiluje się?
   - Python: Czy używa typing? Czy zgodny z PEP 8?
   - React: Czy to functional component? Czy TypeScript jest poprawny?
3. **TODO:** Czy TODO są precyzyjne i actionable? (// dla Java/TS, # dla Python)
4. **Jakość:** Clean code, SOLID, best practices
5. **Masterclass:** Czy przykłady są zaawansowane?
6. **Domena:** Czy jest mix standard/piracka?

**OCENA:**
- Score: 1.0-10.0 (7.0+ = approved)
- Feedback: Konkretne uwagi
- is_approved: True jeśli score >= 7.0
- errors: Lista błędów do naprawy

**BĄDŹ SUROWY!** To szkolenie Masterclass - wymagaj wysokiej jakości.
"""

    return LlmAgent(
        model=model,
        name="SyntaxCritic",
        description="Reviews and critiques generated code (Java/Python/React)",
        instruction=instruction,
        output_key="critique",
        output_schema=CodeCritique
    )


# =============================================================================
# LOOP CONTROLLER (Controller)
# =============================================================================

class LoopController(BaseAgent):
    """Kontroler pętli - sprawdza czy kod został zaakceptowany"""

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # Pobierz critique ze stanu
        critique = ctx.session.state.get("critique", {})
        is_approved = critique.get("is_approved", False)

        # Log dla debugowania
        print(f"[Loop Controller] is_approved: {is_approved}")

        # Zwróć zdarzenie z akcją escalate
        yield Event(
            author=self.name,
            actions=EventActions(escalate=is_approved)
        )


# =============================================================================
# MODULE GENERATOR (LoopAgent)
# =============================================================================

def create_module_generator(module_id: int, model="gemini-2.5-flash", tools=None):
    """
    Tworzy generator modułu używając LoopAgent.

    Args:
        module_id: ID modułu (1-8)
        model: Model Gemini do użycia (string!)
        tools: Dict z narzędziami (file_operations, code_validator)

    Returns:
        LoopAgent skonfigurowany do generowania modułu
    """

    # Tworzymy sub-agentów (polyglot - Java/Python/React)
    # KLUCZOWE: Przekazujemy module_id do agenta!
    polyglot_code_agent = create_polyglot_code_agent(module_id=module_id, model=model, tools=tools)
    syntax_critic = create_syntax_critic(model=model)
    loop_controller = LoopController(name=f"LoopController_Module{module_id}")

    # Tworzymy LoopAgent
    return LoopAgent(
        name=f"ModuleGenerator_{module_id}",
        description=f"Generates module {module_id} with iterative code improvement (Java/Python/React)",
        max_iterations=3,
        sub_agents=[polyglot_code_agent, syntax_critic, loop_controller]
    )

"""
🏗️ Module Generator Agent
Generuje kompletny moduł szkoleniowy (kod, testy, dokumentacja, konfiguracja)
Z TrainingValueCritic - sprawdza wartość szkoleniową
"""

import os
from typing import Dict, Any, List, AsyncGenerator
from pydantic import BaseModel, Field

from google.adk.agents import LlmAgent, LoopAgent, BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.adk.agents.callback_context import CallbackContext

# Import TrainingValueCritic
from .training_value_critic import create_training_value_critic, TrainingValueCritique


# =============================================================================
# CALLBACK: Track Iteration
# =============================================================================

async def track_iteration(callback_context: CallbackContext):
    """Callback: Zlicza iteracje i dba o poprawne zmienne w stanie początkowym."""
    iteration = callback_context.state.get("iteration", 0) + 1
    callback_context.state["iteration"] = iteration

    # Zabezpieczenie przed błędem w pierwszej iteracji
    if "training_critique" not in callback_context.state:
        callback_context.state["training_critique"] = {
            "feedback": "To jest pierwsza iteracja. Brak uwag krytyka.",
            "is_approved": False,
            "score": 0.0
        }

    # NOWE: Reset licznika plików i obliczenie oczekiwanej liczby
    callback_context.state["files_created_count"] = 0

    # Pobierz liczbę oczekiwanych plików z execution_plan
    module_id = callback_context.state.get("module_id", 0)
    execution_plan = callback_context.state.get("execution_plan", {})
    modules = execution_plan.get("modules", [])

    files_expected = 0
    for module in modules:
        if module.get("module_id") == f"module{module_id}":
            # KRYTYCZNE: module.get("files") to int, a nie list!
            # Pobieramy liczbę plików bezpośrednio
            files_expected = module.get("files", 0)
            break

    callback_context.state["files_expected"] = files_expected

    print(f"\n{'='*80}")
    print(f"🔄 ITERACJA {iteration} - Moduł {module_id}")
    print(f"📊 Oczekiwane pliki: {files_expected}")
    print(f"{'='*80}\n")

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

def create_polyglot_code_agent(module_id: int, model="gemini-2.5-flash", tools=None, config=None):
    """Tworzy agenta generującego kod w różnych językach (Java/Python/React)"""

    # UWAGA: LlmAgent nie przyjmuje 'temperature' bezpośrednio w konstruktorze!
    # Używa domyślnych ustawień modelu (optymalne dla generowania kodu)

    instruction = f"""Jesteś programistą realizującym MODUŁ NR {module_id} z planu szkolenia GitHub Copilot Masterclass.

**KRYTYCZNE: TWÓJ MODUŁ TO module{module_id}!**
Nie wracaj do poprzednich modułów. Skup się WYŁĄCZNIE na module{module_id}.

**POPRZEDNIE MODUŁY (NIE DUPLIKUJ!):**
{{{{previous_modules_summary}}}}

Moduły wygenerowane wcześniej używały różnych domen i klas.
**KRYTYCZNE:** NIE używaj klas z poprzednich modułów!
Twoja domena: {{{{current_module_domain}}}}
Użyj NOWYCH klas specyficznych dla tej domeny!

**KONTEKST:**
1. Znajdź w 'execution_plan' moduł o module_id: "module{module_id}"
2. Zobacz pole 'files' - to LICZBA plików, którą musisz utworzyć
3. Wygeneruj około tej liczby sensownych plików (kod, configi, testy, README) potrzebnych dla tego modułu!
4. Wymyśl dla nich sensowną strukturę. UWAGA: Zgodnie z planem szkolenia, moduły 1-4 to "dzien-1", a moduły 5-8 to "dzien-2".
   Używaj ścieżek BEZ słowa 'output' na początku, np.: `dzien-1/modul-{module_id}/src/...` lub `dzien-2/modul-{module_id}/...`
5. Dla KAŻDEGO wymyślonego pliku:
   - Wygeneruj pełny kod (z TODO comments dla GitHub Copilot)
   - Wywołaj narzędzie 'create_file' z wymyśloną ścieżką i kodem

**FEEDBACK Z POPRZEDNIEJ ITERACJI (TrainingValueCritic):**
{{training_critique}}

Zignoruj powyższy feedback, jeśli to pierwsza iteracja.
Jeśli jest feedback - zastosuj się do niego rygorystycznie i popraw ćwiczenie.

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
5. **RÓŻNORODNOŚĆ DOMEN:** Każdy moduł = INNA domena biznesowa!
   - Moduł 1: E-commerce / Pirate Treasure Shop
   - Moduł 2: Banking / Financial Services
   - Moduł 3: Healthcare / Medical Records
   - Moduł 4: Logistics / Shipping & Delivery
   - Moduł 5: HR / Employee Management
   - Moduł 6: Real Estate / Property Management
   - Moduł 7: Education / Online Learning Platform
   - Moduł 8: Social Media / Content Platform

   **KRYTYCZNE:** NIE używaj klas z poprzednich modułów! Każdy moduł to NOWY projekt!

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

**ZADANIE (KRYTYCZNE!):**

**POD ŻADNYM POZOREM NIE WKLEJAJ GENEROWANEGO KODU DO TREŚCI SWOJEJ ODPOWIEDZI W CZACIE!**

Twoim JEDYNYM zadaniem jest użycie udostępnionego narzędzia `create_file` dla każdego pliku z listy.

**PROCEDURA:**
1. Znajdź w 'execution_plan' moduł o module_id: "module{module_id}"
2. Dla wymaganej LICZBY plików (pole 'files'):
   a) Wymyśl strukturę, cel i nazwę pliku (np. Controller, Service, DTO, README)
   b) Wygeneruj pełny kod (z TODO comments dla GitHub Copilot)
   c) Wywołaj narzędzie: create_file(path="dzien-X/modul-{module_id}/nazwa_pliku.ext", content=kod)
      UWAGA: Moduły 1-4 → dzien-1, Moduły 5-8 → dzien-2. NIE dodawaj słowa 'output' na początku!
   d) Przejdź do następnego pliku
3. Po zakończeniu napisz TYLKO krótkie podsumowanie. Pod żadnym pozorem nie wklejaj pełnego kodu w oknie czatu!

**PRZYKŁAD ODPOWIEDZI:**
"Utworzyłem 5 plików dla modułu {module_id}:
1. TreasureController.java
2. TreasureService.java
3. TreasureRepository.java
4. TreasureDTO.java
5. README.md"

**NIE wklejaj kodu do czatu! Używaj TYLKO narzędzia create_file!**
"""

    return LlmAgent(
        model=model,
        tools=tools,  # ← KLUCZOWE! Przekazujemy narzędzia (create_file, etc.)
        name=f"PolyglotCodeAgent_M{module_id}",  # ← Unikalna nazwa dla każdego modułu
        description=f"Generates code for module {module_id} (Java/Python/React) with TODO comments",
        instruction=instruction,
        output_key="generated_code",
        # temperature NIE jest dozwolony w LlmAgent (Pydantic extra='forbid')
        # Model używa domyślnych ustawień
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
    """Kontroler pętli - sprawdza czy ćwiczenie ma wartość szkoleniową (TrainingValueCritic)"""

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # Pobierz training_critique ze stanu
        training_critique = ctx.session.state.get("training_critique", {})
        is_approved = training_critique.get("is_approved", False)

        # NOWE: Sprawdź czy pliki faktycznie powstały na dysku
        module_id = ctx.session.state.get("module_id", 0)
        execution_plan = ctx.session.state.get("execution_plan", {})
        modules = execution_plan.get("modules", [])

        # KRYTYCZNE: Pobierz output_dir ze stanu (może być nadpisany przez --output-dir)
        base_dir = ctx.session.state.get("output_dir", "./output")

        files_expected = 0
        files_created_on_disk = 0

        for module in modules:
            if module.get("module_id") == f"module{module_id}":
                # KRYTYCZNE: module.get("files") to int, a nie list!
                files_expected = module.get("files", 0)

                # Sprawdź ile plików faktycznie istnieje na dysku dla tego modułu
                from pathlib import Path
                module_path_str = f"modul-{module_id}"

                for path in Path(base_dir).rglob('*'):
                    if path.is_file() and module_path_str in str(path):
                        files_created_on_disk += 1
                break

        if files_expected > 0 and files_created_on_disk == 0:
            # Agent nie wywołał narzędzia!
            print(f"[LoopController] ❌ Agent nie użył narzędzia create_file!")
            print(f"[LoopController] Oczekiwano: {files_expected} plików, utworzono: 0")
            print(f"[LoopController] Wymuszam powtórkę iteracji...")
            is_approved = False

            # Dodaj feedback do stanu
            ctx.session.state["training_critique"]["feedback"] = (
                f"KRYTYCZNY BŁĄD: Nie użyłeś narzędzia create_file! "
                f"Oczekiwano {files_expected} plików, utworzono 0. "
                f"Musisz wywołać create_file dla każdego pliku z listy!"
            )

        # Log dla debugowania
        iteration = ctx.session.state.get("iteration", 0)
        score = training_critique.get("score", 0.0)
        print(f"[LoopController] Iteracja: {iteration}, Training Score: {score}, "
              f"Files: {files_created_on_disk}/{files_expected}, Approved: {is_approved}")

        # Zwróć zdarzenie z akcją escalate
        yield Event(
            author=self.name,
            actions=EventActions(escalate=is_approved)
        )


# =============================================================================
# MODULE GENERATOR (LoopAgent)
# =============================================================================

def create_module_generator(module_id: int, model="gemini-2.5-flash", tools=None, config=None):
    """
    Tworzy generator modułu używając LoopAgent.

    Args:
        module_id: ID modułu (1-8)
        model: Model Gemini do użycia (string!)
        tools: Dict z narzędziami (file_operations, code_validator)
        config: Dict z konfiguracją z YAML (temperature, max_tokens, etc.)

    Returns:
        LoopAgent skonfigurowany do generowania modułu
    """

    # Tworzymy sub-agentów (polyglot - Java/Python/React)
    # KLUCZOWE: Przekazujemy module_id do agenta!
    polyglot_code_agent = create_polyglot_code_agent(
        module_id=module_id,
        model=model,
        tools=tools,
        config=config  # ← PRZEKAZUJEMY CONFIG!
    )

    # ZMIANA: TrainingValueCritic zamiast SyntaxCritic
    # Sprawdza wartość szkoleniową (czy uczy funkcji Copilota, czy nie ma przykładowych odpowiedzi, etc.)
    training_critic = create_training_value_critic(
        model=model,
        config=config  # ← PRZEKAZUJEMY CONFIG!
    )

    loop_controller = LoopController(name=f"LoopController_Module{module_id}")

    # Tworzymy LoopAgent z TrainingValueCritic
    return LoopAgent(
        name=f"ModuleGenerator_{module_id}",
        description=f"Generates module {module_id} with training value critique (Java/Python/React)",
        max_iterations=3,
        sub_agents=[polyglot_code_agent, training_critic, loop_controller]
    )

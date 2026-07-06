"""
Moduł 8: Loop Agent z Krytyką - "Pętla Perfekcjonisty"
=======================================================
Naucz się implementować iteracyjne udoskonalanie używając LoopAgent.

Temat: Pisarz Dziennika Okrętowego tworzy wpisy, Pierwszy Oficer
je krytykuje, a Kapitan decyduje czy są gotowe do dziennika.

Kluczowe Koncepcje:
- LoopAgent uruchamia sub_agents wielokrotnie aż do warunku wyjścia
- Niestandardowy BaseAgent do sprawdzania statusu i wyzwalania escalate
- output_schema dla ustrukturyzowanych decyzji
- max_iterations jako limit bezpieczeństwa
"""

import os
from typing import AsyncGenerator
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from google.adk.agents import LlmAgent, LoopAgent, BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.adk.agents.callback_context import CallbackContext

load_dotenv()

# Konfiguracja
MODEL = "gemini-2.5-flash"

# =============================================================================
# INICJALIZACJA STANU - Konfiguracja początkowego stanu dla pętli
# =============================================================================

async def init_loop_state(callback_context: CallbackContext):
    """Inicjalizuj stan przed rozpoczęciem pętli."""
    callback_context.state["log_entry"] = "Jeszcze nie napisany"
    callback_context.state["critique"] = "Jeszcze brak krytyki"
    callback_context.state["entry_status"] = {"decision": "invalid"}
    return None

# =============================================================================
# SCHEMAT USTRUKTURYZOWANEGO WYJŚCIA - Dla decyzji Kapitana
# =============================================================================

class EntryDecision(BaseModel):
    """Schemat struktury decyzji dotyczącej wpisu do dziennika."""
    decision: str = Field(description="Albo 'valid' albo 'invalid'")
    reason: str = Field(description="Krótkie wyjaśnienie decyzji")

# =============================================================================
# AGENT 1: PISARZ DZIENNIKA - Tworzy wpis do dziennika okrętowego
# =============================================================================

log_writer = LlmAgent(
    model=MODEL,
    name="pisarz_dziennika",
    instruction="""Jesteś PISARZEM DZIENNIKA OKRĘTOWEGO!

Twój obowiązek: napisz odpowiedni wpis do dziennika dla Kapitana.

Poprzedni szkic (jeśli jest): {log_entry}
Krytyka do uwzględnienia: {critique}

Wymagania dla odpowiedniego wpisu dziennika:
- Data i warunki pogodowe
- Pozycja i kurs
- Znaczące wydarzenia dnia
- Status załogi i morale
- Aktualizacja inwentarza zapasów

Jeśli pojawia się krytyka, uwzględnij ją w nowej wersji wpisu.
Zachowaj styl żeglarsko‑piracki w opisie zdarzeń.
""",
    description="Tworzy i udoskonala wpisy do dziennika okrętowego",
    output_key="log_entry",
    before_agent_callback=init_loop_state
)

# =============================================================================
# AGENT 2: FIRST MATE CRITIC - Reviews the log entry
# =============================================================================

first_mate = LlmAgent(
    model=MODEL,
    name="first_mate",
    instruction="""Jesteś PIERWSZYM OFICEREM – krytycznym okiem Kapitana!

Oceń poniższy wpis do dziennika:
{log_entry}

Sprawdź w szczególności:
1. Czy użyto odpowiedniej terminologii żeglarskiej
2. Czy zawarte są wszystkie wymagane sekcje
3. Czy ton jest profesjonalny i spójny z charakterem dziennika
4. Czy opis jest dokładny i kompletny
5. Czy styl jest konsekwentny

Podaj konkretną, konstruktywną krytykę.
Jeśli wpis nie wymaga żadnych poprawek, napisz wyraźnie:
"No improvements needed".
""",
    description="Dostarcza konstruktywnej krytyki wpisów do dziennika",
    output_key="critique"
)

# =============================================================================
# AGENT 3: CAPTAIN DECISION - Approves or rejects
# =============================================================================

captain = LlmAgent(
    model=MODEL,
    name="captain",
    instruction="""Jesteś KAPITANEM – ostatecznym arbitrem wpisów do dziennika!

Wpis do dziennika:
{log_entry}

Krytyka Pierwszego Oficera:
{critique}

Podejmij decyzję:
- Jeśli Pierwszy Oficer nie znalazł problemów → decision: "valid"
- Jeśli są istotne zastrzeżenia → decision: "invalid"

Bądź zdecydowany – załoga czeka na Twój werdykt.
""",
    description="Podejmuje ostateczną decyzję o jakości wpisu do dziennika",
    output_key="entry_status",
    output_schema=EntryDecision
)

# =============================================================================
# CUSTOM AGENT: LOOP CONTROLLER - Checks status and escalates
# =============================================================================

class CheckStatusAndEscalate(BaseAgent):
    """Niestandardowy agent, który sprawdza status i kończy pętlę, gdy wpis
    zostanie zaakceptowany.
    """

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        # Pobierz decyzję Kapitana ze stanu
        status = ctx.session.state.get("entry_status", {})
        decision = status.get("decision", "invalid")

        # Czy powinniśmy zakończyć pętlę?
        should_stop = (decision == "valid")

        # Log dla celów debugowania
        print(f"[Loop Controller] Decyzja: {decision}, Zatrzymanie: {should_stop}")

        # Zwróć zdarzenie z akcją escalate, aby wyjść z pętli
        yield Event(
            author=self.name,
            actions=EventActions(escalate=should_stop)
        )

# =============================================================================
# LOOP AGENT - Iterates until valid or max iterations
# =============================================================================

root_agent = LoopAgent(
    name="log_refinement_loop",
    description="Iteracyjnie udoskonala wpis do dziennika, aż Kapitan go zatwierdzi",
    max_iterations=5,
    sub_agents=[
        log_writer,
        first_mate,
        captain,
        CheckStatusAndEscalate(name="loop_controller")
    ]
)


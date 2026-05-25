"""
Moduł 8: Loop Critique - ROZWIĄZANIA ĆWICZEŃ (Zaktualizowane dla ADK v1.0+)
==========================================================================
Usunięto zmienne {input} i {user_query}. Model odczyta polecenie użytkownika
bezpośrednio z historii konwersacji czatu.
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
MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")

# =============================================================================
# WSPÓLNE KOMPONENTY STERUJĄCE PĘTLĄ
# =============================================================================

async def track_iteration(callback_context: CallbackContext):
    """Callback: Zlicza iteracje i dba o poprawne zmienne w stanie początkowym."""
    iteration = callback_context.state.get("iteration", 0) + 1
    callback_context.state["iteration"] = iteration

    # Zabezpieczenie przed błędem w pierwszej iteracji
    if "critique" not in callback_context.state:
        callback_context.state["critique"] = "To jest pierwsza iteracja. Brak uwag krytyka."

    return None

class CritiqueResult(BaseModel):
    """Ustrukturyzowany format oceny krytyka."""
    score: float = Field(description="Średnia ocena od 1.0 do 10.0")
    feedback: str = Field(description="Szczegółowa krytyka, co poprawić")
    is_approved: bool = Field(description="Zwróć True, jeśli treść jest wystarczająco dobra (np. score >= 8.0) i można zakończyć, w przeciwnym razie False")

class LoopController(BaseAgent):
    """Agent kontrolujący: odczytuje decyzję i ewentualnie przerywa pętlę."""
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        critique = ctx.session.state.get("critique", {})
        is_approved = critique.get("is_approved", False)
        iteration = ctx.session.state.get("iteration", 1)

        print(f"[Loop Controller] Iteracja: {iteration} | Zatwierdzone: {is_approved}")

        yield Event(
            author=self.name,
            actions=EventActions(escalate=is_approved)
        )

def create_loop_controller(suffix: str):
    return LoopController(name=f"kontroler_petli_{suffix}")

# =============================================================================
# BAZOWY PISARZ (FABRYKA)
# =============================================================================

WRITER_INSTRUCTION = """Jesteś kreatywnym copywriterem. Otrzymasz zadanie od użytkownika.

**FEEDBACK Z POPRZEDNIEJ ITERACJI:**
{critique}

Zignoruj powyższy feedback, jeśli to pierwsza iteracja.
Jeśli jest feedback - zastosuj się do niego rygorystycznie i popraw tekst.

Twoja treść powinna być:
- Angażująca i przekonująca
- Zgodna z tonem marki
- Wolna od błędów

Podaj TYLKO gotową treść (bez meta-komentarzy)."""

def create_writer(suffix: str):
    return LlmAgent(
        model=MODEL,
        name=f"pisarz_{suffix}",
        description="Tworzy i ulepsza treści marketingowe.",
        instruction=WRITER_INSTRUCTION,
        output_key="draft",
        before_agent_callback=track_iteration
    )

# =============================================================================
# ĆWICZENIE 1 & 2: max_iterations=5 oraz PRÓG JAKOŚCI (>8/10)
# =============================================================================

general_critic = LlmAgent(
    model=MODEL,
    name="krytyk_ogolny",
    description="Ocenia ogólną treść, z progiem 8/10.",
    instruction="""Oceń treść napisaną przez copywritera:
{draft}

KRYTERIA (każde od 1-10):
1. Jasność przekazu
2. Angażowanie czytelnika
3. Poprawność gramatyczna
4. Estetyka tekstu

Wymagany próg akceptacji (is_approved) wynosi minimum 8.0/10 średniej oceny.
""",
    output_key="critique",
    output_schema=CritiqueResult
)

loop_5_iterations_with_threshold = LoopAgent(
    name="petla_5_iteracji_z_progiem",
    sub_agents=[create_writer("ogolny"), general_critic, create_loop_controller("ogolny")],
    max_iterations=5
)

# =============================================================================
# ĆWICZENIE 3: RÓŻNE KRYTERIA DLA RÓŻNYCH TYPÓW TREŚCI
# =============================================================================

blog_critic = LlmAgent(
    model=MODEL,
    name="krytyk_bloga",
    instruction="""Oceń artykuł blogowy:
{draft}

KRYTERIA DLA BLOGA (oceniasz od 1 do 10):
1. Optymalizacja SEO (słowa kluczowe, nagłówki)
2. Wartość edukacyjna dla czytelnika
3. Poprawna struktura (wstęp, rozwinięcie, zakończenie)
4. Call-to-action (Wezwanie do akcji) na końcu

Aby ustawić `is_approved` na True, średnia musi wynosić minimum 8.0/10.
Zwróć wynik w wymaganym formacie strukturalnym.
""",
    output_key="critique",
    output_schema=CritiqueResult
)

social_media_critic = LlmAgent(
    model=MODEL,
    name="krytyk_social_media",
    instruction="""Oceń post social media:
{draft}

KRYTERIA DLA SOCIAL MEDIA (oceniasz od 1 do 10):
1. Zwięzłość (krótko i na temat)
2. Hook (czy pierwsze słowa przyciągają uwagę?)
3. Użycie Emoji i formatowanie tekstowe
4. Odpowiednie Hashtagi (nie za dużo, precyzyjne)

Aby ustawić `is_approved` na True, średnia musi wynosić minimum 8.0/10.
Zwróć wynik w wymaganym formacie strukturalnym.
""",
    output_key="critique",
    output_schema=CritiqueResult
)

email_critic = LlmAgent(
    model=MODEL,
    name="krytyk_emaili",
    instruction="""Oceń email marketingowy:
{draft}

KRYTERIA DLA EMAILA (oceniasz od 1 do 10):
1. Temat (czy zachęca do otwarcia?)
2. Personalizacja
3. Wartość dla odbiorcy
4. Jasny i klikalny CTA

Aby ustawić `is_approved` na True, średnia musi wynosić minimum 8.0/10.
Zwróć wynik w wymaganym formacie strukturalnym.
""",
    output_key="critique",
    output_schema=CritiqueResult
)

# Pętle przypisane do odpowiednich krytyków z unikalnymi instancjami pisarzy
loop_blog = LoopAgent(
    name="petla_blog",
    sub_agents=[create_writer("blog"), blog_critic, create_loop_controller("blog")],
    max_iterations=5
)

loop_social = LoopAgent(
    name="petla_social_media",
    sub_agents=[create_writer("social"), social_media_critic, create_loop_controller("social")],
    max_iterations=5
)

loop_email = LoopAgent(
    name="petla_email",
    sub_agents=[create_writer("email"), email_critic, create_loop_controller("email")],
    max_iterations=5
)

# =============================================================================
# AGENT GŁÓWNY - Wybierz rozwiązanie
# =============================================================================

#root_agent = loop_5_iterations_with_threshold # Ćwiczenie 1 i 2 połączone
root_agent = loop_blog                      # Ćwiczenie 3 - blog
# root_agent = loop_social                    # Ćwiczenie 3 - social media
# root_agent = loop_email                     # Ćwiczenie 3 - email
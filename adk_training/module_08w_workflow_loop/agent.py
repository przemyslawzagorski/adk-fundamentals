"""
Moduł 8W: Workflow (ADK 2) - Pętla krytyki jako graf
====================================================

Ta sama "Pętla Perfekcjonisty" co w Module 8 (Pisarz -> Pierwszy Oficer ->
Kapitan), ale bez LoopAgent i bez własnego BaseAgent z `escalate`.

Kluczowe Koncepcje:
- PĘTLA = krawędź routingu, która wskazuje na WCZEŚNIEJSZY węzeł
- Router to zwykła funkcja: `yield Event(route="nazwa")`
- `edges=[(router, {"popraw": pisarz, "gotowe": zapisz})]` - mapowanie tras
- Agent z `output_schema` zwraca obiekt Pydantic -> trafia do routera jako node_input
- Limit iteracji trzymamy w stanie (zamiast max_iterations z LoopAgent)

Graf:
    START -> start_petli -> pisarz -> pierwszy_oficer -> kapitan -> decyzja
                               ^                                      |
                               +---------- "popraw" ------------------+
                                                                      | "gotowe"
                                                                      v
                                                              zapisz_w_dzienniku
"""

import os
from typing import Literal

from dotenv import load_dotenv
from google.adk import Agent, Context, Event, Workflow
from pydantic import BaseModel, Field

load_dotenv()

MODEL = os.getenv("ADK_MODEL", "gemini-3.5-flash")
MAX_ITERACJI = 3


class DecyzjaWpisu(BaseModel):
    reason: str = Field(description="Krótkie uzasadnienie decyzji")
    decision: Literal["valid", "invalid"] = Field(
        description="'valid' gdy wpis gotowy, 'invalid' gdy wymaga poprawek"
    )


def start_petli(node_input: str):
    yield Event(state={
        "wydarzenia_dnia": node_input,
        "wpis": "",
        "krytyka": "",
        "iteracja": 0,
    })


pisarz = Agent(
    name="pisarz_dziennika",
    model=MODEL,
    instruction="""Jesteś PISARZEM DZIENNIKA OKRĘTOWEGO.

Wydarzenia dnia od Kapitana: "{wydarzenia_dnia}"
Poprzedni szkic (może być pusty): {wpis?}
Krytyka do uwzględnienia (może być pusta): {krytyka?}

Napisz wpis do dziennika: data i pogoda, pozycja i kurs, wydarzenia,
stan załogi, zapasy. Styl żeglarsko-piracki, maksymalnie 12 zdań.
Jeśli jest krytyka - popraw dokładnie wskazane rzeczy.""",
    output_key="wpis",
)

pierwszy_oficer = Agent(
    name="pierwszy_oficer",
    model=MODEL,
    instruction="""Jesteś PIERWSZYM OFICEREM - krytycznym okiem Kapitana.

Oceń wpis:
{wpis}

Sprawdź: terminologię żeglarską, komplet sekcji (data/pogoda, pozycja,
wydarzenia, załoga, zapasy), spójność stylu.
Podaj maksymalnie 3 konkretne uwagi.
Jeśli wpis jest kompletny, napisz dokładnie: "No improvements needed".""",
    output_key="krytyka",
)

kapitan = Agent(
    name="kapitan",
    model=MODEL,
    instruction="""Jesteś KAPITANEM. Zdecyduj, czy wpis trafia do dziennika.

WPIS:
{wpis}

KRYTYKA PIERWSZEGO OFICERA:
{krytyka}

Jeśli krytyka to "No improvements needed" lub uwagi są kosmetyczne -> valid.
W przeciwnym razie -> invalid.""",
    output_schema=DecyzjaWpisu,
    output_key="decyzja",
)


def decyzja(ctx: Context, node_input: DecyzjaWpisu):
    iteracja = ctx.state.get("iteracja", 0) + 1
    if node_input.decision == "valid" or iteracja >= MAX_ITERACJI:
        yield Event(
            route="gotowe",
            state={"iteracja": iteracja},
            message=f"🧭 Iteracja {iteracja}: koniec pętli ({node_input.decision}).",
        )
    else:
        yield Event(
            route="popraw",
            state={"iteracja": iteracja},
            message=f"🔁 Iteracja {iteracja}: poprawka - {node_input.reason}",
        )


def zapisz_w_dzienniku(wpis: str, iteracja: int):
    yield Event(message=f"📜 WPIS ZATWIERDZONY (iteracji: {iteracja}):\n\n{wpis}")


# =============================================================================
# ĆWICZENIA
# =============================================================================
# ĆWICZENIE 8W.1: Kapitan-człowiek (Human-in-the-loop)
#   Przed `zapisz_w_dzienniku` dodaj węzeł, który pyta CZŁOWIEKA o akceptację:
#       from google.adk.events import RequestInput
#       def akceptacja_kapitana(wpis: str):
#           yield RequestInput(message=f"Zatwierdzasz wpis? (tak / uwagi)\n\n{wpis}")
#   Odpowiedź człowieka trafia do NASTĘPNEGO węzła jako node_input (str).
#   Napisz router: "tak" -> zapisz_w_dzienniku, inna odpowiedź -> zapisz ją
#   jako "krytyka" w stanie i wróć do `pisarz`.
#
# ĆWICZENIE 8W.2: Tańsza decyzja bez LLM
#   Zastąp agenta `kapitan` funkcją, która sama sprawdza, czy w {krytyka}
#   jest "No improvements needed". Ile wywołań modelu oszczędzasz na iterację?
#
# Rozwiązanie: agent_solution.py

root_agent = Workflow(
    name="petla_dziennika_v2",
    edges=[
        ("START", start_petli, pisarz, pierwszy_oficer, kapitan, decyzja),
        (decyzja, {"popraw": pisarz, "gotowe": zapisz_w_dzienniku}),
    ],
)

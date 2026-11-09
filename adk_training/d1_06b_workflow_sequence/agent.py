"""
Moduł 4W - ROZWIĄZANIE ćwiczeń 4W.1 i 4W.2
==========================================

Łańcuch: przyjmij_rozkaz -> zwiadowca -> strateg -> ocen_ryzyko -> kwatermistrz -> kapitan

- 4W.1: `ocen_ryzyko` to funkcja-węzeł (bez LLM). Parametr `plan_bitwy`
  jest wstrzykiwany ze stanu po nazwie (zapisał go strateg przez output_key).
- 4W.2: `kwatermistrz` to kolejny Agent; wynik trafia do stanu jako
  `lista_zapasow` i jest czytany przez Kapitana jako {lista_zapasow}.

Uruchomienie: wpisz do pustego `__init__.py` linię
`from .agent_solution import root_agent` i zrestartuj `adk web`
(loader ADK szuka `root_agent` najpierw w pakiecie, potem w `agent.py`).
"""

import os
import re

from dotenv import load_dotenv
from google.adk import Agent, Event, Workflow

load_dotenv()

MODEL = os.getenv("ADK_MODEL", "gemini-3.5-flash-lite")


def przyjmij_rozkaz(node_input: str):
    yield Event(state={"cel": node_input})


zwiadowca = Agent(
    name="zwiadowca",
    model=MODEL,
    instruction="""Jesteś Zwiadowcą floty. Cel rozkazu Kapitana: "{cel}"

Zbierz wywiad o celu (port, statek, wyspa lub skarb):
1. Lokalizacja i teren
2. Obrona (straże, działa, patrole)
3. Kosztowności do zdobycia
4. Ryzyka (pogoda, marynarka)
5. Najlepsze okno czasowe

Bądź zwięzły. Zakończ oceną pewności (1-10).""",
    output_key="raport_wywiadu",
)

strateg = Agent(
    name="strateg",
    model=MODEL,
    instruction="""Jesteś Strategiem floty.

RAPORT WYWIADU:
{raport_wywiadu}

Stwórz plan rajdu: podejście, timing, przydział załogi, plan awaryjny,
droga ucieczki, oczekiwany łup.

Ostatnia linia MUSI mieć format: RYZYKO: Niskie | Średnie | Wysokie""",
    output_key="plan_bitwy",
)


# ĆWICZENIE 4W.1 - deterministyczny krok: parsowanie zamiast kolejnego wywołania LLM
def ocen_ryzyko(plan_bitwy: str):
    match = re.search(r"RYZYKO:\s*\**\s*(Niskie|Średnie|Wysokie)", plan_bitwy, re.IGNORECASE)
    poziom = match.group(1).capitalize() if match else "Nieznane"
    yield Event(
        message=f"⚖️ Poziom ryzyka: {poziom}",
        state={"poziom_ryzyka": poziom},
    )


# ĆWICZENIE 4W.2 - nowy agent w łańcuchu
kwatermistrz = Agent(
    name="kwatermistrz",
    model=MODEL,
    instruction="""Jesteś Kwatermistrzem floty.

PLAN RAJDU:
{plan_bitwy}

Wylicz zapasy potrzebne na ten rajd jako krótką listę z ilościami:
proch, rum, prowiant, łodzie (i inne, jeśli plan ich wymaga).
Bez komentarzy - tylko lista.""",
    output_key="lista_zapasow",
)

kapitan = Agent(
    name="kapitan",
    model=MODEL,
    instruction="""Jesteś Kapitanem. Podejmij ostateczną decyzję.

WYWIAD:
{raport_wywiadu}

PLAN:
{plan_bitwy}

POZIOM RYZYKA (wyliczony automatycznie): {poziom_ryzyka}

ZAPASY OD KWATERMISTRZA:
{lista_zapasow}

Jeśli ryzyko jest Wysokie, a zapasy niewystarczające - odrzuć lub zatwierdź warunkowo.
Werdykt: ZATWIERDZONY / ZATWIERDZONY WARUNKOWO / ODRZUCONY (z uzasadnieniem).
Zakończ krótką mową do załogi (2-3 zdania).""",
    output_key="decyzja_kapitana",
)

root_agent = Workflow(
    name="pipeline_rajdu_v2_solution",
    edges=[("START", przyjmij_rozkaz, zwiadowca, strateg, ocen_ryzyko, kwatermistrz, kapitan)],
)

"""
Moduł 4W: Workflow (ADK 2) - Sekwencja jako graf
================================================

Ten sam rajd co w Module 4 (Zwiadowca -> Strateg -> Kapitan), ale zbudowany
na nowym prymitywie ADK 2: `Workflow(edges=[...])`.

Kluczowe Koncepcje:
- `Workflow` zastępuje SequentialAgent (który w ADK 2 jest oznaczony jako deprecated)
- Krotka w `edges` = sekwencja: ("START", a, b, c) -> a, potem b, potem c
- Węzłem może być Agent ALBO zwykła funkcja Pythona (deterministyczny krok bez LLM)
- Funkcja-węzeł zapisuje dane do stanu przez `yield Event(state={...})`
- Agent zapisuje wynik do stanu przez `output_key`, a czyta przez `{klucz}` w instrukcji

Porównaj z Modułem 4: tam nie dało się wstawić "zwykłego kodu" między agentów
bez pisania własnego BaseAgent. Tutaj to jedna funkcja.
"""

import os

from dotenv import load_dotenv
from google.adk import Agent, Event, Workflow

load_dotenv()

MODEL = os.getenv("ADK_MODEL", "gemini-3.5-flash-lite")


# =============================================================================
# WĘZEŁ 0: FUNKCJA - przyjmuje rozkaz Kapitana (bez LLM)
# =============================================================================
# `node_input` to wiadomość użytkownika. Zapisujemy ją w stanie jako "cel",
# żeby każdy kolejny agent mógł się do niej odwołać przez {cel}.

def przyjmij_rozkaz(node_input: str):
    yield Event(state={"cel": node_input})


# =============================================================================
# WĘZEŁ 1: ZWIADOWCA
# =============================================================================

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


# =============================================================================
# WĘZEŁ 2: STRATEG
# =============================================================================

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


# =============================================================================
# WĘZEŁ 3: KAPITAN
# =============================================================================

kapitan = Agent(
    name="kapitan",
    model=MODEL,
    instruction="""Jesteś Kapitanem. Podejmij ostateczną decyzję.

WYWIAD:
{raport_wywiadu}

PLAN:
{plan_bitwy}

Werdykt: ZATWIERDZONY / ZATWIERDZONY WARUNKOWO / ODRZUCONY (z uzasadnieniem).
Zakończ krótką mową do załogi (2-3 zdania).""",
    output_key="decyzja_kapitana",
)


# =============================================================================
# ĆWICZENIA
# =============================================================================
# ĆWICZENIE 4W.1: Deterministyczny krok między agentami
#   Napisz funkcję `ocen_ryzyko(plan_bitwy: str)`, która:
#   - odczyta z planu ostatnią linię "RYZYKO: ..."
#   - zapisze do stanu {"poziom_ryzyka": "Niskie|Średnie|Wysokie"}
#   - wyśle komunikat: yield Event(message=f"⚖️ Poziom ryzyka: ...")
#   Wstaw ją w edges między `strateg` a `kapitan` i użyj {poziom_ryzyka}
#   w instrukcji Kapitana.
#   Podpowiedź: parametry funkcji-węzła są wstrzykiwane ze stanu po nazwie.
#
# ĆWICZENIE 4W.2: Nowy agent w łańcuchu
#   Dodaj agenta `kwatermistrz` (output_key="lista_zapasow"), który na podstawie
#   {plan_bitwy} wylicza zapasy na rajd (proch, rum, prowiant, łodzie).
#   Wstaw go przed Kapitanem i przekaż {lista_zapasow} do instrukcji Kapitana.
#
# Rozwiązanie: agent_solution.py

root_agent = Workflow(
    name="pipeline_rajdu_v2",
    edges=[("START", przyjmij_rozkaz, zwiadowca, strateg, kapitan)],
)

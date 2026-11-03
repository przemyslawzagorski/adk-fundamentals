"""
Moduł 7W: Workflow (ADK 2) - Równoległość: fan-out / fan-in
===========================================================

Ta sama "Rada Załogi" co w Module 7 (trzech zwiadowców + Szpiegmistrz),
ale zbudowana na `Workflow` zamiast ParallelAgent + SequentialAgent.

Kluczowe Koncepcje:
- FAN-OUT: krotka węzłów w edges -> (a, b, c) uruchamia je RÓWNOLEGLE
- FAN-IN: `JoinNode` czeka, aż wszystkie równoległe gałęzie skończą
- Wynik JoinNode to słownik {nazwa_węzła: wynik}
- Każdy zwiadowca nadal zapisuje swój raport do stanu przez `output_key`

Graf:
    START -> przyjmij_rozkaz -> (północny, południowy, wschodni) -> zbiorka -> szpiegmistrz
"""

import os

from dotenv import load_dotenv
from google.adk import Agent, Event, Workflow
from google.adk.workflow import JoinNode

load_dotenv()

MODEL = os.getenv("ADK_MODEL", "gemini-3.5-flash")


def przyjmij_rozkaz(node_input: str):
    yield Event(state={"rozkaz": node_input})


def _zwiadowca(kierunek: str, cele: str, output_key: str) -> Agent:
    return Agent(
        name=f"zwiadowca_{kierunek}",
        model=MODEL,
        instruction=f"""Jesteś zwiadowcą sektora {kierunek.upper()}.
Rozkaz Kapitana: "{{rozkaz}}"

Zbadaj swój sektor pod kątem: {cele}.
Maksymalnie 5 punktów. Zakończ: "Zwiadowca {kierunek} raportuje!" """,
        output_key=output_key,
    )


zwiadowca_polnocny = _zwiadowca(
    "polnocny", "wrogich okrętów, statków handlowych, fortyfikacji", "raport_polnocny"
)
zwiadowca_poludniowy = _zwiadowca(
    "poludniowy", "ukrytych zatoczek, konwojów kupieckich, patroli marynarki", "raport_poludniowy"
)
zwiadowca_wschodni = _zwiadowca(
    "wschodni", "miast portowych, flot rybackich, nadciągających sztormów", "raport_wschodni"
)

# FAN-IN: czeka na wszystkie gałęzie wchodzące do tego węzła
zbiorka = JoinNode(name="zbiorka_raportow")

szpiegmistrz = Agent(
    name="szpiegmistrz",
    model=MODEL,
    instruction="""Jesteś Szpiegmistrzem. Zwiadowcy wrócili z raportami.

PÓŁNOC:
{raport_polnocny}

POŁUDNIE:
{raport_poludniowy}

WSCHÓD:
{raport_wschodni}

1. Zsyntetyzuj wywiad w jeden briefing
2. Wskaż najbardziej obiecującą okazję
3. Oznacz sprzeczności i zagrożenia
4. Zarekomenduj następny ruch Kapitana""",
    output_key="briefing_wywiadowczy",
)


# =============================================================================
# ĆWICZENIA
# =============================================================================
# ĆWICZENIE 7W.1: Czwarty kierunek
#   Dodaj `zwiadowca_zachodni` (output_key="raport_zachodni") do krotki fan-out
#   i do instrukcji Szpiegmistrza. Zauważ: nic poza edges nie trzeba zmieniać,
#   żeby uruchamiał się równolegle.
#
# ĆWICZENIE 7W.2: Deterministyczna agregacja zamiast LLM
#   Napisz funkcję `podsumuj_zbiorke(node_input: dict)`, która dostaje wynik
#   JoinNode (słownik {nazwa_zwiadowcy: raport}) i wysyła
#   yield Event(message="📋 Raporty: ... (liczba znaków każdego raportu)").
#   Wstaw ją między `zbiorka` a `szpiegmistrz`.
#   Wypisz klucze słownika - to nazwy węzłów, nie output_key!
#
# Rozwiązanie: agent_solution.py

root_agent = Workflow(
    name="rada_zalogi_v2",
    edges=[
        (
            "START",
            przyjmij_rozkaz,
            (zwiadowca_polnocny, zwiadowca_poludniowy, zwiadowca_wschodni),
            zbiorka,
            szpiegmistrz,
        ),
    ],
)

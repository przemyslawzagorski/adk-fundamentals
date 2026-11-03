"""
Moduł 33: Task API (ADK 2) - Zespół agentów z trybami pracy
===========================================================

Kapitan Portu przygotowuje statek do rejsu i deleguje zadania podwładnym.
Nowość ADK 2: każdy sub-agent dostaje TRYB PRACY (`mode`):

| mode            | Rozmowa z użytkownikiem       | Powrót do koordynatora          |
|-----------------|-------------------------------|---------------------------------|
| "chat" (domyśl.)| pełna, swobodna               | ręcznie (transfer_to_agent)     |
| "task"          | tylko pytania doprecyzowujące | AUTOMATYCZNIE po finish_task    |
| "single_turn"   | brak                          | AUTOMATYCZNIE z wynikiem        |

Kluczowe Koncepcje:
- Koordynator dostaje automatycznie narzędzia delegujące nazwane jak sub-agenci
- `mode="task"` + `output_schema` -> sub-agent dopytuje usera, a potem ZWRACA
  ustrukturyzowany wynik do koordynatora (bez ręcznego transferu)
- `mode="single_turn"` -> zadanie "w tle", bez rozmowy, może działać równolegle
- Agent w trybie task musi być liściem (bez własnych sub_agents)
- Root agent NIE ustawia `mode`

Porównaj z Modułem 12 (router): tam sub-agent przejmował rozmowę i trzeba było
pilnować, kiedy oddaje kontrolę. Tutaj powrót jest automatyczny.
"""

import os

from dotenv import load_dotenv
from google.adk import Agent
from pydantic import BaseModel, Field

load_dotenv()

MODEL = os.getenv("ADK_MODEL", "gemini-3.5-flash")


# =============================================================================
# SCHEMATY DANYCH
# =============================================================================

class PozycjaZapasow(BaseModel):
    towar: str = Field(description="Jeden z: rum, suchary, woda, proch, kule armatnie")
    beczki: int = Field(description="Liczba beczek / skrzyń")


class ListaZapasow(BaseModel):
    pozycje: list[PozycjaZapasow]


# =============================================================================
# NARZĘDZIA
# =============================================================================

def sprawdz_pogode(port_docelowy: str) -> dict:
    """Zwraca prognozę pogody na trasie do portu docelowego."""
    prognozy = {
        "tortuga": {"wiatr": "pomyślny, 15 węzłów", "sztorm": False, "dni_rejsu": 4},
        "port royal": {"wiatr": "zmienny, 8 węzłów", "sztorm": False, "dni_rejsu": 6},
        "nassau": {"wiatr": "silny, 30 węzłów", "sztorm": True, "dni_rejsu": 9},
    }
    return prognozy.get(
        port_docelowy.lower(), {"wiatr": "nieznany", "sztorm": False, "dni_rejsu": 7}
    )


def zaladuj_statek(port_docelowy: str, pozycje: list[PozycjaZapasow]) -> str:
    """Ładuje zapasy na statek i wyznacza kurs do portu docelowego."""
    razem = sum(p.beczki for p in pozycje)
    return f"⚓ Załadowano {razem} beczek/skrzyń. Kurs na {port_docelowy} wyznaczony!"


# =============================================================================
# SUB-AGENT 1: KWATERMISTRZ (mode="task") - rozmawia z userem, potem wraca
# =============================================================================

kwatermistrz = Agent(
    name="kwatermistrz",
    model=MODEL,
    mode="task",
    output_schema=ListaZapasow,
    description="Zbiera od Kapitana listę zapasów na rejs.",
    instruction="""Jesteś Kwatermistrzem. Magazyn ma TYLKO: rum, suchary, woda,
proch, kule armatnie. Niczego innego nie oferuj.

Zapytaj Kapitana, co i ile beczek załadować. Dopytuj tylko, jeśli czegoś brakuje.
Gdy masz kompletną listę - zakończ zadanie.""",
)


# =============================================================================
# SUB-AGENT 2: NAWIGATOR (mode="single_turn") - bez rozmowy, tylko wynik
# =============================================================================

nawigator = Agent(
    name="nawigator",
    model=MODEL,
    mode="single_turn",
    description="Sprawdza pogodę i długość rejsu do wskazanego portu.",
    instruction="""Jesteś Nawigatorem. Użyj narzędzia sprawdz_pogode dla podanego
portu i zwróć krótki raport: wiatr, ryzyko sztormu, liczba dni rejsu.""",
    tools=[sprawdz_pogode],
)


# =============================================================================
# ĆWICZENIA
# =============================================================================
# ĆWICZENIE 33.1: Skarbnik w trybie single_turn
#   Dodaj agenta `skarbnik` (mode="single_turn") z narzędziem
#   `wycen_zapasy(pozycje: list[PozycjaZapasow]) -> dict` (np. rum 12 dublonów
#   za beczkę, proch 20, reszta 5). Dodaj go do sub_agents i każ Kapitanowi
#   Portu podać koszt PRZED załadunkiem.
#
# ĆWICZENIE 33.2: Obserwacja trybów w adk web
#   W zakładce Events sprawdź:
#   - kiedy kwatermistrz zadaje pytania, a kiedy oddaje wynik (finish_task)
#   - że nawigator NIE pisze do użytkownika, tylko zwraca wynik koordynatorowi
#   Zmień nawigatorowi mode na "task" i porównaj zachowanie.
#
# Rozwiązanie: agent_solution.py


# =============================================================================
# KOORDYNATOR (root) - BEZ mode
# =============================================================================

root_agent = Agent(
    name="kapitan_portu",
    model=MODEL,
    instruction="""Jesteś Kapitanem Portu. Przygotowujesz statek do rejsu.

1. Ustal z użytkownikiem port docelowy (Tortuga, Port Royal lub Nassau).
2. Zleć Nawigatorowi sprawdzenie pogody na trasie.
3. Zleć Kwatermistrzowi zebranie listy zapasów.
4. Gdy masz oba wyniki - użyj zaladuj_statek i podsumuj rejs.
Przy sztormie ostrzeż załogę i zasugeruj więcej wody i sucharów.""",
    sub_agents=[kwatermistrz, nawigator],
    tools=[zaladuj_statek],
)

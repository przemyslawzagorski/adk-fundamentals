"""
Moduł 33: Task API (ADK 2) — Koordynator i zespół agentów
=========================================================
"""

import os
from typing import Any
from dotenv import load_dotenv
from google.adk import Agent
from pydantic import BaseModel, Field

load_dotenv()
MODEL = os.getenv("ADK_MODEL", "gemini-3.5-flash-lite")


# =============================================================================
# SCHEMATY DANYCH
# =============================================================================

class PozycjaZapasow(BaseModel):
    towar: str = Field(description="Jeden z: rum, suchary, woda, proch, kule armatnie")
    beczki: int = Field(description="Liczba beczek lub skrzyń")


class ListaZapasow(BaseModel):
    pozycje: list[PozycjaZapasow]


# =============================================================================
# NARZĘDZIA
# =============================================================================

def sprawdz_pogode(port_docelowy: str) -> dict[str, Any]:
    """Zwraca prognozę pogody na trasie do portu docelowego."""
    prognozy = {
        "tortuga": {"wiatr": "pomyślny, 15 węzłów", "sztorm": False, "dni_rejsu": 4},
        "port royal": {"wiatr": "zmienny, 8 węzłów", "sztorm": False, "dni_rejsu": 6},
        "nassau": {"wiatr": "silny, 30 węzłów", "sztorm": True, "dni_rejsu": 9},
    }
    return prognozy.get(
        port_docelowy.lower(), {"wiatr": "nieznany", "sztorm": False, "dni_rejsu": 7}
    )


def zaladuj_statek(port_docelowy: str, pozycje: list[dict] | list[PozycjaZapasow]) -> str:
    """Ładuje zapasy na statek i wyznacza kurs do portu docelowego."""
    razem = 0
    for p in pozycje:
        if isinstance(p, dict):
            razem += p.get("beczki", 0)
        else:
            razem += getattr(p, "beczki", 0)
    return f"⚓ Załadowano łącznie {razem} beczek/skrzyń. Kurs na {port_docelowy} wyznaczony!"


# =============================================================================
# SUB-AGENT 1: KWATERMISTRZ (mode="task")
# =============================================================================

kwatermistrz = Agent(
    name="kwatermistrz",
    model=MODEL,
    mode="task",
    output_schema=ListaZapasow,
    disallow_transfer_to_parent=True,
    disallow_transfer_to_peers=True,
    description="Zbiera bezpośrednio od użytkownika listę zapasów na rejs (rum, suchary, woda, proch, kule armatnie).",
    instruction="""Jesteś Kwatermistrzem na statku pirackim.
W magazynie posiadasz TYLKO: rum, suchary, woda, proch, kule armatnie.

ZASADY:
1. Twoim zadaniem jest rozmowa z użytkownikiem i ustalenie, jakie zapasy załadować.
2. Jeśli użytkownik NIE podał jeszcze listy towarów i ilości:
   - Zwróć wiadomość tekstową do użytkownika i zapytaj go wprost, co i ile beczek chce zabrać.
   - Wymień dostępne towary.
3. Jeśli użytkownik podał zapasy i liczby beczek:
   - NATYCHMIAST wywołaj narzędzie `finish_task(pozycje=[...])`.
   - Zaakceptuj każdą podaną listę (nie wymagaj zamawiania wszystkich 5 towarów).
4. KRYTYCZNE: Gdy wywołujesz `finish_task`, NIE dodawaj tekstu w stylu "Przekazuję sprawę" ani podsumowań. Twoim jedynym działaniem kończącym MUSI być wywołanie narzędzia `finish_task`.""",
)


# =============================================================================
# SUB-AGENT 2: NAWIGATOR (mode="single_turn")
# =============================================================================

nawigator = Agent(
    name="nawigator",
    model=MODEL,
    mode="single_turn",
    description="Sprawdza pogodę i długość rejsu do portu docelowego. Działa w tle bez kontaktu z użytkownikiem.",
    instruction="""Jesteś Nawigatorem. Użyj narzędzia `sprawdz_pogode` dla wskazanego portu i zwróć krótki raport: parametry wiatru, ryzyko sztormu i czas rejsu.""",
    tools=[sprawdz_pogode],
)


# =============================================================================
# KOORDYNATOR (root)
# =============================================================================

root_agent = Agent(
    name="kapitan_portu",
    model=MODEL,
    instruction="""Jesteś Kapitanem Portu. Koordynujesz przygotowanie okrętu do wyprawy.

TWOJA PROCEDURA:
1. Port docelowy: Ustal z użytkownikiem port (Tortuga, Port Royal lub Nassau). Jeśli jeszcze go nie podał, zapytaj o port.
2. Gdy znasz port docelowy:
   - Wywołaj podwładnego `nawigator`, aby sprawdzić pogodę na trasie.
   - NATYCHMIAST wywołaj podwładnego `kwatermistrz`, aby przejął rozmowę z użytkownikiem i zebrał zamówienie na zapasy.
   - KRYTYCZNE: Ty (Kapitan) NIE pytaj użytkownika w swojej wiadomości o zapasy, beczki czy prowiant! Oddaj to zadanie w całości Kwatermistrzowi poprzez wywołanie jego narzędzia.
3. Gdy Kwatermistrz zakończy zadanie i zwróci listę zapasów:
   - Wywołaj narzędzie `zaladuj_statek(port_docelowy=..., pozycje=...)`.
   - Przedstaw użytkownikowi ostateczne podsumowanie: status załadunku, pogodę i ostrzeżenie przed sztormem (jeśli występuje).""",
    sub_agents=[kwatermistrz, nawigator],
    tools=[zaladuj_statek],
)
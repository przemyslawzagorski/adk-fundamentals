"""
Module 12: Router Agent - The Captain's Command
================================================

Ten moduł demonstruje wzorzec routingu (przekierowywania) w ADK.
Kapitan używa klasy RouterAgent, aby skierować pytania do odpowiedniego specjalisty z załogi.

Kluczowe koncepcje:
- RouterAgent do inteligentnego kierowania zapytań
- Sub-agenci jako specjaliści w swoich domenach
- Precyzyjne opisy (description) jako klucz do dobrego routingu
"""

import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent

load_dotenv()
MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")

# =============================================================================
# SPECJALIŚCI Z ZAŁOGI
# =============================================================================

navigator_agent = LlmAgent(
    model=MODEL,
    name="navigator",
    description="Ekspert od nawigacji, map, tras, pogody i warunków na morzu. Odpowiada na pytania o kierunki i czas podróży.",
    instruction="""Jesteś Nawigatorem statku!
    Odpowiadaj na pytania o trasy, nawigację, mapy i pogodę.
    Używaj żeglarskiego żargonu (węzły, sterburt, kurs)."""
)

quartermaster_agent = LlmAgent(
    model=MODEL,
    name="quartermaster",
    description="Ekspert od ładunku, zapasów, inwentarza, amunicji i napraw statku.",
    instruction="""Jesteś Kwatermistrzem!
    Odpowiadaj na pytania o zapasy, prowiant, stan statku i naprawy.
    Bądź precyzyjny w wyliczeniach beczek i skrzyń."""
)

gunner_agent = LlmAgent(
    model=MODEL,
    name="gunner",
    description="Ekspert od broni, armat, taktyk walki i obrony statku przed wrogiem.",
    instruction="""Jesteś Głównym Artylerzystą!
    Odpowiadaj na pytania o uzbrojenie, taktykę bitewną i obronę.
    Wypowiadaj się z autorytetem weterana walk morskich."""
)

cook_agent = LlmAgent(
    model=MODEL,
    name="cook",
    description="Ekspert od jedzenia, przygotowywania posiłków, morale załogi i racji rumu.",
    instruction="""Jesteś Okrętowym Kucharzem!
    Odpowiadaj na pytania o jedzenie, zdrowie załogi i racje rumu.
    Bądź wesoły i dbaj o pełne brzuchy załogi."""
)

# =============================================================================
# KAPITAN (ROUTER AGENT)
# =============================================================================

root_agent = LlmAgent(
    name="captain_router",
    model=MODEL,
    instruction="""Ahoj! Jesteś Kapitanem Czarnej Perły - inteligentnym routerem.

    Twoim zadaniem jest przekierowanie pytań użytkownika do odpowiednich członków załogi na podstawie ich specjalizacji.

    Przeanalizuj pytanie i wybierz JEDNEGO eksperta:
    - Nawigacja, trasy, pogoda -> navigator
    - Zapasy, ładownia, naprawy -> quartermaster
    - Walka, broń, taktyka -> gunner
    - Jedzenie, picie, morale -> cook

    Jeśli pytanie nie pasuje, po prostu poproś o doprecyzowanie.
    """,
    sub_agents=[
        navigator_agent,
        quartermaster_agent,
        gunner_agent,
        cook_agent
    ]
)
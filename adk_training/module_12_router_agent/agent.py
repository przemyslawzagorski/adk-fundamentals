"""
Module 12: Router Agent - The Captain's Command
================================================

Ten modu┼é demonstruje wzorzec routingu (przekierowywania) w ADK.
Kapitan u┼╝ywa klasy RouterAgent, aby skierowa─ç pytania do odpowiedniego specjalisty z za┼éogi.

Kluczowe koncepcje:
- RouterAgent do inteligentnego kierowania zapyta┼ä
- Sub-agenci jako specjali┼Ťci w swoich domenach
- Precyzyjne opisy (description) jako klucz do dobrego routingu
"""

import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent

load_dotenv()
MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")

# =============================================================================
# SPECJALI┼ÜCI Z ZA┼üOGI
# =============================================================================

navigator_agent = LlmAgent(
    model=MODEL,
    name="navigator",
    description="Ekspert od nawigacji, map, tras, pogody i warunk├│w na morzu. Odpowiada na pytania o kierunki i czas podr├│┼╝y.",
    instruction="""Jeste┼Ť Nawigatorem statku!
    Odpowiadaj na pytania o trasy, nawigacj─Ö, mapy i pogod─Ö.
    U┼╝ywaj ┼╝eglarskiego ┼╝argonu (w─Öz┼éy, sterburt, kurs)."""
)

quartermaster_agent = LlmAgent(
    model=MODEL,
    name="quartermaster",
    description="Ekspert od ┼éadunku, zapas├│w, inwentarza, amunicji i napraw statku.",
    instruction="""Jeste┼Ť Kwatermistrzem!
    Odpowiadaj na pytania o zapasy, prowiant, stan statku i naprawy.
    B─ůd┼║ precyzyjny w wyliczeniach beczek i skrzy┼ä."""
)

gunner_agent = LlmAgent(
    model=MODEL,
    name="gunner",
    description="Ekspert od broni, armat, taktyk walki i obrony statku przed wrogiem.",
    instruction="""Jeste┼Ť G┼é├│wnym Artylerzyst─ů!
    Odpowiadaj na pytania o uzbrojenie, taktyk─Ö bitewn─ů i obron─Ö.
    Wypowiadaj si─Ö z autorytetem weterana walk morskich."""
)

cook_agent = LlmAgent(
    model=MODEL,
    name="cook",
    description="Ekspert od jedzenia, przygotowywania posi┼ék├│w, morale za┼éogi i racji rumu.",
    instruction="""Jeste┼Ť Okr─Ötowym Kucharzem!
    Odpowiadaj na pytania o jedzenie, zdrowie za┼éogi i racje rumu.
    B─ůd┼║ weso┼éy i dbaj o pe┼éne brzuchy za┼éogi."""
)

# =============================================================================
# KAPITAN (ROUTER AGENT)
# =============================================================================

root_agent = LlmAgent(
    name="captain_router",
    model=MODEL,
    instruction="""Ahoj! Jeste┼Ť Kapitanem Czarnej Per┼éy - inteligentnym routerem.

    Twoim zadaniem jest przekierowanie pyta┼ä u┼╝ytkownika do odpowiednich cz┼éonk├│w za┼éogi na podstawie ich specjalizacji.

    Przeanalizuj pytanie i wybierz JEDNEGO eksperta:
    - Nawigacja, trasy, pogoda -> navigator
    - Zapasy, ┼éadownia, naprawy -> quartermaster
    - Walka, bro┼ä, taktyka -> gunner
    - Jedzenie, picie, morale -> cook

    Je┼Ťli pytanie nie pasuje, po prostu popro┼Ť o doprecyzowanie.
    """,
    sub_agents=[
        navigator_agent,
        quartermaster_agent,
        gunner_agent,
        cook_agent
    ]
)

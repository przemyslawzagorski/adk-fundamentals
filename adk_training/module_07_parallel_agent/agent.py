"""
Modu┼é 7: Agent R├│wnoleg┼éy - "Rada Za┼éogi"
==========================================
Naucz si─Ö uruchamia─ç wielu agent├│w jednocze┼Ťnie u┼╝ywaj─ůc ParallelAgent.

Temat: Trzej zwiadowcy eksploruj─ů r├│┼╝ne kierunki r├│wnolegle,
potem Szpiegmistrz syntetyzuje ich raporty wywiadowcze.

Kluczowe Koncepcje:
- ParallelAgent uruchamia sub_agents wsp├│┼ébie┼╝nie (izolowane konteksty)
- Ka┼╝dy r├│wnoleg┼éy agent zapisuje do w┼éasnego output_key
- SequentialAgent opakowuje r├│wnoleg┼ée wykonanie + syntez─Ö
- Wzorzec agregacji wynik├│w
"""

import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent

load_dotenv()

# Konfiguracja
MODEL = "gemini-2.5-flash"

# =============================================================================
# R├ôWNOLEG┼üY ZWIADOWCY - Trzej agenci eksploruj─ůcy jednocze┼Ťnie
# =============================================================================

north_scout = LlmAgent(
    model=MODEL,
    name="zwiadowca_polnocny",
    instruction="""Jeste┼Ť P├ô┼üNOCNYM ZWIADOWC─ä za┼éogi!

    Twoja misja: Zwiaduj p├│┼énocne wody szukaj─ůc:
    - Ruch├│w wrogich statk├│w
    - Harmonogram├│w statk├│w handlowych
    - Wzorc├│w pogodowych nadci─ůgaj─ůcych z p├│┼énocy
    - Fortyfikacji przybrze┼╝nych

    Na podstawie zapytania Kapitana, dostarcz wywiad z sektora P├ô┼üNOCNEGO.
    B─ůd┼║ zwi─Öz┼éy ale dok┼éadny. Zako┼äcz "Zwiadowca P├│┼énocny raportuje!"
    """,
    description="Zwiaduje p├│┼énocne wody dla wywiadu",
    output_key="raport_polnocny"
)

south_scout = LlmAgent(
    model=MODEL,
    name="zwiadowca_poludniowy",
    instruction="""Jeste┼Ť PO┼üUDNIOWYM ZWIADOWC─ä za┼éogi!

    Twoja misja: Zwiaduj po┼éudniowe wody szukaj─ůc:
    - Ukrytych zatoczek i bezpiecznych port├│w
    - Tras konwoj├│w kupieckich
    - Harmonogram├│w patroli marynarki
    - Zasob├│w wyspiarskich

    Na podstawie zapytania Kapitana, dostarcz wywiad z sektora PO┼üUDNIOWEGO.
    B─ůd┼║ zwi─Öz┼éy ale dok┼éadny. Zako┼äcz "Zwiadowca Po┼éudniowy raportuje!"
    """,
    description="Zwiaduje po┼éudniowe wody dla wywiadu",
    output_key="raport_poludniowy"
)

east_scout = LlmAgent(
    model=MODEL,
    name="zwiadowca_wschodni",
    instruction="""Jeste┼Ť WSCHODNIM ZWIADOWC─ä za┼éogi!

    Twoja misja: Zwiaduj wschodnie wody szukaj─ůc:
    - Okazji do ataku o wschodzie s┼éo┼äca
    - Ruch├│w flot rybackich
    - Aktywno┼Ťci miast portowych
    - System├│w burzowych ze wschodu

    Na podstawie zapytania Kapitana, dostarcz wywiad z sektora WSCHODNIEGO.
    B─ůd┼║ zwi─Öz┼éy ale dok┼éadny. Zako┼äcz "Zwiadowca Wschodni raportuje!"
    """,
    description="Zwiaduje wschodnie wody dla wywiadu",
    output_key="raport_wschodni"
)

# =============================================================================
# R├ôWNOLEG┼üE WYKONANIE - Wszyscy zwiadowcy dzia┼éaj─ů jednocze┼Ťnie
# =============================================================================

parallel_scouts = ParallelAgent(
    name="grupa_zwiadowcza",
    description="Wysy┼éa wszystkich trzech zwiadowc├│w jednocze┼Ťnie dla maksymalnego pokrycia",
    sub_agents=[north_scout, south_scout, east_scout]
)

# =============================================================================
# SZPIEGMISTRZ - Syntetyzuje wszystkie raporty wywiadowcze
# =============================================================================

spymaster = LlmAgent(
    model=MODEL,
    name="szpiegmistrz",
    instruction="""Jeste┼Ť SZPIEGMISTRZEM - mistrzem zbierania wywiadu!

    Twoi zwiadowcy wr├│cili ze swoimi raportami:

    ­čôŹ SEKTOR P├ô┼üNOCNY:
    {raport_polnocny}

    ­čôŹ SEKTOR PO┼üUDNIOWY:
    {raport_poludniowy}

    ­čôŹ SEKTOR WSCHODNI:
    {raport_wschodni}

    Tw├│j obowi─ůzek:
    1. Zsyntetyzuj ca┼éy wywiad w zunifikowany briefing
    2. Zidentyfikuj najbardziej obiecuj─ůc─ů okazj─Ö
    3. Oznacz wszelkie niebezpiecze┼ästwa lub konflikty mi─Ödzy raportami
    4. Zarekomenduj nast─Öpny ruch Kapitana

    Sformatuj jako odpowiedni briefing wywiadowczy dla Kapitana.
    """,
    description="Syntetyzuje wywiad od wszystkich zwiadowc├│w w wykonalny briefing",
    output_key="briefing_wywiadowczy"
)

# =============================================================================
# KOMPLETNA MISJA - R├│wnoleg┼éy zwiad nast─Öpnie synteza
# =============================================================================

root_agent = SequentialAgent(
    name="misja_rozpoznawcza",
    description="Kompletne rozpoznanie: r├│wnoleg┼éy zwiad + synteza wywiadu",
    sub_agents=[parallel_scouts, spymaster]
)


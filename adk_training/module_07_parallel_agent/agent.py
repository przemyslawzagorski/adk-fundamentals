"""
Moduł 7: Agent Równoległy - "Rada Załogi"
==========================================
Naucz się uruchamiać wielu agentów jednocześnie używając ParallelAgent.

Temat: Trzej zwiadowcy eksplorują różne kierunki równolegle,
potem Szpiegmistrz syntetyzuje ich raporty wywiadowcze.

Kluczowe Koncepcje:
- ParallelAgent uruchamia sub_agents współbieżnie (izolowane konteksty)
- Każdy równoległy agent zapisuje do własnego output_key
- SequentialAgent opakowuje równoległe wykonanie + syntezę
- Wzorzec agregacji wyników
"""

import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent

load_dotenv()

# Konfiguracja
MODEL = "gemini-2.5-flash"

# =============================================================================
# RÓWNOLEGŁY ZWIADOWCY - Trzej agenci eksplorujący jednocześnie
# =============================================================================

north_scout = LlmAgent(
    model=MODEL,
    name="zwiadowca_polnocny",
    instruction="""Jesteś PÓŁNOCNYM ZWIADOWCĄ załogi!

    Twoja misja: Zwiaduj północne wody szukając:
    - Ruchów wrogich statków
    - Harmonogramów statków handlowych
    - Wzorców pogodowych nadciągających z północy
    - Fortyfikacji przybrzeżnych

    Na podstawie zapytania Kapitana, dostarcz wywiad z sektora PÓŁNOCNEGO.
    Bądź zwięzły ale dokładny. Zakończ "Zwiadowca Północny raportuje!"
    """,
    description="Zwiaduje północne wody dla wywiadu",
    output_key="raport_polnocny"
)

south_scout = LlmAgent(
    model=MODEL,
    name="zwiadowca_poludniowy",
    instruction="""Jesteś POŁUDNIOWYM ZWIADOWCĄ załogi!

    Twoja misja: Zwiaduj południowe wody szukając:
    - Ukrytych zatoczek i bezpiecznych portów
    - Tras konwojów kupieckich
    - Harmonogramów patroli marynarki
    - Zasobów wyspiarskich

    Na podstawie zapytania Kapitana, dostarcz wywiad z sektora POŁUDNIOWEGO.
    Bądź zwięzły ale dokładny. Zakończ "Zwiadowca Południowy raportuje!"
    """,
    description="Zwiaduje południowe wody dla wywiadu",
    output_key="raport_poludniowy"
)

east_scout = LlmAgent(
    model=MODEL,
    name="zwiadowca_wschodni",
    instruction="""Jesteś WSCHODNIM ZWIADOWCĄ załogi!

    Twoja misja: Zwiaduj wschodnie wody szukając:
    - Okazji do ataku o wschodzie słońca
    - Ruchów flot rybackich
    - Aktywności miast portowych
    - Systemów burzowych ze wschodu

    Na podstawie zapytania Kapitana, dostarcz wywiad z sektora WSCHODNIEGO.
    Bądź zwięzły ale dokładny. Zakończ "Zwiadowca Wschodni raportuje!"
    """,
    description="Zwiaduje wschodnie wody dla wywiadu",
    output_key="raport_wschodni"
)

# =============================================================================
# RÓWNOLEGŁE WYKONANIE - Wszyscy zwiadowcy działają jednocześnie
# =============================================================================

parallel_scouts = ParallelAgent(
    name="grupa_zwiadowcza",
    description="Wysyła wszystkich trzech zwiadowców jednocześnie dla maksymalnego pokrycia",
    sub_agents=[north_scout, south_scout, east_scout]
)

# =============================================================================
# SZPIEGMISTRZ - Syntetyzuje wszystkie raporty wywiadowcze
# =============================================================================

spymaster = LlmAgent(
    model=MODEL,
    name="szpiegmistrz",
    instruction="""Jesteś SZPIEGMISTRZEM - mistrzem zbierania wywiadu!

    Twoi zwiadowcy wrócili ze swoimi raportami:

    📍 SEKTOR PÓŁNOCNY:
    {raport_polnocny}

    📍 SEKTOR POŁUDNIOWY:
    {raport_poludniowy}

    📍 SEKTOR WSCHODNI:
    {raport_wschodni}

    Twój obowiązek:
    1. Zsyntetyzuj cały wywiad w zunifikowany briefing
    2. Zidentyfikuj najbardziej obiecującą okazję
    3. Oznacz wszelkie niebezpieczeństwa lub konflikty między raportami
    4. Zarekomenduj następny ruch Kapitana

    Sformatuj jako odpowiedni briefing wywiadowczy dla Kapitana.
    """,
    description="Syntetyzuje wywiad od wszystkich zwiadowców w wykonalny briefing",
    output_key="briefing_wywiadowczy"
)

# =============================================================================
# KOMPLETNA MISJA - Równoległy zwiad następnie synteza
# =============================================================================

root_agent = SequentialAgent(
    name="misja_rozpoznawcza",
    description="Kompletne rozpoznanie: równoległy zwiad + synteza wywiadu",
    sub_agents=[parallel_scouts, spymaster]
)


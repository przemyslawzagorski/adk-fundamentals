"""
Moduł 7: Agent Równoległy - "Rada Załogi"
==========================================
Naucz się uruchamiać wielu agentów jednocześnie używając ParallelAgent.

Ten plik zawiera bazowy przykład oraz rozwiązania wszystkich 3 ćwiczeń.
Przewiń na sam dół pliku, aby odkomentować wariant, który chcesz przetestować!
"""

import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent

load_dotenv()

# Konfiguracja
MODEL = "gemini-2.5-flash"

# =============================================================================
# BAZA - 3 Zwiadowców geograficznych
# =============================================================================

north_scout_base = LlmAgent(
    model=MODEL,
    name="zwiadowca_polnocny",
    instruction="""Jesteś PÓŁNOCNYM ZWIADOWCĄ załogi!
    Twoja misja: Zwiaduj północne wody szukając ruchów wrogich statków i pogody.
    Na podstawie zapytania Kapitana, dostarcz wywiad z sektora PÓŁNOCNEGO.
    Bądź zwięzły ale dokładny. Zakończ "Zwiadowca Północny raportuje!"
    """,
    output_key="raport_polnocny"
)

south_scout_base = LlmAgent(
    model=MODEL,
    name="zwiadowca_poludniowy",
    instruction="""Jesteś POŁUDNIOWYM ZWIADOWCĄ załogi!
    Twoja misja: Zwiaduj południowe wody szukając ukrytych zatoczek i tras kupieckich.
    Na podstawie zapytania Kapitana, dostarcz wywiad z sektora POŁUDNIOWEGO.
    Bądź zwięzły ale dokładny. Zakończ "Zwiadowca Południowy raportuje!"
    """,
    output_key="raport_poludniowy"
)

east_scout_base = LlmAgent(
    model=MODEL,
    name="zwiadowca_wschodni",
    instruction="""Jesteś WSCHODNIM ZWIADOWCĄ załogi!
    Twoja misja: Zwiaduj wschodnie wody szukając okazji do ataku o wschodzie słońca.
    Na podstawie zapytania Kapitana, dostarcz wywiad z sektora WSCHODNIEGO.
    Bądź zwięzły ale dokładny. Zakończ "Zwiadowca Wschodni raportuje!"
    """,
    output_key="raport_wschodni"
)

parallel_scouts_base = ParallelAgent(
    name="grupa_zwiadowcza_baza",
    sub_agents=[north_scout_base, south_scout_base, east_scout_base]
)

spymaster_base = LlmAgent(
    model=MODEL,
    name="szpiegmistrz_baza",
    instruction="""Jesteś SZPIEGMISTRZEM! Zsyntetyzuj raporty:
    PÓŁNOC: {raport_polnocny}
    POŁUDNIE: {raport_poludniowy}
    WSCHÓD: {raport_wschodni}

    Zarekomenduj następny ruch Kapitana.
    """,
    output_key="briefing_wywiadowczy"
)

root_agent_base = SequentialAgent(
    name="misja_bazowa",
    sub_agents=[parallel_scouts_base, spymaster_base]
)


# =============================================================================
# ĆWICZENIE 1: Dodaj Czwartego Zwiadowcę (Zachodniego)
# =============================================================================

north_scout_ex1 = LlmAgent(
    model=MODEL,
    name="zwiadowca_polnocny_ex1",
    instruction="""Jesteś PÓŁNOCNYM ZWIADOWCĄ załogi! Zwiaduj północne wody szukając wrogich statków i pogody. Dostarcz wywiad z sektora PÓŁNOCNEGO. Zakończ "Zwiadowca Północny raportuje!\"""",
    output_key="raport_polnocny"
)

south_scout_ex1 = LlmAgent(
    model=MODEL,
    name="zwiadowca_poludniowy_ex1",
    instruction="""Jesteś POŁUDNIOWYM ZWIADOWCĄ załogi! Zwiaduj południowe wody szukając ukrytych zatoczek i tras kupieckich. Dostarcz wywiad z sektora POŁUDNIOWEGO. Zakończ "Zwiadowca Południowy raportuje!\"""",
    output_key="raport_poludniowy"
)

east_scout_ex1 = LlmAgent(
    model=MODEL,
    name="zwiadowca_wschodni_ex1",
    instruction="""Jesteś WSCHODNIM ZWIADOWCĄ załogi! Zwiaduj wschodnie wody szukając okazji do ataku o wschodzie słońca. Dostarcz wywiad z sektora WSCHODNIEGO. Zakończ "Zwiadowca Wschodni raportuje!\"""",
    output_key="raport_wschodni"
)

west_scout_ex1 = LlmAgent(
    model=MODEL,
    name="zwiadowca_zachodni_ex1",
    instruction="""Jesteś ZACHODNIM ZWIADOWCĄ załogi!
    Twoja misja: Zwiaduj zachodnie wody szukając tras ucieczki i wysp.
    Na podstawie zapytania Kapitana, dostarcz wywiad z sektora ZACHODNIEGO.
    Bądź zwięzły ale dokładny. Zakończ "Zwiadowca Zachodni raportuje!"
    """,
    output_key="raport_zachodni"
)

parallel_scouts_ex1 = ParallelAgent(
    name="grupa_zwiadowcza_ex1",
    sub_agents=[north_scout_ex1, south_scout_ex1, east_scout_ex1, west_scout_ex1]
)

spymaster_ex1 = LlmAgent(
    model=MODEL,
    name="szpiegmistrz_ex1",
    instruction="""Jesteś SZPIEGMISTRZEM! Zsyntetyzuj raporty od 4 zwiadowców:
    PÓŁNOC: {raport_polnocny}
    POŁUDNIE: {raport_poludniowy}
    WSCHÓD: {raport_wschodni}
    ZACHÓD: {raport_zachodni}

    Zarekomenduj następny ruch Kapitana uwzględniając wszystkie kierunki.
    """,
    output_key="briefing_wywiadowczy"
)

root_agent_ex1 = SequentialAgent(
    name="misja_ex1_czterech_zwiadowcow",
    sub_agents=[parallel_scouts_ex1, spymaster_ex1]
)


# =============================================================================
# ĆWICZENIE 2: Wyspecjalizowani Zwiadowcy
# =============================================================================

weather_expert = LlmAgent(
    model=MODEL,
    name="ekspert_pogodowy",
    instruction="""Jesteś EKSPERTEM POGODOWYM floty. Skup się TYLKO na analizie warunków atmosferycznych (burze, wiatry). Na podstawie zapytania Kapitana, dostarcz raport pogodowy.""",
    output_key="raport_pogodowy"
)

military_analyst = LlmAgent(
    model=MODEL,
    name="analityk_wojskowy",
    instruction="""Jesteś ANALITYKIEM WOJSKOWYM floty. Skup się TYLKO na analizie zagrożeń militarnych (flota wroga, porty). Na podstawie zapytania Kapitana, dostarcz raport taktyczny.""",
    output_key="raport_wojskowy"
)

trade_specialist = LlmAgent(
    model=MODEL,
    name="specjalista_handlowy",
    instruction="""Jesteś SPECJALISTĄ HANDLOWYM floty. Skup się TYLKO na okazjach do łupów i handlu (statki kupieckie). Na podstawie zapytania Kapitana, dostarcz raport o potencjalnych łupach.""",
    output_key="raport_handlowy"
)

parallel_experts = ParallelAgent(
    name="rada_ekspertow",
    sub_agents=[weather_expert, military_analyst, trade_specialist]
)

spymaster_specialized = LlmAgent(
    model=MODEL,
    name="szpiegmistrz_ekspertow",
    instruction="""Jesteś SZPIEGMISTRZEM. Zsyntetyzuj wiedzę domenową specjalistów:
    ☁️ POGODA: {raport_pogodowy}
    ⚔️ WOJSKO: {raport_wojskowy}
    💰 HANDEL: {raport_handlowy}

    Dostarcz kompleksową rekomendację.
    """,
    output_key="briefing_wywiadowczy"
)

root_agent_ex2 = SequentialAgent(
    name="misja_ex2_specjalisci",
    sub_agents=[parallel_experts, spymaster_specialized]
)


# =============================================================================
# ĆWICZENIE 3: Wzorzec Głosowania
# =============================================================================

weather_voter = LlmAgent(
    model=MODEL,
    name="ekspert_pogodowy_glosujacy",
    instruction="""Oceń warunki pogodowe dla celu zapytania.
    NA KOŃCU RAPORTU MUSISZ ODDAĆ GŁOS NA JEDNĄ Z AKCJI:
    - GŁOS: ATAKUJ (dobra pogoda)
    - GŁOS: CZEKAJ (niepewna pogoda)
    - GŁOS: ODRÓT (sztorm)
    """,
    output_key="glos_pogodowy"
)

military_voter = LlmAgent(
    model=MODEL,
    name="analityk_wojskowy_glosujacy",
    instruction="""Oceń siły wroga dla celu zapytania.
    NA KOŃCU RAPORTU MUSISZ ODDAĆ GŁOS NA JEDNĄ Z AKCJI:
    - GŁOS: ATAKUJ (słaby wróg)
    - GŁOS: CZEKAJ (potrzeba czasu na przygotowania)
    - GŁOS: ODRÓT (przeważające siły wroga)
    """,
    output_key="glos_wojskowy"
)

trade_voter = LlmAgent(
    model=MODEL,
    name="specjalista_handlowy_glosujacy",
    instruction="""Oceń łupy dla celu zapytania.
    NA KOŃCU RAPORTU MUSISZ ODDAĆ GŁOS NA JEDNĄ Z AKCJI:
    - GŁOS: ATAKUJ (bogate łupy)
    - GŁOS: CZEKAJ (dopiero płyną)
    - GŁOS: ODRÓT (brak wartościowych celów)
    """,
    output_key="glos_handlowy"
)

parallel_voters = ParallelAgent(
    name="glosowanie_rady",
    sub_agents=[weather_voter, military_voter, trade_voter]
)

vote_counter = LlmAgent(
    model=MODEL,
    name="kapitan_liczacy_glosy",
    instruction="""Otrzymałeś głosy rady:
    Pogoda: {glos_pogodowy}
    Wojsko: {glos_wojskowy}
    Handel: {glos_handlowy}

    Twoje zadanie:
    1. Zlicz głosy na ATAKUJ, CZEKAJ i ODRÓT.
    2. Ogłoś ostateczną decyzję na podstawie większości głosów.
    3. Krótko uargumentuj.
    Zakończ "DECYZJA RADY: [AKCJA]"
    """,
    output_key="ostateczna_decyzja"
)

root_agent_ex3 = SequentialAgent(
    name="misja_ex3_demokracja",
    sub_agents=[parallel_voters, vote_counter]
)


# =============================================================================
# WYBÓR AKTYWNEGO AGENTA DO TESTÓW (Zostaw odkomentowane TYLKO jedno)
# =============================================================================

#root_agent = root_agent_base          # Test kodu bazowego (3 geograficznych zwiadowców)
#root_agent = root_agent_ex1         # Test ćwiczenia 1 (4 geograficznych zwiadowców)
#root_agent = root_agent_ex2         # Test ćwiczenia 2 (Specjaliści dziedzinowi)
root_agent = root_agent_ex3         # Test ćwiczenia 3 (Wzorzec głosowania)
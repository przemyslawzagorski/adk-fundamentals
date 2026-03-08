"""
Moduł 4: Sekwencyjny Multi-Agent - Pipeline Planowania
=======================================================

Ten moduł demonstruje SequentialAgent dla wieloetapowych przepływów pracy.
Trzej agenci pracują sekwencyjnie: Zwiadowca → Strateg → Kapitan.

Kluczowe Koncepcje:
- SequentialAgent orkiestruje agentów w kolejności
- output_key przechowuje wynik każdego agenta w stanie sesji
- Składnia {key_name} odczytuje ze stanu w instrukcjach
- Dane przepływają automatycznie przez pipeline

Temat: Planowanie rajdu z wywiadem, strategią i zatwierdzeniem!
"""

import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent, SequentialAgent

# Załaduj zmienne środowiskowe
load_dotenv()

# Konfiguracja
MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")
AGENT_APP_NAME = "flota_planowania_rajdu"

# =============================================================================
# AGENT 1: ZWIADOWCA
# =============================================================================
# Zwiadowca zbiera wywiad o celu. Ich wynik jest przechowywany
# w stanie sesji pod kluczem "raport_wywiadu".

scout = LlmAgent(
    model=MODEL,
    name="zwiadowca",
    description="Zwiadowca zbierający wywiad o celach.",
    instruction="""Jesteś Zwiadowcą - oczami i uszami floty.

Twoja misja: Zbierz wywiad o celu który wspomina użytkownik.

Dla każdego celu (port, statek, wyspa, lub lokalizacja skarbu), dostarcz:
1. **Szczegóły Lokalizacji**: Gdzie dokładnie jest? Jaki jest teren?
2. **Obrona**: Straże, działa, fortyfikacje, harmonogramy patroli
3. **Kosztowności**: Jakie skarby lub dobra można tam znaleźć?
4. **Ryzyka**: Pogoda, obecność marynarki, lokalne zagrożenia
5. **Okna Możliwości**: Najlepsze czasy na podejście

Bądź dokładny ale zwięzły. Strateg potrzebuje dobrego wywiadu do planowania!

Formatuj raport wyraźnie z sekcjami. Zakończ oceną pewności (1-10).""",
    output_key="raport_wywiadu"  # Przechowuje wynik w stanie sesji
)

# =============================================================================
# AGENT 2: STRATEG
# =============================================================================
# Strateg czyta raport_wywiadu Zwiadowcy ze stanu i tworzy plan.
# Ich wynik jest przechowywany pod "plan_bitwy".

strategist = LlmAgent(
    model=MODEL,
    name="strateg",
    description="Taktyczny mistrz tworzący plany bitewne.",
    instruction="""Jesteś Strategiem! Czas opracować sprytny plan.

**RAPORT WYWIADOWCZY ZWIADOWCY:**
{raport_wywiadu}

Na podstawie tego wywiadu, stwórz szczegółowy plan rajdu:

1. **Strategia Podejścia**: Jak podejdziemy niewykryci?
2. **Timing**: Kiedy uderzamy? (na podstawie okien możliwości)
3. **Przydziały Załogi**: Kto co robi podczas rajdu?
   - Grupa abordażowa
   - Obserwatorzy
   - Załoga ucieczki
4. **Plany Awaryjne**: Co jeśli coś pójdzie nie tak?
5. **Droga Ucieczki**: Jak uciekniemy z łupem?
6. **Oczekiwany Łup**: Szacunek skarbów do zdobycia

Rozważ ryzyka wspomniane w wywiadzie. Priorytet: bezpieczeństwo załogi!

Zakończ oceną ryzyka: Niskie / Średnie / Wysokie""",
    output_key="plan_bitwy"  # Przechowuje wynik w stanie sesji
)

# =============================================================================
# AGENT 3: KAPITAN
# =============================================================================
# Kapitan przegląda zarówno wywiad jak i plan, potem podejmuje ostateczną decyzję.
# Może uzyskać dostęp do obu poprzednich wyników ze stanu.

captain = LlmAgent(
    model=MODEL,
    name="kapitan",
    description="Kapitan zatwierdzający lub odrzucający plany rajdów.",
    instruction="""Jesteś Kapitanem! Załoga czeka na Twoją decyzję.

**WYWIAD ZWIADOWCY:**
{raport_wywiadu}

**PLAN BITEWNY STRATEGA:**
{plan_bitwy}

Jako Kapitan, musisz podjąć ostateczną decyzję. Rozważ:

1. **Czy wywiad jest wiarygodny?** (Sprawdź ocenę pewności)
2. **Czy plan jest solidny?** (Czy uwzględnia ryzyka?)
3. **Czy warto ryzykować?** (Skarb vs. niebezpieczeństwo dla załogi)
4. **Morale załogi**: Czy to podniesie czy obniży morale?

Wydaj werdykt:
- ⚓ **ZATWIERDZONY**: W drogę! Dołącz ewentualne modyfikacje.
- 🏴‍☠️ **ZATWIERDZONY WARUNKOWO**: Jedź, ale zmień te rzeczy...
- ❌ **ODRZUCONY**: Zbyt ryzykowne. Wyjaśnij dlaczego i zasugeruj alternatywy.

Zakończ porywającą mową do załogi (2-3 zdania)!""",
    output_key="decyzja_kapitana"  # Końcowy wynik
)

# =============================================================================
# SEKWENCYJNY PIPELINE
# =============================================================================
# SequentialAgent uruchamia sub_agents w kolejności: zwiadowca → strateg → kapitan
# output_key każdego agenta udostępnia ich odpowiedź następnemu agentowi.

raid_pipeline = SequentialAgent(
    name="pipeline_planowania_rajdu",
    sub_agents=[scout, strategist, captain]
)

# root_agent to to co ADK uruchamia
root_agent = raid_pipeline


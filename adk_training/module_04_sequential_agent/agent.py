"""
Modu┼é 4: Sekwencyjny Multi-Agent - Pipeline Planowania
=======================================================

Ten modu┼é demonstruje SequentialAgent dla wieloetapowych przep┼éyw├│w pracy.
Trzej agenci pracuj─ů sekwencyjnie: Zwiadowca Ôćĺ Strateg Ôćĺ Kapitan.

Kluczowe Koncepcje:
- SequentialAgent orkiestruje agent├│w w kolejno┼Ťci
- output_key przechowuje wynik ka┼╝dego agenta w stanie sesji
- Sk┼éadnia {key_name} odczytuje ze stanu w instrukcjach
- Dane przep┼éywaj─ů automatycznie przez pipeline

Temat: Planowanie rajdu z wywiadem, strategi─ů i zatwierdzeniem!
"""

import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent, SequentialAgent

# Za┼éaduj zmienne ┼Ťrodowiskowe
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
    description="Zwiadowca zbieraj─ůcy wywiad o celach.",
    instruction="""Jeste┼Ť Zwiadowc─ů - oczami i uszami floty.

Twoja misja: Zbierz wywiad o celu kt├│ry wspomina u┼╝ytkownik.

Dla ka┼╝dego celu (port, statek, wyspa, lub lokalizacja skarbu), dostarcz:
1. **Szczeg├│┼éy Lokalizacji**: Gdzie dok┼éadnie jest? Jaki jest teren?
2. **Obrona**: Stra┼╝e, dzia┼éa, fortyfikacje, harmonogramy patroli
3. **Kosztowno┼Ťci**: Jakie skarby lub dobra mo┼╝na tam znale┼║─ç?
4. **Ryzyka**: Pogoda, obecno┼Ť─ç marynarki, lokalne zagro┼╝enia
5. **Okna Mo┼╝liwo┼Ťci**: Najlepsze czasy na podej┼Ťcie

B─ůd┼║ dok┼éadny ale zwi─Öz┼éy. Strateg potrzebuje dobrego wywiadu do planowania!

Formatuj raport wyra┼║nie z sekcjami. Zako┼äcz ocen─ů pewno┼Ťci (1-10).""",
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
    description="Taktyczny mistrz tworz─ůcy plany bitewne.",
    instruction="""Jeste┼Ť Strategiem! Czas opracowa─ç sprytny plan.

**RAPORT WYWIADOWCZY ZWIADOWCY:**
{raport_wywiadu}

Na podstawie tego wywiadu, stw├│rz szczeg├│┼éowy plan rajdu:

1. **Strategia Podej┼Ťcia**: Jak podejdziemy niewykryci?
2. **Timing**: Kiedy uderzamy? (na podstawie okien mo┼╝liwo┼Ťci)
3. **Przydzia┼éy Za┼éogi**: Kto co robi podczas rajdu?
   - Grupa aborda┼╝owa
   - Obserwatorzy
   - Za┼éoga ucieczki
4. **Plany Awaryjne**: Co je┼Ťli co┼Ť p├│jdzie nie tak?
5. **Droga Ucieczki**: Jak uciekniemy z ┼éupem?
6. **Oczekiwany ┼üup**: Szacunek skarb├│w do zdobycia

Rozwa┼╝ ryzyka wspomniane w wywiadzie. Priorytet: bezpiecze┼ästwo za┼éogi!

Zako┼äcz ocen─ů ryzyka: Niskie / ┼Ürednie / Wysokie""",
    output_key="plan_bitwy"  # Przechowuje wynik w stanie sesji
)

# =============================================================================
# AGENT 3: KAPITAN
# =============================================================================
# Kapitan przegl─ůda zar├│wno wywiad jak i plan, potem podejmuje ostateczn─ů decyzj─Ö.
# Mo┼╝e uzyska─ç dost─Öp do obu poprzednich wynik├│w ze stanu.

captain = LlmAgent(
    model=MODEL,
    name="kapitan",
    description="Kapitan zatwierdzaj─ůcy lub odrzucaj─ůcy plany rajd├│w.",
    instruction="""Jeste┼Ť Kapitanem! Za┼éoga czeka na Twoj─ů decyzj─Ö.

**WYWIAD ZWIADOWCY:**
{raport_wywiadu}

**PLAN BITEWNY STRATEGA:**
{plan_bitwy}

Jako Kapitan, musisz podj─ů─ç ostateczn─ů decyzj─Ö. Rozwa┼╝:

1. **Czy wywiad jest wiarygodny?** (Sprawd┼║ ocen─Ö pewno┼Ťci)
2. **Czy plan jest solidny?** (Czy uwzgl─Ödnia ryzyka?)
3. **Czy warto ryzykowa─ç?** (Skarb vs. niebezpiecze┼ästwo dla za┼éogi)
4. **Morale za┼éogi**: Czy to podniesie czy obni┼╝y morale?

Wydaj werdykt:
- ÔÜô **ZATWIERDZONY**: W drog─Ö! Do┼é─ůcz ewentualne modyfikacje.
- ­čĆ┤ÔÇŹÔśá´ŞĆ **ZATWIERDZONY WARUNKOWO**: Jed┼║, ale zmie┼ä te rzeczy...
- ÔŁî **ODRZUCONY**: Zbyt ryzykowne. Wyja┼Ťnij dlaczego i zasugeruj alternatywy.

Zako┼äcz porywaj─ůc─ů mow─ů do za┼éogi (2-3 zdania)!""",
    output_key="decyzja_kapitana"  # Ko┼äcowy wynik
)

# =============================================================================
# SEKWENCYJNY PIPELINE
# =============================================================================
# SequentialAgent uruchamia sub_agents w kolejno┼Ťci: zwiadowca Ôćĺ strateg Ôćĺ kapitan
# output_key ka┼╝dego agenta udost─Öpnia ich odpowied┼║ nast─Öpnemu agentowi.

raid_pipeline = SequentialAgent(
    name="pipeline_planowania_rajdu",
    sub_agents=[scout, strategist, captain]
)

# root_agent to to co ADK uruchamia
root_agent = raid_pipeline


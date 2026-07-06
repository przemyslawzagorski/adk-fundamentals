"""
Moduł 4: Sequential Agent - ROZWIĄZANIA ĆWICZEŃ
================================================
Ćwiczenia:
1. Dodaj czwartego agenta (Kwatermistrz)
2. Modyfikacja przepływu danych (morale, warunki)
3. Obsługa błędów (niska pewność)
"""

import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent, SequentialAgent

load_dotenv()
MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")

# =============================================================================
# ĆWICZENIE 1: DODAJ CZWARTEGO AGENTA - KWATERMISTRZ
# =============================================================================

scout = LlmAgent(
    model=MODEL,
    name="zwiadowca",
    description="Zwiadowca zbierający wywiad o celach.",
    instruction="""Jesteś Zwiadowcą - zbierz wywiad o celu.

Dostarcz:
1. Szczegóły lokalizacji i terenu
2. Obrona (straże, działa, patrole)
3. Kosztowności (skarby, dobra)
4. Ryzyka (pogoda, marynarka)
5. Okna możliwości (najlepsze czasy)
6. **MORALE załogi** (jak wpłynie na morale)
7. **WARUNKI środowiskowe** (pogoda, prądy morskie)

Zakończ oceną pewności (1-10).""",
    output_key="raport_wywiadu"
)

strategist = LlmAgent(
    model=MODEL,
    name="strateg",
    description="Taktyczny mistrz tworzący plany bitewne.",
    instruction="""Jesteś Strategiem - opracuj plan rajdu.

**RAPORT WYWIADOWCZY:**
{raport_wywiadu}

Stwórz plan:
1. Strategia podejścia
2. Timing (kiedy uderzyć)
3. Przydziały załogi
4. Plany awaryjne
5. Droga ucieczki
6. Oczekiwany łup

Uwzględnij morale i warunki środowiskowe z raportu!
Zakończ oceną ryzyka: Niskie/Średnie/Wysokie""",
    output_key="plan_bitwy"
)

# NOWY AGENT: Kwatermistrz
quartermaster = LlmAgent(
    model=MODEL,
    name="kwatermistrz",
    description="Ocenia potrzeby zasobowe i sprzętowe.",
    instruction="""Jesteś Kwatermistrzem - oceń potrzeby zasobowe.

**PLAN BITEWNY:**
{plan_bitwy}

Oceń:
1. **Zapasy** - żywność, woda, rum (ile dni wystarczy)
2. **Amunicja** - kule armatnie, proch (czy wystarczy do bitwy)
3. **Sprzęt** - liny, kotwice, żagle (stan techniczny)
4. **Załoga** - liczebność, zdrowie (czy wystarczy ludzi)
5. **Koszty** - szacunkowy koszt operacji vs oczekiwany łup

Zakończ rekomendacją: GOTOWI / POTRZEBUJEMY ZAOPATRZENIA / ZBYT RYZYKOWNE""",
    output_key="ocena_zasobow"
)

captain = LlmAgent(
    model=MODEL,
    name="kapitan",
    description="Kapitan zatwierdzający lub odrzucający plany.",
    instruction="""Jesteś Kapitanem - podejmij ostateczną decyzję.

**WYWIAD:**
{raport_wywiadu}

**PLAN:**
{plan_bitwy}

**ZASOBY:**
{ocena_zasobow}

Rozważ:
1. Czy wywiad jest wiarygodny? (ocena pewności)
2. Czy plan jest solidny?
3. Czy mamy zasoby? (ocena kwatermistrza)
4. Morale załogi (z wywiadu)
5. Warunki środowiskowe

**OBSŁUGA BŁĘDÓW:**
- Jeśli pewność wywiadu < 5 → ODRZUĆ (zbyt niepewne)
- Jeśli kwatermistrz mówi ZBYT RYZYKOWNE → ODRZUĆ
- Jeśli ryzyko WYSOKIE + morale NISKIE → ODRZUĆ

Werdykt: ZATWIERDZONY / WARUNKOWO / ODRZUCONY
Zakończ mową do załogi!""",
    output_key="decyzja_kapitana"
)

# =============================================================================
# ROZWIĄZANIE ĆWICZENIA 1
# =============================================================================

root_agent = SequentialAgent(
    name="pipeline_z_kwatermistrzem",
    sub_agents=[scout, strategist, quartermaster, captain]  # 4 agentów!
)

# =============================================================================
# PRZYKŁADY TESTOWANIA
# =============================================================================
"""
TESTOWANIE:

1. Podstawowy scenariusz:
   "Zaplanuj rajd na Port Królewskie"
   → Obserwuj jak wszyscy 4 agenci pracują sekwencyjnie

2. Test niskiej pewności (Ćwiczenie 3):
   "Zaplanuj rajd na nieznaną wyspę"
   → Zwiadowca powinien dać niską pewność (< 5)
   → Kapitan powinien ODRZUCIĆ

3. Test morale (Ćwiczenie 2):
   "Zaplanuj rajd tuż po przegranej bitwie"
   → Zwiadowca: morale NISKIE
   → Kapitan: rozważy wpływ na załogę

4. Test zasobów:
   "Zaplanuj długą wyprawę na odległą wyspę"
   → Kwatermistrz: POTRZEBUJEMY ZAOPATRZENIA
   → Kapitan: rozważy rekomendację

URUCHOMIENIE:
adk web
"""

# =============================================================================
# WARIANT 2: Uproszczony (bez kwatermistrza)
# =============================================================================

# simple_pipeline = SequentialAgent(
#     name="pipeline_prosty",
#     sub_agents=[scout, strategist, captain]
# )

# Odkomentuj aby użyć prostszej wersji:
# root_agent = simple_pipeline


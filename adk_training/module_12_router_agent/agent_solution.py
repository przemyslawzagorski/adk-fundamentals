"""
Moduł 12: Router Agent - ROZWIĄZANIA ĆWICZEŃ
=============================================
Rozwiązanie obejmuje:
1. Dodanie nowego specjalisty (Lekarz / Doctor)
2. Wdrożenie wzorca "Agent as a Tool" (Agent jako Narzędzie)
   zamiast standardowego przekierowania w Routerze.
"""

import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool

load_dotenv()
MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")

# =============================================================================
# 1. SPECJALIŚCI (Włączając nowego: Lekarza)
# =============================================================================

navigator_agent = LlmAgent(
    model=MODEL,
    name="navigator",
    description="Ekspert od nawigacji, map, tras i warunków morskich.",
    instruction="Jesteś Nawigatorem. Odpowiadaj na pytania o trasy, pogodę i szacowany czas podróży."
)

quartermaster_agent = LlmAgent(
    model=MODEL,
    name="quartermaster",
    description="Ekspert od ładunku, zapasów, inwentarza i napraw statku.",
    instruction="Jesteś Kwatermistrzem. Odpowiadaj na pytania o zapasy, amunicję i stan statku."
)

gunner_agent = LlmAgent(
    model=MODEL,
    name="gunner",
    description="Ekspert od broni, taktyk walki i obrony statku.",
    instruction="Jesteś Artylerzystą. Odpowiadaj na pytania o armaty, taktyki i obronę."
)

cook_agent = LlmAgent(
    model=MODEL,
    name="cook",
    description="Ekspert od jedzenia, morale załogi i rozrywki.",
    instruction="Jesteś Kucharzem. Odpowiadaj na pytania o posiłki, racje rumu i morale."
)

# NOWY AGENT - Ćwiczenie 1
doctor_agent = LlmAgent(
    model=MODEL,
    name="doctor",
    description="Ekspert od zdrowia załogi, medycyny i leczenia ran.",
    instruction="""Jesteś Lekarzem Okrętowym (Medykiem).
    Odpowiadaj na pytania o:
    - Leczenie ran odniesionych w walce
    - Zapobieganie chorobom (np. szkorbut)
    - Zioła i zapasy medyczne
    Używaj pirackiego, morskiego żargonu!"""
)

# =============================================================================
# 2. WZORZEC "AGENT AS A TOOL" (Opakowanie agentów w narzędzia)
# =============================================================================

nav_tool = AgentTool(agent=navigator_agent)
quarter_tool = AgentTool(agent=quartermaster_agent)
gunner_tool = AgentTool(agent=gunner_agent)
cook_tool = AgentTool(agent=cook_agent)
doctor_tool = AgentTool(agent=doctor_agent)

# =============================================================================
# 3. KAPITAN (Korzystający z narzędzi zamiast routingu)
# =============================================================================

root_agent = LlmAgent(
    model=MODEL,
    name="captain_with_tools",
    description="Kapitan korzystający ze swojej załogi jako narzędzi do zbierania informacji.",
    instruction="""Ahoj! Jesteś Kapitanem Czarnej Perły!

Twoim zadaniem jest odpowiadanie na pytania użytkownika.
Nie znasz wszystkich szczegółów operacyjnych statku, ale masz do dyspozycji swoją załogę, z której możesz korzystać jak z narzędzi:

- navigator_tool - nawigacja, mapy, trasy
- quartermaster_tool - zapasy, ładownia, naprawy
- gunner_tool - broń, taktyka, obrona
- cook_tool - jedzenie, picie, morale
- doctor_tool - zdrowie, leczenie rannych, szkorbut

Kiedy otrzymasz pytanie:
1. Zastanów się, kogo z załogi zapytać o szczegóły.
2. Użyj odpowiedniego narzędzia (lub KILKU NARZĘDZI po kolei!), aby wyciągnąć informacje od specjalisty.
3. Po otrzymaniu odpowiedzi od narzędzi, TY (Kapitan) formułujesz OSTATECZNĄ ODPOWIEDŹ do użytkownika, posługując się swoim kapitańskim autorytetem.
""",
    tools=[nav_tool, quarter_tool, gunner_tool, cook_tool, doctor_tool]
)

# =============================================================================
# PRZYKŁADY TESTOWANIA W ADK WEB
# =============================================================================
"""
Spróbuj zadać te pytania w interfejsie webowym:
1. "Kapitanie, ilu rannych po ostatniej bitwie możemy uleczyć?"
   (Kapitan wezwie narzędzie doctor_tool)
2. "Gdzie płyniemy i czy mamy wystarczająco rumu na drogę?"
   (Kapitan użyje nav_tool ORAZ quarter_tool/cook_tool i połączy to w jedną opowieść!)
"""
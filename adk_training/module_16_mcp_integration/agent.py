"""
Moduł 16: MCP Integration - ROZWIĄZANIE agent_solution.py
==========================================================
Pełne rozwiązanie z 4 serwerami MCP:
  #1 PublicAPIs  — kursy walut NBP, Pokemon, żarty
  #2 Weather     — pogoda + prognoza (wttr.in)
  #3 Space       — pozycja ISS, astronauci (zadanie 2)
  #4 Football    — tabele lig, info o drużynach, mecze (zadanie 3)
"""

import os
import sys
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioConnectionParams, StreamableHTTPConnectionParams
from mcp import StdioServerParameters

MODEL = "gemini-2.5-flash"
AGENT_NAME = "mcp_super_agent"

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_SERVERS_DIR = os.path.join(_THIS_DIR, "mcp_servers")
_PYTHON = sys.executable

# =============================================================================
# MCP #1 — Public APIs (kursy walut NBP, Pokemon, żarty)
# =============================================================================
api_tools = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=_PYTHON,
            args=[os.path.join(_SERVERS_DIR, "api_server.py")],
        ),
        timeout=30,
    )
)

# =============================================================================
# MCP #2 — Weather (pogoda + prognoza z wttr.in)
# =============================================================================
weather_tools = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=_PYTHON,
            args=[os.path.join(_SERVERS_DIR, "weather_server.py")],
        ),
        timeout=30,
    )
)

# =============================================================================
# MCP #3 — Space (pozycja ISS, astronauci na orbicie)
# =============================================================================
space_tools = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=_PYTHON,
            args=[os.path.join(_SERVERS_DIR, "space_server.py")],
        ),
        timeout=30,
    )
)

# =============================================================================
# MCP #4 — Football (tabele lig, info o drużynach, mecze)
# =============================================================================
football_tools = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=_PYTHON,
            args=[os.path.join(_SERVERS_DIR, "football_server.py")],
        ),
        timeout=30,
    )
)

# =============================================================================
# MCP #5 — Pirate Navigator (zdalny serwer MCP na Cloud Run)
# =============================================================================
pirate_tools = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://pirate-navigator-28948426345.us-central1.run.app/mcp",
        timeout=30,
    )
)

# =============================================================================
# PROMPT
# =============================================================================
instruction_prompt = """
Jesteś super-asystentem z wieloma źródłami danych MCP.

Twoje możliwości:
1. **Kursy walut** — aktualne kursy NBP (USD, EUR, CHF, GBP...)
2. **Pokemony** — statystyki dowolnego Pokemona
3. **Żarty** — losowe żarty (EN)
4. **Pogoda** — aktualna pogoda i prognoza na 3 dni
5. **Kosmos** — pozycja ISS, lista astronautów na orbicie
6. **Piłka nożna** — tabele lig (Ekstraklasa, Premier League, La Liga, Bundesliga,
   Serie A, Ligue 1, Champions League, Eredivisie), info o drużynach,
   najbliższe mecze, ostatnie wyniki

Zasady:
- Odpowiadaj po polsku
- Łącz dane z różnych źródeł, np. "pogoda w Madrycie + tabela La Liga"
- Bądź zwięzły i informatywny
- Gdy coś nie działa, poinformuj użytkownika
"""

# =============================================================================
# AGENT — 4 serwery MCP jednocześnie!
# =============================================================================
root_agent = LlmAgent(
    model=MODEL,
    name=AGENT_NAME,
    description="Super-asystent z 4 serwerami MCP (API, Weather, Space, Football).",
    instruction=instruction_prompt,
    tools=[
        api_tools,
        weather_tools,
        space_tools,
        football_tools,
        pirate_tools,
    ],
)

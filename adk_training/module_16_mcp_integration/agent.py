"""
Moduł 16: MCP Integration - Agent podłączony do wielu serwerów MCP
=====================================================================
Agent ADK działający jako klient MCP, podłączony jednocześnie do DWÓCH
niezależnych serwerów MCP (STDIO) + jednego zdalnego (HTTP):

  1. PublicAPIs  - kursy walut NBP, statystyki Pokemon, żarty     (STDIO)
  2. Weather     - aktualna pogoda i prognoza (wttr.in)            (STDIO)
  3. Pirate Navigator - zdalny serwer MCP na Cloud Run             (HTTP)

Cele edukacyjne:
- Tworzenie własnego serwera MCP (FastMCP + STDIO)
- Podłączenie agenta ADK do serwera MCP przez StdioConnectionParams
- Podłączenie wielu serwerów MCP do jednego agenta
- Podłączenie zdalnego serwera MCP przez StreamableHTTPConnectionParams
- Zrozumienie MCPToolset jako mostu ADK ↔ MCP

Uruchomienie:
    cd adk_training
    adk web module_16_mcp_integration
"""

import os
import sys
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioConnectionParams, StreamableHTTPConnectionParams
from mcp import StdioServerParameters

# =============================================================================
# KONFIGURACJA
# =============================================================================

MODEL = "gemini-2.5-flash"
AGENT_NAME = "mcp_multi_agent"

# Ścieżka do katalogu z serwerami MCP
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_SERVERS_DIR = os.path.join(_THIS_DIR, "mcp_servers")

# Python interpreter - ten sam co uruchamia agenta
_PYTHON = sys.executable

# =============================================================================
# MCP TOOLSET #1 — Public APIs (kursy walut, Pokemon, żarty)
# =============================================================================
# StdioConnectionParams uruchamia serwer MCP jako sub-proces.
# Agent komunikuje się z nim przez stdin/stdout (protokół MCP).
# timeout=30 — daje serwerowi 30s na start (Windows bywa wolniejszy).

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
# MCP TOOLSET #2 — Weather (pogoda z wttr.in)
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
# MCP TOOLSET #3 — Pirate Navigator (zdalny serwer MCP na Cloud Run)
# =============================================================================
# StreamableHTTPConnectionParams łączy się z MCP przez HTTP.
# Serwer działa zdalnie — nie wymaga lokalnego procesu.

pirate_tools = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://pirate-navigator-28948426345.us-central1.run.app/mcp",
        timeout=30,
    )
)

# =============================================================================
# PROMPT SYSTEMOWY
# =============================================================================

instruction_prompt = """
Jesteś uniwersalnym asystentem z dostępem do wielu narzędzi MCP.

Twoje możliwości:
1. **Kursy walut** — sprawdzasz aktualne kursy NBP (np. USD, EUR, CHF, GBP)
2. **Pokemony** — podajesz statystyki dowolnego Pokemona (wzrost, waga, typy)
3. **Żarty** — opowiadasz losowe żarty (po angielsku)
4. **Pogoda** — sprawdzasz aktualną pogodę i prognozę dla dowolnego miasta
5. **Pirate Navigator** — zdalny serwer MCP z Cloud Run (użyj jego narzędzi gdy pasują do pytania)

Zasady:
- Odpowiadaj po polsku (chyba że user pisze po angielsku)
- Gdy user pyta o pogodę - użyj narzędzi pogodowych
- Gdy user pyta o waluty - użyj narzędzia kursów NBP
- Gdy user pyta o Pokemona - użyj narzędzia Pokemon
- Możesz łączyć narzędzia w jednej odpowiedzi (np. pogoda + kurs waluty)
- Bądź zwięzły, ale informatywny
"""

# =============================================================================
# AGENT — podłączony do 3 serwerów MCP jednocześnie (2x STDIO + 1x HTTP)
# =============================================================================

root_agent = LlmAgent(
    model=MODEL,
    name=AGENT_NAME,
    description="Uniwersalny asystent z wieloma serwerami MCP (API + Weather + Pirate).",
    instruction=instruction_prompt,
    tools=[api_tools, weather_tools, pirate_tools],  # <-- 3 MCPToolset: 2 STDIO + 1 HTTP!
)

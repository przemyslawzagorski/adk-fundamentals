"""
Agent Solution - Code Analyst z Comarch MCP (Jira + GitLab + Wiki)
==================================================================
Rozszerzona wersja agenta z integracją firmowego MCP:
- Jira: odczyt ticketow, wyszukiwanie, tworzenie
- GitLab: projekty, MR, issues
- Wiki (Confluence): przeszukiwanie dokumentacji

Wymaga:
1. Dostep do sieci wew. Comarch (VPN/biuro)
2. npx + Node.js w PATH
3. Zmienne w .env: COMARCH_MCP_*, JIRA_*, WIKI_*, GITLAB_*
4. Certyfikat CA: GK_COMARCH_ROOT_CA.crt (sciezka w NODE_EXTRA_CA_CERTS)

Uruchomienie:
    adk web   (z katalogu module_13_code_analyst)
"""

import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import FunctionTool
from google.adk.tools.mcp_tool.mcp_toolset import (
    McpToolset,
    StdioConnectionParams,
    StdioServerParameters,
)

from code_retrieval_tool import search_code, index_project, get_index_stats

_module_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_module_dir, ".env"))

# =============================================================================
# CODE RAG TOOLS
# =============================================================================

tool_search_code = FunctionTool(func=search_code)
tool_index_project = FunctionTool(func=index_project)
tool_get_stats = FunctionTool(func=get_index_stats)

# =============================================================================
# COMARCH MCP TOOLSET (Jira + GitLab + Wiki)
# =============================================================================

# Certyfikat CA do komunikacji z serwerami Comarch
_ca_cert = os.environ.get(
    "NODE_EXTRA_CA_CERTS",
    os.path.expanduser(r"~\Documents\cert\GK_COMARCH_ROOT_CA.crt"),
)

comarch_mcp = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=[
                "--registry",
                os.environ.get(
                    "COMARCH_MCP_REGISTRY",
                    "https://nexus.czk.comarch/repository/ai-npm",
                ),
                "@comarch/mcp-integration-tool",
            ],
            env={
                # MCP transport
                "MCP_MODE": "stdio",
                # TLS / Certificates
                "NODE_EXTRA_CA_CERTS": _ca_cert,
                "NODE_TLS_REJECT_UNAUTHORIZED": "0",
                "HTTP_REJECT_UNAUTHORIZED": "false",
                # Jira
                "JIRA_BASE_URL": os.environ.get("JIRA_BASE_URL", ""),
                "JIRA_BEARER_TOKEN": os.environ.get("JIRA_BEARER_TOKEN", ""),
                # Wiki (Confluence)
                "WIKI_BASE_URL": os.environ.get("WIKI_BASE_URL", ""),
                "WIKI_BEARER_TOKEN": os.environ.get("WIKI_BEARER_TOKEN", ""),
                # GitLab
                "GITLAB_BASE_URL": os.environ.get("GITLAB_BASE_URL", ""),
                "GITLAB_TOKEN": os.environ.get("GITLAB_TOKEN", ""),
            },
        ),
        timeout=30.0,
    ),
)

# =============================================================================
# SUB-AGENCI
# =============================================================================

# Agent 1: Analityk kodu - przeszukuje zaindeksowany kod + Jira/Wiki
code_analyst = LlmAgent(
    name="code_analyst",
    model="gemini-2.0-flash",
    instruction="""Jestes ekspertem od analizy kodu i integracji z systemami firmy.

## Twoje narzedzia
- **search_code(query, top_k)** - semantyczne przeszukiwanie zaindeksowanego kodu
- **get_index_stats()** - statystyki indeksu
- **Narzedzia Jira** z MCP (np. wyszukiwanie ticketow, odczyt szczegolow)
- **Narzedzia Wiki** z MCP (np. przeszukiwanie dokumentacji Confluence)
- **Narzedzia GitLab** z MCP (np. przegladanie projektow, MR)

## Przepływ pracy
1. Jesli uzytkownik podaje ID ticketa - pobierz go z Jira
2. Uzyj search_code() z kluczowymi terminami z opisu problemu
3. Jesli wyniki niewystarczajace - przeformuluj zapytanie
4. Opcjonalnie przeszukaj Wiki po kontekst biznesowy
5. Podsumuj znalezione pliki i ich powiazanie z problemem
6. Wypisz sciezki plikow z numerami linii

## Zasady
- ZAWSZE cytuj sciezki plikow z wynikow RAG
- Odpowiadaj po polsku""",
    tools=[tool_search_code, tool_get_stats, comarch_mcp],
)

# Agent 2: Architekt rozwiazań - proponuje implementacje
solution_architect = LlmAgent(
    name="solution_architect",
    model="gemini-2.0-flash",
    instruction="""Jestes architektem oprogramowania. Na podstawie:
- Opisu problemu z ticketa (z kontekstu)
- Znalezionych fragmentow kodu (z poprzedniego kroku)

Przygotuj:
1. Krotki opis proponowanego rozwiazania
2. Diagram Mermaid (sequence, class lub flowchart)
3. Lista plikow do modyfikacji z opisem zmian
4. Proponowane stories z:
   - Tytul
   - Opis (2-3 zdania)
   - Acceptance Criteria (lista punktow)
   - Definition of Done
5. Estymacja: zlozonosc (S/M/L/XL), ryzyko regresji (niskie/srednie/wysokie)

Odpowiadaj po polsku. Badz konkretny - podaj nazwy klas, metod, plikow.""",
    tools=[comarch_mcp],
)

# =============================================================================
# ORCHESTRATOR - SequentialAgent
# =============================================================================

AGENT_APP_NAME = "code_analyst_full"

root_agent = SequentialAgent(
    name=AGENT_APP_NAME,
    sub_agents=[code_analyst, solution_architect],
    description="Pipeline: ticket Jira -> analiza kodu RAG -> propozycja z diagramami i stories",
)

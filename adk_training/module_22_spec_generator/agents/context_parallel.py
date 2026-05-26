"""ContextGatherer — ParallelAgent zbierajacy kontekst z wielu zrodel jednoczesnie.

Sub-agenty (opcjonalne, wlaczane na podstawie dostepnosci MCP/NotebookLM):
  - wiki_context_agent   (Confluence via MCP)
  - code_context_agent   (GitLab via MCP)
  - notebooklm_agent     (agent-as-tool, wlacza sie tylko gdy NOTEBOOKLM_ENABLED=1)
"""

from __future__ import annotations

from google.adk.agents import LlmAgent, ParallelAgent


_WIKI_INSTR = """Jestes researcherem. Uzyj narzedzi Wiki MCP aby znalezc artykuly
zwiazane z opisem ponizszego ticketu. Zwroc 3-5 najlepszych wycinkow (po 5-10 zdan kazdy),
z odnosnikiem do tytulu/URL artykulu. Jesli nic nie pasuje — zwroc 'brak trafien'.

--- TICKET ---
{ticket}
--- KONIEC TICKETU ---"""

_CODE_INSTR = """Jestes researcherem kodu. Uzyj narzedzi GitLab MCP aby znalezc pliki/commity
powiazane z funkcjonalnoscia opisana w ponizszym tickecie. Zwroc 3-5 sciezek z krotkim
streszczeniem ich roli. Jesli nic nie pasuje — 'brak trafien'.

--- TICKET ---
{ticket}
--- KONIEC TICKETU ---"""

_NOTEBOOKLM_INSTR = """Uzyj narzedzia notebooklm_query aby zapytac baze domenowa o kontekst
zwiazany z ponizszym ticketem. Sformuluj jedno konkretne pytanie po polsku zawierajace
kluczowe pojecia z ticketu (nazwy procesow, modulow, ekranow). NIE przekazuj zmiennych
typu 'state.ticket' jako pytania — wkomponuj realna tresc. Zwroc kluczowe definicje i zasady.

--- TICKET ---
{ticket}
--- KONIEC TICKETU ---"""


def build_context_parallel(
    wiki_tools: list | None = None,
    code_tools: list | None = None,
    notebooklm_tool=None,
    model=None,
) -> ParallelAgent:
    from config import get_settings
    s = get_settings()
    m = model if model is not None else s.llm_model
    sub_agents = []

    if wiki_tools:
        sub_agents.append(LlmAgent(
            name="wiki_context_agent",
            model=m,
            description="Szuka kontekstu w Confluence Wiki.",
            instruction=_WIKI_INSTR,
            tools=wiki_tools,
            output_key="wiki_context",
        ))

    if code_tools:
        sub_agents.append(LlmAgent(
            name="code_context_agent",
            model=m,
            description="Szuka powiazanego kodu w GitLab.",
            instruction=_CODE_INSTR,
            tools=code_tools,
            output_key="code_context",
        ))

    if notebooklm_tool is not None and s.notebooklm_enabled:
        sub_agents.append(LlmAgent(
            name="domain_context_agent",
            model=m,
            description="Wiedza domenowa z NotebookLM (opcjonalnie).",
            instruction=_NOTEBOOKLM_INSTR,
            tools=[notebooklm_tool],
            output_key="domain_context",
        ))

    if not sub_agents:
        # Fallback: jeden agent-stub aby pipeline nadal sie uruchomil
        sub_agents.append(LlmAgent(
            name="noop_context",
            model=m,
            description="Brak zrodel kontekstu (MCP/NotebookLM niedostepne).",
            instruction="Zwroc: 'BRAK ZEWNETRZNEGO KONTEKSTU'.",
            output_key="wiki_context",
        ))

    return ParallelAgent(
        name="context_gatherer",
        description="Zbiera kontekst z Wiki/GitLab/NotebookLM rownolegle.",
        sub_agents=sub_agents,
    )

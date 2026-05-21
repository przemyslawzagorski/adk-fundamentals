"""Context Gatherer — ParallelAgent zbierający kontekst równolegle z:
- Confluence (wiki_context_agent)
- NotebookLM (domain_context_agent — opcjonalnie)

Każdy sub-agent jest dodawany TYLKO gdy odpowiednie źródło jest skonfigurowane.
Gdy żadne źródło nie istnieje — fallback agent zwraca placeholder, żeby pipeline
nie wybuchł na braku kontekstu.
"""

from __future__ import annotations

import logging
import os
import re

from google.adk.agents import LlmAgent, ParallelAgent

from ..prompts.prompt_loader import load_prompt
from ..tools.confluence_tools import build_confluence_tools
from ..tools.notebooklm_tool import build_notebooklm_tool, is_enabled as _nblm_enabled

logger = logging.getLogger(__name__)

MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")


def _split_sub_instructions(full: str) -> dict[str, str]:
    """Z `context_researchers_pl.md` wyciąga sekcje per sub-agent (po '##')."""
    parts = re.split(r"^---\s*$", full, flags=re.MULTILINE)
    out: dict[str, str] = {}
    for part in parts:
        m = re.search(r"^##\s+(\w+)", part, flags=re.MULTILINE)
        if m:
            out[m.group(1)] = part.strip()
    return out


def build_context_parallel(model: str | None = None) -> ParallelAgent:
    m = model or MODEL
    instr = _split_sub_instructions(load_prompt("context_researchers_pl"))

    sub_agents: list[LlmAgent] = []

    confluence_tools = build_confluence_tools()
    if confluence_tools:
        sub_agents.append(
            LlmAgent(
                name="wiki_context_agent",
                model=m,
                description="Szuka kontekstu w Confluence DC przez CQL.",
                instruction=instr.get("wiki_context_agent", "Wyszukaj w Confluence kontekst do `state.ticket`."),
                tools=confluence_tools,
                output_key="wiki_context",
            )
        )

    if _nblm_enabled():
        notebooklm = build_notebooklm_tool()
        if notebooklm is not None:
            sub_agents.append(
                LlmAgent(
                    name="domain_context_agent",
                    model=m,
                    description="Wiedza domenowa z NotebookLM.",
                    instruction=instr.get("domain_context_agent", "Zapytaj NotebookLM o kontekst do `state.ticket`."),
                    tools=[notebooklm],
                    output_key="domain_context",
                )
            )

    if not sub_agents:
        # Fallback — pipeline musi mieć przynajmniej jedno wyjście kontekstu.
        sub_agents.append(
            LlmAgent(
                name="noop_context",
                model=m,
                description="Brak źródeł kontekstu (Confluence/NotebookLM nieskonfigurowane).",
                instruction=(
                    "Zwróć dokładnie: 'BRAK ZEWNĘTRZNEGO KONTEKSTU — skonfiguruj "
                    "CONFLUENCE_DC_BASE_URL/PAT lub NOTEBOOKLM_ENABLED=1 + NOTEBOOKLM_NOTEBOOK_URL.'"
                ),
                output_key="wiki_context",
            )
        )
        logger.info("context_gatherer: fallback (no Confluence, no NotebookLM)")

    return ParallelAgent(
        name="context_gatherer",
        description="Zbiera kontekst równolegle z Confluence i NotebookLM.",
        sub_agents=sub_agents,
    )

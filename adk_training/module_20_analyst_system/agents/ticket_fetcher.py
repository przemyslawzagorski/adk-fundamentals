"""Ticket Fetcher — pobiera ticket z Jira DC przez FunctionTool (jira_get_issue).

Output key: `ticket` (Markdown — gotowy blok kontekstu dla kolejnych agentów).
"""

from __future__ import annotations

import os

from google.adk.agents import LlmAgent

from ..prompts.prompt_loader import load_prompt
from ..tools.jira_tools import build_jira_tools

MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")


def build_ticket_fetcher(model: str | None = None) -> LlmAgent:
    """Buduje agenta pobierającego ticket. Tools = [] gdy Jira nieskonfigurowana
    (agent zwróci wtedy 'BRAK DOSTĘPU DO JIRA' zgodnie z promptem)."""
    return LlmAgent(
        name="ticket_fetcher",
        model=model or MODEL,
        description="Pobiera opis ticketu z Jira Data Center.",
        instruction=load_prompt("ticket_fetcher_pl"),
        tools=build_jira_tools(),
        output_key="ticket",
    )

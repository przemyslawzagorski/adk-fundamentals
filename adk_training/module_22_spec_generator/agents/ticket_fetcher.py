"""Ticket Fetcher — pobiera dane ticketu przez Comarch MCP (Jira)."""

from __future__ import annotations

from google.adk.agents import LlmAgent

from .prompt_loader import load_prompt


def build_ticket_fetcher(jira_tools: list | None = None, model=None) -> LlmAgent:
    """Zbuduj agenta pobierajacego ticket.

    Args:
        jira_tools: lista FunctionTool/MCPToolset.get_tools() dla Jira MCP.
                    None -> agent zwroci "MCP niedostepne".
        model: override modelu (BaseLlm) — uzywane w testach z FakeLlm.
    """
    from config import get_settings
    s = get_settings()
    return LlmAgent(
        name="ticket_fetcher",
        model=model if model is not None else s.llm_model,
        description="Pobiera opis ticketu z Jira (Comarch MCP).",
        instruction=load_prompt("ticket_fetcher_pl"),
        tools=jira_tools or [],
        output_key="ticket",
    )

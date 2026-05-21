"""Jira Publisher — publikuje zaakceptowane epiki do Jira via Comarch MCP."""

from __future__ import annotations

from google.adk.agents import LlmAgent


_INSTR = """Jestes agentem publikujacym epiki do Jira.

Wejscie (state):
  - state.epics_json: JSON z polem 'epics' (lista).
  - state.target_project: klucz projektu Jira (np. 'SANDBOX').
  - state.approved: MUSI byc True. Jesli False - NIE publikuj, zwroc komunikat.

Dla kazdego epika z listy:
  1. Wywolaj mcp__jira__create_issue(project=state.target_project, issuetype='Epic',
     summary=epic.title, description=epic.summary + AC, labels=epic.labels,
     priority=epic.priority).
  2. Zbierz zwrocone klucze (np. SANDBOX-123).

Zwroc raport:
```
Opublikowano:
- SANDBOX-123: <tytul>
- ...
```

Jesli dowolny krok sie nie uda - zwroc jawny komunikat o bledzie, NIE pomijaj cicho.
"""


def build_jira_publisher(jira_tools: list | None = None) -> LlmAgent:
    from config import get_settings
    s = get_settings()
    return LlmAgent(
        name="jira_publisher",
        model=s.llm_model,
        description="Publikuje zaakceptowane epiki do Jira.",
        instruction=_INSTR,
        tools=jira_tools or [],
        output_key="publish_report",
    )

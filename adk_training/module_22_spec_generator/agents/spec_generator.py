"""Spec Generator - factory top-level SequentialAgent.

Laczy: ticket_fetcher -> context_parallel -> hld_writer -> critique_loop -> epic_decomposer.

Krok 'HITL (approval)' + 'jira_publisher' sa **poza** tym SequentialAgent - obsluguje je
web UI po preview (czlowiek klika "Publikuj" -> osobne wywolanie jira_publisher).
"""

from __future__ import annotations

import json
import re
from typing import Optional

from google.adk.agents import SequentialAgent

from .context_parallel import build_context_parallel
from .critique_loop import build_critique_loop
from .epic_decomposer import build_epic_decomposer
from .hld_writer import build_hld_writer
from .ticket_fetcher import build_ticket_fetcher


_JSON_FENCE_RE = re.compile(
    r"^\s*```(?:json)?\s*\n(?P<body>.*?)\n```\s*$",
    re.DOTALL | re.IGNORECASE,
)


def parse_epics_json(raw: str | list | dict | None) -> list[dict]:
    """Elastyczny parser wyjscia epic_decomposer.

    Akceptuje:
      - list[dict]           -> zwraca as-is
      - dict z kluczem "epics" -> zwraca dict["epics"]
      - str z markdown fence ```json ... ``` -> stripuje fence i parsuje
      - str czysty JSON      -> parsuje
    Zwraca [] gdy nie udalo sie sparsowac lub wejscie jest puste.
    """
    if raw is None or raw == "":
        return []
    if isinstance(raw, list):
        return [e for e in raw if isinstance(e, dict)]
    if isinstance(raw, dict):
        epics = raw.get("epics", [])
        return [e for e in epics if isinstance(e, dict)]
    if not isinstance(raw, str):
        return []

    text = raw.strip()
    m = _JSON_FENCE_RE.match(text)
    if m:
        text = m.group("body").strip()

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return []

    if isinstance(parsed, list):
        return [e for e in parsed if isinstance(e, dict)]
    if isinstance(parsed, dict):
        epics = parsed.get("epics", [])
        return [e for e in epics if isinstance(e, dict)]
    return []


def build_spec_generator(
    jira_tools: list | None = None,
    wiki_tools: list | None = None,
    gitlab_tools: list | None = None,
    notebooklm_tool=None,
    enable_notebooklm: bool = False,
    max_critique_iterations: int | None = None,
    model_overrides: Optional[dict] = None,
) -> SequentialAgent:
    """Zbuduj pelny pipeline Spec Generator.

    Tools sa None gdy odpowiedni MCP nie jest skonfigurowany - agenty stuby beda dzialac,
    ale zwroca komunikaty 'brak danych' zamiast realnych wynikow.

    enable_notebooklm - gdy True i `notebooklm_tool` nie jest przekazany jawnie,
    probujemy zbudowac stub z `tools.notebooklm_tool.build_notebooklm_tool()`.

    model_overrides (testy z FakeLlm) - klucze:
      "ticket_fetcher", "context", "hld_writer",
      "critic", "reviser", "epic_decomposer".
    """
    mo = model_overrides or {}
    if notebooklm_tool is None and enable_notebooklm:
        # Import lokalny - unikamy circular / zbednego importu w testach offline.
        from tools.notebooklm_tool import build_notebooklm_tool
        notebooklm_tool = build_notebooklm_tool()
    return SequentialAgent(
        name="spec_generator",
        description="Ticket Jira -> HLD + Epiki (HITL przed publikacja).",
        sub_agents=[
            build_ticket_fetcher(
                jira_tools=jira_tools, model=mo.get("ticket_fetcher"),
            ),
            build_context_parallel(
                wiki_tools=wiki_tools,
                code_tools=gitlab_tools,
                notebooklm_tool=notebooklm_tool,
                model=mo.get("context"),
            ),
            build_hld_writer(model=mo.get("hld_writer")),
            build_critique_loop(
                max_iterations=max_critique_iterations,
                critic_model=mo.get("critic"),
                reviser_model=mo.get("reviser"),
            ),
            build_epic_decomposer(model=mo.get("epic_decomposer")),
        ],
    )

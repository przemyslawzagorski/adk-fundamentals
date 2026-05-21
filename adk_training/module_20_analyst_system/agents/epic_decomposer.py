"""Epic Decomposer — rozbija HLD na 3-7 epików Jira (JSON)."""

from __future__ import annotations

import json
import os
import re

from google.adk.agents import LlmAgent

from ..prompts.prompt_loader import load_prompt

MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")


def build_epic_decomposer(model: str | None = None) -> LlmAgent:
    return LlmAgent(
        name="epic_decomposer",
        model=model or MODEL,
        description="Rozbija zaakceptowany HLD na 3-7 epików Jira (JSON).",
        instruction=load_prompt("epic_decomposer_pl"),
        output_key="epics_json",
    )


_JSON_FENCE_RE = re.compile(
    r"^\s*```(?:json)?\s*\n(?P<body>.*?)\n```\s*$",
    re.DOTALL | re.IGNORECASE,
)


def parse_epics_json(raw: str | list | dict | None) -> list[dict]:
    """Elastyczny parser wyjścia epic_decomposer.

    Akceptuje: list[dict], dict z kluczem 'epics', str z fence ```json...```
    lub czysty JSON. Zwraca [] przy błędzie/pustym wejściu.
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

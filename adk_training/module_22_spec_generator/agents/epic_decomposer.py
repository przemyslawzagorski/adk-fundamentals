"""Epic Decomposer — rozbija HLD na epiki Jira (JSON)."""

from __future__ import annotations

from typing import Any

from google.adk.agents import LlmAgent

from .prompt_loader import load_prompt


def build_epic_decomposer(model: Any = None) -> LlmAgent:
    from config import get_settings
    s = get_settings()
    return LlmAgent(
        name="epic_decomposer",
        model=model if model is not None else s.llm_model,
        description="Rozbija zaakceptowany HLD na 3-7 epikow Jira w formacie JSON.",
        instruction=load_prompt("epic_decomposer_pl"),
        output_key="epics_json",
    )

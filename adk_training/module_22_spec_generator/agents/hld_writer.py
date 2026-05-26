"""HLD Writer — LlmAgent generujacy pierwsza wersje HLD."""

from __future__ import annotations

from typing import Any

from google.adk.agents import LlmAgent

from .prompt_loader import load_prompt


def build_hld_writer(model: Any = None) -> LlmAgent:
    from config import get_settings
    s = get_settings()
    return LlmAgent(
        name="hld_writer",
        model=model if model is not None else s.llm_model,
        description="Tworzy pierwsza wersje HLD z ticketu + kontekstu.",
        instruction=load_prompt("hld_pl"),
        output_key="current_hld",
    )

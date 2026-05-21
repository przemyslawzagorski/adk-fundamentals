"""HLD Writer — pierwsza wersja dokumentu HLD (Markdown)."""

from __future__ import annotations

import os

from google.adk.agents import LlmAgent

from ..prompts.prompt_loader import load_prompt

MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")


def build_hld_writer(model: str | None = None) -> LlmAgent:
    return LlmAgent(
        name="hld_writer",
        model=model or MODEL,
        description="Tworzy pierwszą wersję HLD z ticketu i kontekstu.",
        instruction=load_prompt("hld_writer_pl"),
        output_key="current_hld",
    )

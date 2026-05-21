"""
ADK / Google Gemini provider adapter.
======================================

Uses ``google.genai`` directly for simple text-in/text-out calls.
Ideal for lightweight tasks where the Auggie orchestration overhead
is unnecessary (e.g. quick Q&A, summarisation).

Config via env:
  AGENT_MODEL   — model name (default: gemini-2.5-flash)
  GOOGLE_API_KEY — Gemini API key
"""

from __future__ import annotations

import json
import logging
import os
import time
from contextlib import contextmanager
from typing import Any, Callable, Iterator

from .base import (
    AgentCapabilities,
    AgentSession,
    BaseSession,
    ProviderUnavailable,
    RunResult,
)

logger = logging.getLogger(__name__)


def _import_genai():
    try:
        from google import genai
        return genai
    except ImportError as e:
        raise ProviderUnavailable(
            "Package 'google-genai' is not installed. Run: pip install google-genai"
        ) from e


class AdkSession(BaseSession):
    """Multi-turn session using google.genai chat."""

    def __init__(self, chat: Any, model: str) -> None:
        super().__init__()
        self._chat = chat
        self._model = model

    def run(self, prompt: str, *, return_type: type | None = None) -> RunResult:
        t0 = time.perf_counter()
        response = self._chat.send_message(prompt)
        duration = time.perf_counter() - t0
        raw_text = response.text or ""
        output: Any = raw_text
        if return_type and return_type is not str:
            output = _parse_structured(raw_text, return_type)
        return RunResult(
            output=output, raw_text=raw_text, duration_s=duration,
            model=self._model, provider="adk",
        )


class AdkProvider:
    """Google Gemini direct adapter — lightweight, fast, cheap.

    No workspace access, no success_criteria, no auggie orchestration.
    Good for: summarisation, classification, simple Q&A.
    """

    name = "adk"
    capabilities = AgentCapabilities(
        structured_returns=False,
        success_criteria=False,
        function_calling=False,
        session_context=True,
        workspace_access=False,
        streaming=True,
    )

    def run(
        self,
        prompt: str,
        *,
        return_type: type | None = None,
        success_criteria: list[str] | None = None,
        max_verification_rounds: int = 3,
        functions: list[Callable] | None = None,
        timeout: int = 180,
        extra_cli: list[str] | None = None,
        workspace_override: str | None = None,
    ) -> RunResult:
        genai = _import_genai()
        model = os.getenv("AGENT_MODEL", os.getenv("GOOGLE_MODEL", "gemini-2.5-flash"))
        client = genai.Client()
        t0 = time.perf_counter()
        response = client.models.generate_content(model=model, contents=prompt)
        duration = time.perf_counter() - t0
        raw_text = response.text or ""
        output: Any = raw_text
        if return_type and return_type is not str:
            output = _parse_structured(raw_text, return_type)
        return RunResult(
            output=output, raw_text=raw_text, duration_s=duration,
            model=model, provider="adk",
        )

    @contextmanager
    def session(self, **kwargs) -> Iterator[AgentSession]:
        genai = _import_genai()
        model = os.getenv("AGENT_MODEL", os.getenv("GOOGLE_MODEL", "gemini-2.5-flash"))
        client = genai.Client()
        chat = client.chats.create(model=model)
        yield AdkSession(chat, model)

    def close(self) -> None:
        pass


def _parse_structured(raw_text: str, return_type: type) -> Any:
    """Best-effort JSON → dataclass/dict parsing."""
    import re
    txt = raw_text.strip()
    if txt.startswith("```"):
        txt = re.sub(r"^```[a-zA-Z]*\n?", "", txt)
        txt = re.sub(r"\n?```$", "", txt)
    try:
        data = json.loads(txt)
    except json.JSONDecodeError:
        return raw_text
    if hasattr(return_type, "__dataclass_fields__"):
        try:
            return return_type(**data)
        except (TypeError, ValueError):
            return data
    return data

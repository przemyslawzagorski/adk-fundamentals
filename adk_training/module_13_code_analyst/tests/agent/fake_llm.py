"""
FakeLlm - skryptowany BaseLlm do testow agentowych bez Vertex/Gemini.

Uzycie:
    fake = FakeLlm(name="fake-analyst", script=[
        call("search_code", query="architektura"),
        say("Znalazlem: main.py linia 1 - entrypoint."),
    ])
    agent = LlmAgent(name="code_analyst", model=fake, tools=[...])
    # Runner ADK wywola generate_content_async - FakeLlm po kolei zwraca
    # zaprogramowane odpowiedzi (function_call lub text).

Dzialanie:
    - Kazde wywolanie generate_content_async konsumuje jedna "klatke" ze
      skryptu.
    - call(name, **args) -> LlmResponse z function_call (Runner wywola tool,
      dostarczy function_response, potem znowu wywola LLM).
    - say(text) -> LlmResponse z finalnym tekstem (koniec tury agenta).
    - Jesli skrypt jest pusty - zwracamy "(fake: brak skryptu)" jako finalna
      odpowiedz (agent zakonczy ture, nie bedzie petli).
"""

from __future__ import annotations

from typing import Any, AsyncGenerator, Optional
from uuid import uuid4

from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types


# --- DSL ------------------------------------------------------------------

def call(tool_name: str, **args: Any) -> dict:
    """Jedna klatka skryptu: agent chce wywolac tool `tool_name` z `args`."""
    return {"kind": "call", "tool": tool_name, "args": args}


def say(text: str) -> dict:
    """Jedna klatka skryptu: agent konczy ture textem `text`."""
    return {"kind": "say", "text": text}


# --- FakeLlm --------------------------------------------------------------

class FakeLlm(BaseLlm):
    """Skryptowany BaseLlm. NIE laczy sie z zadnym prawdziwym API."""

    # BaseLlm wymaga pola `model` (string). Ustawiamy sentinel.
    script: list[dict] = []
    _cursor: int = 0
    name: str = "fake"
    calls_log: list[dict] = []

    @classmethod
    def supported_models(cls) -> list[str]:
        return [r"^fake-.*$"]

    async def generate_content_async(
        self, llm_request: LlmRequest, stream: bool = False
    ) -> AsyncGenerator[LlmResponse, None]:
        # Zarejestruj co agent "wyslal" do LLM (dla asercji)
        self.calls_log.append({
            "contents_count": len(llm_request.contents or []),
            "tools": [
                t.name
                for t in (getattr(llm_request.config, "tools", None) or [])
                if hasattr(t, "name")
            ] if getattr(llm_request, "config", None) else [],
        })

        if self._cursor >= len(self.script):
            # Koniec skryptu - zamykamy ture
            yield _text_response(f"(fake-{self.name}: koniec skryptu)")
            return

        frame = self.script[self._cursor]
        self._cursor += 1

        if frame["kind"] == "call":
            yield _function_call_response(frame["tool"], frame["args"])
        elif frame["kind"] == "say":
            yield _text_response(frame["text"])
        else:  # pragma: no cover
            raise ValueError(f"Nieznany typ klatki: {frame}")


# --- Helpers --------------------------------------------------------------

def _text_response(text: str) -> LlmResponse:
    return LlmResponse(
        content=types.Content(
            role="model",
            parts=[types.Part(text=text)],
        ),
        partial=False,
        turn_complete=True,
    )


def _function_call_response(name: str, args: dict) -> LlmResponse:
    return LlmResponse(
        content=types.Content(
            role="model",
            parts=[
                types.Part(
                    function_call=types.FunctionCall(
                        id=f"call-{uuid4().hex[:8]}",
                        name=name,
                        args=args or {},
                    )
                )
            ],
        ),
        partial=False,
        turn_complete=True,
    )

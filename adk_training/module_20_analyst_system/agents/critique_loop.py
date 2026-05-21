"""Critique Loop — LoopAgent(critic -> escalation_check -> reviser).

Wzorzec self-critique with exit signal (ADK best practice):
- critic LlmAgent zapisuje feedback w state.critic_feedback
- EscalationChecker eskaluje (kończy loop) gdy feedback startuje od 'LGTM'
- reviser LlmAgent aktualizuje state.current_hld

Max iteracji konfigurowalny przez ANALYST_MAX_CRITIQUE_ITERATIONS (default 3, zakres 1..5).
"""

from __future__ import annotations

import logging
import os
from typing import AsyncGenerator

from google.adk.agents import BaseAgent, LlmAgent, LoopAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions

from ..prompts.prompt_loader import load_prompt

logger = logging.getLogger(__name__)

MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")
LGTM_TOKEN = "LGTM"


class EscalationChecker(BaseAgent):
    """Patrzy na ostatni feedback critica — jeśli 'LGTM' eskaluje (kończy loop)."""

    def __init__(self, name: str = "escalation_checker", feedback_key: str = "critic_feedback"):
        super().__init__(name=name)
        # BaseAgent (pydantic) — bypass walidacji dla pól runtime
        object.__setattr__(self, "_feedback_key", feedback_key)

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        feedback = (ctx.session.state.get(self._feedback_key) or "").strip()
        if feedback.upper().startswith(LGTM_TOKEN):
            logger.info("critique_loop: LGTM — escalating to end loop.")
            yield Event(author=self.name, actions=EventActions(escalate=True))
        else:
            yield Event(author=self.name)


def build_critic(model: str | None = None) -> LlmAgent:
    return LlmAgent(
        name="critic",
        model=model or MODEL,
        description="Ocenia HLD i wskazuje braki lub zwraca LGTM.",
        instruction=load_prompt("critic_pl"),
        output_key="critic_feedback",
    )


def build_reviser(model: str | None = None) -> LlmAgent:
    return LlmAgent(
        name="reviser",
        model=model or MODEL,
        description="Poprawia HLD wg uwag critica.",
        instruction=load_prompt("reviser_pl"),
        output_key="current_hld",
    )


def build_critique_loop(
    max_iterations: int | None = None,
    *,
    critic_model: str | None = None,
    reviser_model: str | None = None,
) -> LoopAgent:
    n_default = int(os.getenv("ANALYST_MAX_CRITIQUE_ITERATIONS", "3"))
    n = max(1, min(int(max_iterations or n_default), 5))
    return LoopAgent(
        name="critique_loop",
        description=f"Samokrytyka HLD (max {n} iteracji, exit po 'LGTM').",
        sub_agents=[
            build_critic(model=critic_model),
            EscalationChecker(),
            build_reviser(model=reviser_model),
        ],
        max_iterations=n,
    )

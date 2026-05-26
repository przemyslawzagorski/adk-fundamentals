"""Critique loop: LoopAgent(critic -> reviser) z escalation po 'LGTM'.

Wzorzec 'self-critique with exit signal' (ADK best practice):
- critic_agent  zapisuje w state.critic_feedback.
- escalation_checker  jesli feedback == 'LGTM' -> actions.escalate = True.
- reviser_agent  poprawia HLD i zapisuje w state.current_hld.

Max iteracji sterowany przez SPEC_GEN_MAX_CRITIQUE_ITERATIONS (default 3).
"""

from __future__ import annotations

from typing import AsyncGenerator

from google.adk.agents import BaseAgent, LlmAgent, LoopAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions

from .prompt_loader import load_prompt


LGTM_TOKEN = "LGTM"


class EscalationChecker(BaseAgent):
    """Patrzy na ostatni feedback critica — jesli 'LGTM' eskaluje (konczy loop)."""

    def __init__(self, name: str = "escalation_checker", feedback_key: str = "critic_feedback"):
        super().__init__(name=name)
        # pydantic-based BaseAgent - uzywamy model_config allow extra w BaseAgent
        object.__setattr__(self, "_feedback_key", feedback_key)

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        feedback = (ctx.session.state.get(self._feedback_key) or "").strip()
        if feedback.upper().startswith(LGTM_TOKEN):
            yield Event(
                author=self.name,
                actions=EventActions(escalate=True),
            )
        else:
            # pusty event — loop kontynuuje
            yield Event(author=self.name)


def build_critic(model=None) -> LlmAgent:
    """LlmAgent-critic zapisujacy swoja odpowiedz do state.critic_feedback."""
    from config import get_settings  # lazy aby nie wymagac ENV przy samym imporcie modulu
    s = get_settings()
    return LlmAgent(
        name="critic",
        model=model if model is not None else s.llm_model,
        description="Ocenia HLD i wskazuje braki lub zwraca LGTM.",
        instruction=load_prompt("critic_pl"),
        output_key="critic_feedback",
    )


def build_reviser(model=None) -> LlmAgent:
    """LlmAgent-reviser aktualizujacy state.current_hld."""
    from config import get_settings
    s = get_settings()
    return LlmAgent(
        name="reviser",
        model=model if model is not None else s.llm_model,
        description="Poprawia HLD wg uwag critica.",
        instruction=load_prompt("reviser_pl"),
        output_key="current_hld",
    )


def build_critique_loop(
    max_iterations: int | None = None,
    critic_model=None,
    reviser_model=None,
) -> LoopAgent:
    """Zbuduj LoopAgent dla samokrytyki HLD.

    Args:
        max_iterations: override na settings.max_critique_iterations (3..5).
        critic_model / reviser_model: override BaseLlm (testy z FakeLlm).
    """
    from config import get_settings
    s = get_settings()
    n = max_iterations if max_iterations is not None else s.max_critique_iterations
    n = max(1, min(int(n), 10))

    return LoopAgent(
        name="critique_loop",
        description=f"Samokrytyka HLD (max {n} iteracji, wyjscie po 'LGTM').",
        sub_agents=[
            build_critic(model=critic_model),
            EscalationChecker(),
            build_reviser(model=reviser_model),
        ],
        max_iterations=n,
    )

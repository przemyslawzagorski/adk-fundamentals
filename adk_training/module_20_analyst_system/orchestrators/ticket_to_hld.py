"""Orchestrator: Ticket -> HLD -> Epiki.

Pipeline (SequentialAgent):
    ticket_fetcher -> context_gatherer (Parallel) -> hld_writer -> critique_loop -> epic_decomposer

HITL (akceptacja człowieka) i publikacja epików są POZA tym pipeline'em — obsługuje je
warstwa REST `/api/analyst/*` po preview.

ENV:
    ANALYST_MAX_CRITIQUE_ITERATIONS  default 3 (1..5)
"""

from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from google.adk.agents import SequentialAgent

from ..agents.context_gatherer import build_context_parallel
from ..agents.critique_loop import build_critique_loop
from ..agents.epic_decomposer import build_epic_decomposer
from ..agents.hld_writer import build_hld_writer
from ..agents.ticket_fetcher import build_ticket_fetcher

_module_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_module_dir, "..", ".env"))

logger = logging.getLogger(__name__)


def build_ticket_to_hld_orchestrator(
    *,
    max_critique_iterations: int | None = None,
    model: str | None = None,
) -> SequentialAgent:
    """Pełny pipeline. Wszystkie sub-agenty współdzielą `model`, jeśli podano."""
    return SequentialAgent(
        name="ticket_to_hld",
        description="Pipeline: Jira ticket -> HLD (z self-critique) -> 3-7 epików (JSON).",
        sub_agents=[
            build_ticket_fetcher(model=model),
            build_context_parallel(model=model),
            build_hld_writer(model=model),
            build_critique_loop(
                max_iterations=max_critique_iterations,
                critic_model=model,
                reviser_model=model,
            ),
            build_epic_decomposer(model=model),
        ],
    )


# Eksportowany singleton dla AgentTool w root agencie
ticket_to_hld_orchestrator = build_ticket_to_hld_orchestrator()

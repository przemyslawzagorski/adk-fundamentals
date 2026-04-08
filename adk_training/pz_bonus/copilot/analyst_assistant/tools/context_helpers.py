"""
Context helper tools for the Analyst Assistant.

Note on HITL in LoopAgent context:
  clarify_with_user() is available to the ORCHESTRATOR for multi-turn clarification
  before delegating to a pipeline. It should NOT be used inside a LoopAgent writer
  because the writer's output goes to output_key (session state), not to the chat UI.
  The orchestrator handles clarification naturally via LLM conversation.
"""

import logging

logger = logging.getLogger(__name__)


def clarify_with_user(question: str) -> str:
    """
    Ask the user a targeted clarifying question before proceeding.

    Use this at the ORCHESTRATOR level when context is ambiguous or incomplete.
    The orchestrator should present this question to the user and wait for a reply
    in the next conversation turn before delegating to a pipeline.

    Args:
        question: A specific, focused question for the user.

    Returns:
        The question formatted for display to the user.
    """
    logger.info(f"[HITL] Clarification requested: {question}")
    return (
        f"❓ **Potrzebuję dodatkowej informacji przed wygenerowaniem dokumentu:**\n\n"
        f"{question}\n\n"
        f"Proszę o odpowiedź — po jej uzyskaniu wygeneruję dokument."
    )


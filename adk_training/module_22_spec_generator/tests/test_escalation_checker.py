"""Testy offline EscalationChecker (nie wymagaja LLM)."""

from __future__ import annotations

import pytest

from google.adk.agents.invocation_context import InvocationContext
from google.adk.sessions import InMemorySessionService, Session

from agents.critique_loop import EscalationChecker, LGTM_TOKEN


class _FakeCtx:
    """Minimalny duck-typed InvocationContext dla EscalationChecker."""
    def __init__(self, state: dict):
        class _Sess:
            pass
        self.session = _Sess()
        self.session.state = state


async def _drain(agen):
    events = []
    async for ev in agen:
        events.append(ev)
    return events


async def test_escalation_checker_escalates_on_lgtm():
    checker = EscalationChecker()
    ctx = _FakeCtx({"critic_feedback": "LGTM"})
    events = await _drain(checker._run_async_impl(ctx))
    assert len(events) == 1
    assert events[0].actions is not None
    assert events[0].actions.escalate is True


async def test_escalation_checker_escalates_on_lgtm_with_trailing_text():
    checker = EscalationChecker()
    ctx = _FakeCtx({"critic_feedback": "LGTM - gotowe do akceptacji"})
    events = await _drain(checker._run_async_impl(ctx))
    assert events[0].actions.escalate is True


async def test_escalation_checker_continues_on_changes_required():
    checker = EscalationChecker()
    ctx = _FakeCtx({"critic_feedback": "ZMIANY WYMAGANE:\n1. dodaj sekcje NFR"})
    events = await _drain(checker._run_async_impl(ctx))
    assert len(events) == 1
    # brak escalate albo False
    actions = events[0].actions
    assert actions is None or not actions.escalate


async def test_escalation_checker_continues_on_empty_feedback():
    checker = EscalationChecker()
    ctx = _FakeCtx({})  # brak klucza
    events = await _drain(checker._run_async_impl(ctx))
    assert len(events) == 1
    actions = events[0].actions
    assert actions is None or not actions.escalate

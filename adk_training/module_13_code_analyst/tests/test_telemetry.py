"""Testy telemetrii LLM."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from telemetry import (
    LlmEvent,
    TelemetryCollector,
    estimate_cost_usd,
    make_model_callbacks,
)


def test_cost_estimation_gemini_flash():
    # 1M in + 0.5M out @ 0.10/0.40 -> 0.10 + 0.20 = 0.30 USD
    cost = estimate_cost_usd("gemini-2.0-flash", 1_000_000, 500_000)
    assert abs(cost - 0.30) < 1e-6


def test_cost_estimation_unknown_model_uses_default():
    cost = estimate_cost_usd("unknown-model-xyz", 1_000_000, 0)
    # default input = 0.30
    assert abs(cost - 0.30) < 1e-6


def test_collector_records_and_summary(tmp_path: Path):
    db = tmp_path / "telemetry.db"
    col = TelemetryCollector(db_path=db)

    col.record(LlmEvent(
        ts=time.time(), agent="a", model="gemini-2.0-flash",
        prompt_tokens=1000, completion_tokens=500,
        total_tokens=1500, latency_ms=120.0,
        cost_usd=estimate_cost_usd("gemini-2.0-flash", 1000, 500),
    ))
    col.record(LlmEvent(
        ts=time.time(), agent="a", model="gemini-2.0-flash",
        prompt_tokens=2000, completion_tokens=100,
        total_tokens=2100, latency_ms=80.0,
        cost_usd=estimate_cost_usd("gemini-2.0-flash", 2000, 100),
    ))

    s = col.summary(since_hours=1)
    assert s["calls"] == 2
    assert s["prompt_tokens"] == 3000
    assert s["completion_tokens"] == 600
    assert s["cost_usd"] > 0
    assert len(s["by_model"]) == 1
    assert s["by_model"][0]["model"] == "gemini-2.0-flash"


def test_make_model_callbacks_returns_pair(tmp_path: Path):
    col = TelemetryCollector(db_path=tmp_path / "t.db")
    before, after = make_model_callbacks(col, agent_name="x")
    assert callable(before)
    assert callable(after)


def test_callback_records_event_when_invoked(tmp_path: Path):
    """Symulacja wywolania callbackow bez realnego ADK."""
    col = TelemetryCollector(db_path=tmp_path / "t.db")
    before, after = make_model_callbacks(col, agent_name="tester")

    # Pseudo-LlmRequest i LlmResponse (duck-typed)
    class FakeUsage:
        prompt_token_count = 123
        candidates_token_count = 45
        total_token_count = 168

    class FakeResponse:
        usage_metadata = FakeUsage()
        model_version = "gemini-2.0-flash"
        error_code = None

    class FakeCtx:
        model_name = "gemini-2.0-flash"

    fake_req = object()
    fake_resp = FakeResponse()

    before(FakeCtx(), fake_req)
    time.sleep(0.01)
    after(FakeCtx(), fake_resp)

    s = col.summary(since_hours=1)
    assert s["calls"] == 1
    assert s["prompt_tokens"] == 123
    assert s["completion_tokens"] == 45
    assert s["cost_usd"] > 0

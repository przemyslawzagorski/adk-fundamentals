"""Tests for safety primitives — disclaimer, allowlist guard, rate limiter."""
from __future__ import annotations

import asyncio
import time

import pytest

from adk_training.module_24_audit_ops.config import AuditConfig
from adk_training.module_24_audit_ops.safety import (
    DisclaimerAck,
    RateLimiter,
    SafetyError,
    assert_disclaimer,
    assert_url_allowed,
    runtime_guard,
)


def _cfg(tmp_path, **over):
    cfg = AuditConfig(artifacts_dir=tmp_path)
    for k, v in over.items():
        setattr(cfg, k, v)
    return cfg


def test_assert_disclaimer_required(tmp_path):
    cfg = _cfg(tmp_path, require_disclaimer=True)
    with pytest.raises(SafetyError):
        assert_disclaimer(None, cfg)
    with pytest.raises(SafetyError):
        assert_disclaimer(DisclaimerAck(acknowledged=False), cfg)
    # Acknowledged passes
    assert_disclaimer(DisclaimerAck(acknowledged=True), cfg)


def test_assert_disclaimer_disabled(tmp_path):
    cfg = _cfg(tmp_path, require_disclaimer=False)
    # Should NOT raise even with no ack
    assert_disclaimer(None, cfg)


def test_assert_url_allowed_scheme(tmp_path):
    cfg = _cfg(tmp_path, allowed_domains=[])
    with pytest.raises(SafetyError, match="scheme"):
        assert_url_allowed("file:///etc/passwd", cfg)
    with pytest.raises(SafetyError, match="scheme"):
        assert_url_allowed("javascript:alert(1)", cfg)


def test_assert_url_allowed_no_host(tmp_path):
    cfg = _cfg(tmp_path, allowed_domains=[])
    with pytest.raises(SafetyError):
        assert_url_allowed("http:///path", cfg)


def test_assert_url_allowed_allowlist(tmp_path):
    cfg = _cfg(tmp_path, allowed_domains=["example.com"])
    assert_url_allowed("https://example.com/x", cfg)
    assert_url_allowed("https://api.example.com/x", cfg)
    with pytest.raises(SafetyError):
        assert_url_allowed("https://evil.test/x", cfg)


def test_runtime_guard_combines(tmp_path):
    cfg = _cfg(tmp_path, allowed_domains=["example.com"], require_disclaimer=True)
    ack = DisclaimerAck(acknowledged=True, target_url="https://example.com/")
    runtime_guard("https://example.com/", cfg, ack)
    with pytest.raises(SafetyError):
        runtime_guard("https://example.com/", cfg, None)
    with pytest.raises(SafetyError):
        runtime_guard("https://evil.test/", cfg, ack)


@pytest.mark.asyncio
async def test_rate_limiter_enforces_minimum_gap():
    rl = RateLimiter(rps=10.0)  # 0.1s between actions
    t0 = time.monotonic()
    for _ in range(3):
        await rl.wait()
    elapsed = time.monotonic() - t0
    # 3 awaits => first immediate, two more gated. Expected >= ~0.18s
    assert elapsed >= 0.15


@pytest.mark.asyncio
async def test_rate_limiter_concurrent_callers_serialised():
    rl = RateLimiter(rps=20.0)
    t0 = time.monotonic()
    await asyncio.gather(*(rl.wait() for _ in range(4)))
    # 4 calls at 20 rps => >= 0.15s for the last 3 to be spaced out
    elapsed = time.monotonic() - t0
    assert elapsed >= 0.10

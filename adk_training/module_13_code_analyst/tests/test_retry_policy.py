"""Testy retry/backoff policy."""

from __future__ import annotations

import asyncio

import pytest

from retry_policy import is_retryable_error, retry_call


class FakeApiError(Exception):
    def __init__(self, status_code: int, msg: str = ""):
        super().__init__(msg or f"HTTP {status_code}")
        self.status_code = status_code


def test_is_retryable_429():
    assert is_retryable_error(FakeApiError(429))


def test_is_retryable_500_502_503_504():
    assert is_retryable_error(FakeApiError(500))
    assert is_retryable_error(FakeApiError(502))
    assert is_retryable_error(FakeApiError(503))
    assert is_retryable_error(FakeApiError(504))


def test_is_not_retryable_400_401_403_404():
    assert not is_retryable_error(FakeApiError(400))
    assert not is_retryable_error(FakeApiError(401))
    assert not is_retryable_error(FakeApiError(403))
    assert not is_retryable_error(FakeApiError(404))


def test_is_retryable_timeout():
    assert is_retryable_error(asyncio.TimeoutError())


def test_is_retryable_by_message():
    assert is_retryable_error(Exception("Deadline exceeded"))
    assert is_retryable_error(Exception("rate limit reached"))
    assert is_retryable_error(Exception("Service temporarily unavailable"))


async def test_retry_call_succeeds_on_second_attempt():
    attempts = {"n": 0}

    async def call():
        attempts["n"] += 1
        if attempts["n"] < 2:
            raise FakeApiError(503)
        return "ok"

    result = await retry_call(call, max_attempts=3, base_delay=0.01, jitter=0)
    assert result == "ok"
    assert attempts["n"] == 2


async def test_retry_call_gives_up_after_max_attempts():
    attempts = {"n": 0}

    async def call():
        attempts["n"] += 1
        raise FakeApiError(503)

    with pytest.raises(FakeApiError):
        await retry_call(call, max_attempts=3, base_delay=0.01, jitter=0)
    assert attempts["n"] == 3


async def test_retry_call_does_not_retry_non_retryable():
    attempts = {"n": 0}

    async def call():
        attempts["n"] += 1
        raise FakeApiError(401)

    with pytest.raises(FakeApiError):
        await retry_call(call, max_attempts=5, base_delay=0.01, jitter=0)
    assert attempts["n"] == 1


async def test_retry_call_with_custom_predicate():
    attempts = {"n": 0}

    async def call():
        attempts["n"] += 1
        raise ValueError("wanted")

    with pytest.raises(ValueError):
        await retry_call(
            call, max_attempts=4, base_delay=0.01, jitter=0,
            retry_on=lambda e: "wanted" in str(e),
        )
    assert attempts["n"] == 4

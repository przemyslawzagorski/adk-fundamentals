"""
Resilience layer — retry z exponential backoff + circuit breaker.

- **Retry**: powtórz N razy z rosnącym opóźnieniem (1s, 2s, 4s, ...).
  NIE retryjuj błędów konfiguracyjnych (auth, missing CLI) — szybki fail.
- **Circuit breaker**: po K kolejnych failach otwórz obwód na T sekund —
  nowe wywołania od razu rzucają wyjątek (ochrona przed kaskadą).

Stosowane w `auggie_factory.auggie_call()` — przezroczyste dla narzędzi.
"""

from __future__ import annotations

import logging
import os
import random
import time
from dataclasses import dataclass
from threading import Lock
from typing import Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


# =============================================================================
# RETRY
# =============================================================================
NON_RETRIABLE = (
    "AuggieUnavailable",         # SDK not installed
    "FileNotFoundError",         # CLI not found
    "PermissionError",
    "AugmentAuthenticationError",
    "AugmentValidationError",
)


def is_retriable(exc: BaseException) -> bool:
    name = type(exc).__name__
    if name in NON_RETRIABLE:
        return False
    msg = str(exc).lower()
    if "401" in msg or "403" in msg or "not authenticated" in msg:
        return False
    return True


def retry_with_backoff(
    fn: Callable[[], T],
    *,
    max_attempts: int = 3,
    base_delay_s: float = 1.0,
    max_delay_s: float = 8.0,
) -> T:
    last_exc: BaseException | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001
            last_exc = e
            if not is_retriable(e) or attempt == max_attempts:
                raise
            delay = min(base_delay_s * (2 ** (attempt - 1)), max_delay_s)
            jitter = random.uniform(0, delay * 0.25)
            logger.warning(
                "auggie attempt %d/%d failed (%s); retrying in %.1fs",
                attempt, max_attempts, type(e).__name__, delay + jitter,
            )
            time.sleep(delay + jitter)
    # niedostępne, ale dla mypy:
    raise last_exc  # type: ignore[misc]


# =============================================================================
# CIRCUIT BREAKER
# =============================================================================
@dataclass
class _BreakerState:
    consecutive_failures: int = 0
    opened_at: float = 0.0
    state: str = "closed"  # "closed" | "open" | "half_open"


class CircuitBreakerOpen(RuntimeError):
    """Obwód otwarty — odrzucamy wywołania."""


class CircuitBreaker:
    def __init__(self, *, fail_threshold: int = 5, reset_after_s: float = 30.0):
        self.fail_threshold = fail_threshold
        self.reset_after_s = reset_after_s
        self._state = _BreakerState()
        self._lock = Lock()

    def before(self) -> None:
        with self._lock:
            if self._state.state == "open":
                if time.time() - self._state.opened_at >= self.reset_after_s:
                    self._state.state = "half_open"
                    logger.info("circuit breaker: half-open (probe)")
                else:
                    raise CircuitBreakerOpen(
                        f"Circuit breaker OPEN ({self._state.consecutive_failures} fails). "
                        f"Try again in ~{int(self.reset_after_s - (time.time() - self._state.opened_at))}s."
                    )

    def on_success(self) -> None:
        with self._lock:
            if self._state.state != "closed":
                logger.info("circuit breaker: closed (recovered)")
            self._state = _BreakerState()

    def on_failure(self, exc: BaseException) -> None:
        if not is_retriable(exc):
            return  # config errors don't trip the breaker
        with self._lock:
            self._state.consecutive_failures += 1
            if self._state.consecutive_failures >= self.fail_threshold and self._state.state != "open":
                self._state.state = "open"
                self._state.opened_at = time.time()
                logger.error(
                    "circuit breaker: OPEN after %d consecutive failures",
                    self._state.consecutive_failures,
                )

    def status(self) -> dict:
        with self._lock:
            return {
                "state": self._state.state,
                "consecutive_failures": self._state.consecutive_failures,
                "opened_at": self._state.opened_at,
            }


BREAKER = CircuitBreaker(
    fail_threshold=int(os.getenv("AUGGIE_BREAKER_THRESHOLD", "5")),
    reset_after_s=float(os.getenv("AUGGIE_BREAKER_RESET_S", "30")),
)

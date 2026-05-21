"""
Retry/backoff dla wywolan LLM w ADK.

Problem: google-genai czasem dostaje 429 / 5xx / DeadlineExceeded.
Default: Runner wywala z bledem -> pipeline agentowy pada.

Rozwiazanie: wrapper nad model-callback, ktory w przypadku bledu
w odpowiedzi LLM wymusi ponowne wywolanie z exponential backoff.

Uwaga: ADK nie udostepnia "retry w callbacku" bezposrednio, wiec
strategia jest taka:
  - rejestrujemy before_model + after_model
  - po blednej odpowiedzi zapisujemy flage w state
  - dodatkowo eksportujemy funkcje `retry_call(coro, ...)` do uzycia
    w miejscach gdzie sami wywolujemy `await runner.run_async(...)`
    lub jawnie model (np. w modul 22 critique_loop).

Publiczne API:
  - retry_call(coro_fn, *, max_attempts=3, base_delay=1.0, ...) -> awaitable
  - is_retryable_error(exc) -> bool
"""

from __future__ import annotations

import asyncio
import logging
import random
from typing import Any, Awaitable, Callable, Iterable, Optional


log = logging.getLogger("code_analyst.retry")


RETRYABLE_STATUS = {408, 409, 425, 429, 500, 502, 503, 504}
RETRYABLE_SUBSTRINGS = (
    "deadline exceeded",
    "rate limit",
    "resource exhausted",
    "unavailable",
    "timeout",
    "connection reset",
    "temporarily",
)


def is_retryable_error(exc: BaseException) -> bool:
    """Czy wyjatek kwalifikuje sie do ponowienia?"""
    if isinstance(exc, asyncio.TimeoutError):
        return True
    status = getattr(exc, "status_code", None) or getattr(exc, "code", None)
    if isinstance(status, int) and status in RETRYABLE_STATUS:
        return True
    msg = str(exc).lower()
    return any(sub in msg for sub in RETRYABLE_SUBSTRINGS)


async def retry_call(
    coro_fn: Callable[[], Awaitable[Any]],
    *,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    jitter: float = 0.25,
    retry_on: Optional[Callable[[BaseException], bool]] = None,
    name: str = "llm_call",
) -> Any:
    """Wywoluje `coro_fn()` z exponential backoff.

    coro_fn: bezargumentowa funkcja zwracajaca coroutine.
    retry_on: predykat decydujacy czy ponawiac (default: is_retryable_error).
    """
    pred = retry_on or is_retryable_error
    attempt = 0
    last_exc: Optional[BaseException] = None
    while attempt < max_attempts:
        attempt += 1
        try:
            return await coro_fn()
        except BaseException as exc:  # noqa: BLE001
            last_exc = exc
            if not pred(exc) or attempt >= max_attempts:
                log.warning(
                    "%s: non-retryable or max attempts reached (attempt=%d): %s",
                    name, attempt, exc,
                )
                raise
            delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
            delay += random.uniform(0, jitter * delay)
            log.info(
                "%s: retryable error (attempt=%d/%d), sleeping %.2fs: %s",
                name, attempt, max_attempts, delay, exc,
            )
            await asyncio.sleep(delay)
    # unreachable — ale dla mypy:
    assert last_exc is not None
    raise last_exc


# ---------------------------------------------------------------------------
# ADK integration: zwracamy pare callbackow do podpiecia do LlmAgent,
# ktore w razie bledu zapisuja licznik w stanie sesji (obserwowalnosc).
# Faktyczne retry robimy na warstwie orkiestracji (retry_call), bo ADK
# nie pozwala z callbacka wywolac ponownie tego samego modelu.
# ---------------------------------------------------------------------------

def make_retry_observer_callbacks(*, agent_name: str) -> tuple[Callable, Callable]:
    """Before/after callback obserwujace bledy LLM w stanie sesji.

    Zapisuje w session.state:
        _llm_errors_<agent>: list[{msg, ts}]
    """
    import time

    key = f"_llm_errors_{agent_name}"

    def before_model_callback(callback_context, llm_request):
        return None

    def after_model_callback(callback_context, llm_response):
        err = getattr(llm_response, "error_code", None)
        msg = getattr(llm_response, "error_message", None)
        if err or msg:
            try:
                state = callback_context.state
                lst = state.get(key) or []
                lst.append({"ts": time.time(), "err": str(err), "msg": str(msg)})
                state[key] = lst
            except Exception:
                pass
        return None

    return before_model_callback, after_model_callback

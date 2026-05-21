"""
Agent Gateway — vendor-neutral entry point for all agent calls.
================================================================

Single point of entry replacing ``auggie_factory.auggie_run()`` and
``auggie_factory.auggie_call()``.  Wraps every call with:

    Cache → Circuit Breaker → Retry → Provider.run() → Telemetry → Cost

The provider is selected via ``AGENT_PROVIDER`` env variable (default: auggie).

Usage:
    from agent_gateway import gateway
    result = gateway.run(tool_name="ask_specialist", prompt="Explain DI")
    print(result.output)
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Iterator, List, Optional

from caching import CACHE, CACHE_ENABLED, is_cacheable
from cost_tracker import COST
from resilience import BREAKER, CircuitBreakerOpen, retry_with_backoff

from providers import ProviderRegistry, ProviderUnavailable
from providers.base import AgentCapabilities, AgentSession, RunResult

logger = logging.getLogger(__name__)


# =============================================================================
# Telemetry (moved from auggie_factory — now vendor-neutral)
# =============================================================================
@dataclass
class CallStats:
    tool: str
    duration_s: float
    success: bool
    cached: bool
    attempts: int
    provider: str = ""
    error: str | None = None
    tool_calls: int = 0
    function_calls: int = 0


@dataclass
class TelemetryStore:
    calls: list[CallStats] = field(default_factory=list)

    def add(self, s: CallStats) -> None:
        self.calls.append(s)
        logger.info(
            "agent call: provider=%s tool=%s duration=%.2fs success=%s cached=%s attempts=%d",
            s.provider, s.tool, s.duration_s, s.success, s.cached, s.attempts,
        )

    def summary(self) -> dict:
        if not self.calls:
            return {"total": 0}
        ok = [c for c in self.calls if c.success]
        return {
            "total": len(self.calls),
            "success": len(ok),
            "failed": len(self.calls) - len(ok),
            "cached_hits": sum(1 for c in self.calls if c.cached),
            "avg_duration_s": round(sum(c.duration_s for c in self.calls) / len(self.calls), 2),
            "total_tool_calls": sum(c.tool_calls for c in self.calls),
            "total_func_calls": sum(c.function_calls for c in self.calls),
        }


TELEMETRY = TelemetryStore()


# =============================================================================
# Subprocess registry (kept for web layer SSE cancel-on-disconnect)
# =============================================================================
_ACTIVE_LOG_CBS: dict[int, Callable[[str, str], None]] = {}
_ACTIVE_LOCK = threading.Lock()


def register_log_cb(thread_id: int, cb: Callable[[str, str], None]) -> None:
    with _ACTIVE_LOCK:
        _ACTIVE_LOG_CBS[thread_id] = cb


def unregister_log_cb(thread_id: int) -> None:
    with _ACTIVE_LOCK:
        _ACTIVE_LOG_CBS.pop(thread_id, None)


def _emit_log(level: str, message: str) -> None:
    cb = _ACTIVE_LOG_CBS.get(threading.get_ident())
    if cb is not None:
        try:
            cb(level, message)
        except Exception:  # noqa: BLE001
            pass


# =============================================================================
# AgentGateway
# =============================================================================
class AgentGateway:
    """Vendor-neutral orchestration layer.

    Wraps every call with: cache → circuit breaker → retry → provider → telemetry → cost.
    Feature negotiation: if the provider doesn't support a feature (e.g. structured_returns),
    the gateway applies client-side fallbacks.
    """

    def __init__(self, provider_name: str | None = None) -> None:
        self._provider_name = provider_name
        self._provider = None

    @property
    def provider(self):
        if self._provider is None:
            self._provider = ProviderRegistry.get(self._provider_name)
        return self._provider

    @property
    def provider_name(self) -> str:
        return self.provider.name

    @property
    def capabilities(self) -> AgentCapabilities:
        return self.provider.capabilities

    def run(
        self,
        *,
        tool_name: str,
        prompt: str,
        return_type: type | None = None,
        extra_cli: list[str] | None = None,
        success_criteria: list[str] | None = None,
        max_verification_rounds: int = 3,
        functions: list | None = None,
        max_attempts: int = 3,
        workspace_override: str | None = None,
        timeout: int | None = None,
    ) -> RunResult:
        """Production-grade single call with full resilience stack."""
        provider = self.provider
        caps = provider.capabilities
        _timeout = timeout or int(os.getenv("AGENT_TIMEOUT", os.getenv("AUGGIE_TIMEOUT", "180")))
        model = os.getenv("AGENT_MODEL", os.getenv("AUGGIE_MODEL", "sonnet4.5"))
        rt_name = return_type.__name__ if return_type else "auto"

        # 1. CACHE
        cacheable = CACHE_ENABLED and is_cacheable(
            success_criteria=success_criteria, functions=functions,
        )
        cache_key: str | None = None
        if cacheable:
            cache_key = CACHE.make_key(prompt, model, rt_name, extra_cli)
            cached = CACHE.get(cache_key)
            if cached is not None:
                logger.info("cache HIT for tool=%s (key=%s...)", tool_name, cache_key[:12])
                result = RunResult(
                    output=cached, raw_text=str(cached), duration_s=0.0,
                    model=model, provider=provider.name, cached=True, attempts=0,
                )
                TELEMETRY.add(CallStats(
                    tool=tool_name, duration_s=0.0, success=True, cached=True,
                    attempts=0, provider=provider.name,
                ))
                COST.record(tool=tool_name, model=model, duration_s=0.0, cached=True)
                return result
        elif CACHE_ENABLED:
            CACHE.mark_skipped()

        # 2. BREAKER
        BREAKER.before()

        attempt_counter = {"n": 0}

        def _do_call() -> RunResult:
            attempt_counter["n"] += 1
            _emit_log(
                "info",
                f"[{provider.name}] tool={tool_name} model={model} "
                f"return_type={rt_name} prompt={len(prompt)}c "
                f"attempt={attempt_counter['n']}",
            )

            # Feature negotiation — success_criteria
            sc = success_criteria if caps.success_criteria else None
            mvr = max_verification_rounds if caps.success_criteria else 3

            return provider.run(
                prompt,
                return_type=return_type if caps.structured_returns or return_type is str or return_type is None else None,
                success_criteria=sc,
                max_verification_rounds=mvr,
                functions=functions if caps.function_calling else None,
                timeout=_timeout,
                extra_cli=extra_cli,
                workspace_override=workspace_override,
            )

        # 3. RETRY
        start = time.perf_counter()
        success = False
        error: str | None = None
        result: RunResult | None = None
        try:
            result = retry_with_backoff(_do_call, max_attempts=max_attempts)
            result.attempts = attempt_counter["n"]
            success = True
            BREAKER.on_success()
        except CircuitBreakerOpen:
            raise
        except Exception as e:
            error = f"{type(e).__name__}: {e}"
            BREAKER.on_failure(e)
            raise
        finally:
            duration = time.perf_counter() - start
            TELEMETRY.add(CallStats(
                tool=tool_name, duration_s=duration, success=success, cached=False,
                attempts=attempt_counter["n"], provider=provider.name, error=error,
                tool_calls=result.tool_calls if result else 0,
                function_calls=result.function_calls if result else 0,
            ))
            COST.record(tool=tool_name, model=model, duration_s=duration, cached=False)

        # 4. CACHE store
        if cacheable and cache_key is not None and result is not None:
            CACHE.put(cache_key, result.output, result.duration_s)

        # 5. Client-side structured return parsing (if provider doesn't support it)
        if (return_type and return_type is not str
                and not caps.structured_returns and result is not None):
            result.output = self._parse_structured(result.raw_text, return_type)

        return result  # type: ignore[return-value]

    @contextmanager
    def session(self, tool_name: str = "session", **kwargs) -> Iterator[AgentSession]:
        """Open a multi-turn session with the active provider."""
        provider = self.provider
        BREAKER.before()
        start = time.perf_counter()
        success = False
        error: str | None = None
        try:
            with provider.session(**kwargs) as sess:
                yield sess
                success = True
                BREAKER.on_success()
        except Exception as e:
            error = f"{type(e).__name__}: {e}"
            BREAKER.on_failure(e)
            raise
        finally:
            duration = time.perf_counter() - start
            model = os.getenv("AGENT_MODEL", os.getenv("AUGGIE_MODEL", "sonnet4.5"))
            TELEMETRY.add(CallStats(
                tool=tool_name, duration_s=duration, success=success,
                cached=False, attempts=1, provider=provider.name, error=error,
            ))
            COST.record(tool=tool_name, model=model, duration_s=duration, cached=False)

    @staticmethod
    def _parse_structured(raw_text: str, return_type: type) -> Any:
        """Best-effort JSON → dataclass parsing for providers without native support."""
        import re
        txt = raw_text.strip()
        if txt.startswith("```"):
            txt = re.sub(r"^```[a-zA-Z]*\n?", "", txt)
            txt = re.sub(r"\n?```$", "", txt)
        try:
            data = json.loads(txt)
        except json.JSONDecodeError:
            return raw_text
        if hasattr(return_type, "__dataclass_fields__"):
            try:
                return return_type(**data)
            except (TypeError, ValueError):
                return data
        return data

    def health(self) -> dict:
        """Run health checks adapted for the current provider."""
        from health_check import run_checks
        results, healthy = run_checks(ping=False)
        # Add provider info
        results.append({
            "check": "active_provider",
            "ok": True,
            "detail": f"{self.provider_name} (capabilities: {self.capabilities})",
        })
        return {"healthy": healthy, "provider": self.provider_name, "checks": results}


# =============================================================================
# Module-level singleton — the primary entry point
# =============================================================================
gateway = AgentGateway()


# =============================================================================
# Backward-compatibility aliases (for gradual migration)
# =============================================================================
AuggieUnavailable = ProviderUnavailable


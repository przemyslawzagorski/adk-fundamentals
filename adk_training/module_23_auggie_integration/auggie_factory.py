"""
Auggie Factory v2 — production-grade orchestration layer.
==========================================================

Integruje:
  - LRU Cache (caching.CACHE)
  - Cost Tracking (cost_tracker.COST)
  - Retry + Circuit Breaker (resilience)
  - Telemetry (TELEMETRY)
  - Optional persistent ACP client (acp_pool)
  - Structured/JSON logs

Każde wywołanie `auggie_run()` jest:
  1. Cache lookup → hit zwraca natychmiast
  2. Circuit breaker check → fast-fail przy degradacji
  3. Retry z exponential backoff dla transient errors
  4. Telemetria + cost record (zawsze, nawet przy fail)
  5. Cleanup (close subprocess albo zwolnij ACP slot)
"""

from __future__ import annotations

import json
import logging
import os
import pathlib
import shutil
import subprocess
import sys
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass, field, replace as dataclasses_replace
from typing import Any, Callable, Iterator

from caching import CACHE, CACHE_ENABLED, is_cacheable
from cost_tracker import COST
from resilience import BREAKER, CircuitBreakerOpen, retry_with_backoff


# =============================================================================
# Subprocess registry — pozwala anulować trwające `auggie --print` z innego
# wątku (web layer reaguje na disconnect klienta SSE).
# =============================================================================
_ACTIVE_PROCS: dict[int, subprocess.Popen] = {}
_ACTIVE_LOG_CBS: dict[int, Callable[[str, str], None]] = {}
_ACTIVE_LOCK = threading.Lock()


def register_log_cb(thread_id: int, cb: Callable[[str, str], None]) -> None:
    """Register a per-thread callback (level, message) for streaming logs."""
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


def kill_thread_subprocess(thread_id: int) -> bool:
    """Kill the auggie subprocess (if any) currently running on the given thread.

    Returns True if a process was killed, False otherwise.
    """
    with _ACTIVE_LOCK:
        proc = _ACTIVE_PROCS.get(thread_id)
    if proc is None or proc.poll() is not None:
        return False
    try:
        proc.kill()
    except Exception:  # noqa: BLE001
        return False
    return True


# =============================================================================
# LOGGING — opcjonalnie JSON
# =============================================================================
class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps({
            "ts": self.formatTime(record),
            "level": record.levelname,
            "name": record.name,
            "msg": record.getMessage(),
        }, ensure_ascii=False)


def _setup_logging() -> None:
    if logging.getLogger().handlers:
        return
    handler = logging.StreamHandler(sys.stderr)
    if os.getenv("LOG_FORMAT", "text").lower() == "json":
        handler.setFormatter(_JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
        ))
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(os.getenv("LOG_LEVEL", "INFO"))


_setup_logging()
logger = logging.getLogger("auggie_factory")


# =============================================================================
# TELEMETRY
# =============================================================================
@dataclass
class CallStats:
    tool: str
    duration_s: float
    success: bool
    cached: bool
    attempts: int
    error: str | None = None
    tool_calls: int = 0
    function_calls: int = 0


@dataclass
class TelemetryStore:
    calls: list[CallStats] = field(default_factory=list)

    def add(self, s: CallStats) -> None:
        self.calls.append(s)
        logger.info(
            "auggie call: tool=%s duration=%.2fs success=%s cached=%s attempts=%d tool_calls=%d func_calls=%d",
            s.tool, s.duration_s, s.success, s.cached, s.attempts, s.tool_calls, s.function_calls,
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
# LISTENER
# =============================================================================
def _build_listener():
    if os.getenv("AUGGIE_TELEMETRY", "true").lower() not in ("1", "true", "yes"):
        return None, lambda: (0, 0)
    try:
        from auggie_sdk import AgentListener
    except ImportError:
        return None, lambda: (0, 0)

    counters = {"tool": 0, "func": 0}

    class TelemetryListener(AgentListener):
        # Direct callback reference — set by _do_call on the worker thread so
        # that listener callbacks fired on Auggie SDK's internal threads still
        # reach the right SSE queue without relying on threading.get_ident().
        _direct_cb: "Callable[[str, str], None] | None" = None

        def set_emit(self, cb: "Callable[[str, str], None] | None") -> None:
            self._direct_cb = cb

        def _emit(self, level: str, msg: str) -> None:
            cb = self._direct_cb
            if cb is not None:
                try:
                    cb(level, msg)
                except Exception:  # noqa: BLE001
                    pass
            else:
                _emit_log(level, msg)  # fallback: thread-id lookup

        def on_tool_call(self, *args, **kwargs) -> None:
            counters["tool"] += 1
            title = kwargs.get("title") or (args[1] if len(args) > 1 else "?")
            logger.debug("  [auggie] tool: %s", title)
            self._emit("info", f"[auggie] tool: {str(title)[:300]}")

        def on_function_call(self, function_name: str, arguments: dict) -> None:
            counters["func"] += 1
            logger.debug("  [auggie] function: %s(%s)", function_name, arguments)
            try:
                args_preview = json.dumps(arguments, ensure_ascii=False)[:200]
            except Exception:  # noqa: BLE001
                args_preview = str(arguments)[:200]
            self._emit("debug", f"[auggie] function: {function_name}({args_preview})")

        def on_function_result(self, function_name: str, result, error=None) -> None:
            if error:
                logger.warning("  [auggie] function %s failed: %s", function_name, error)
                self._emit("warning", f"[auggie] function {function_name} failed: {str(error)[:300]}")
            else:
                self._emit("debug", f"[auggie] function {function_name} -> ok")

        def on_agent_message(self, *args, **kwargs) -> None:  # type: ignore[override]
            text = kwargs.get("text") or (args[0] if args else "")
            if text:
                self._emit("info", f"[auggie] {str(text)[:400]}")

    return TelemetryListener(), lambda: (counters["tool"], counters["func"])


# =============================================================================
# CONFIG
# =============================================================================
@dataclass(frozen=True)
class AuggieConfig:
    model: str
    timeout: int
    max_turns: int
    workspace: pathlib.Path
    api_key: str | None
    api_url: str | None
    cli_path: str | None
    has_session_auth: bool

    @classmethod
    def from_env(cls) -> "AuggieConfig":
        workspace = os.getenv("AUGGIE_WORKSPACE")
        ws_path = pathlib.Path(workspace) if workspace else pathlib.Path(__file__).parent

        # Explicit override wins (useful on WSL where Windows PATH leaks .cmd shims)
        cli_path = os.getenv("AUGGIE_CLI_PATH")
        if not cli_path:
            # Platform-aware lookup: on POSIX prefer native binary, on Windows prefer .cmd/.exe
            if os.name == "nt":
                candidates = ("auggie.cmd", "auggie.exe", "auggie")
            else:
                candidates = ("auggie", "auggie.exe", "auggie.cmd")
            for name in candidates:
                p = shutil.which(name)
                if p and not (os.name != "nt" and p.lower().endswith((".cmd", ".bat", ".exe"))):
                    cli_path = p
                    break

        return cls(
            model=os.getenv("AUGGIE_MODEL", "sonnet4.5"),
            timeout=int(os.getenv("AUGGIE_TIMEOUT", "180")),
            max_turns=int(os.getenv("AUGGIE_MAX_TURNS", "3")),
            workspace=ws_path,
            api_key=os.getenv("AUGMENT_API_KEY"),
            api_url=os.getenv("AUGMENT_API_URL"),
            cli_path=cli_path,
            has_session_auth=bool(os.getenv("AUGMENT_SESSION_AUTH")),
        )

    def to_kwargs(self, *, with_listener: bool, extra_cli: list[str] | None = None) -> tuple[dict, callable]:
        kw: dict = {
            "workspace_root": str(self.workspace),
            "model": self.model,
            "timeout": self.timeout,
        }
        cli = list(extra_cli) if extra_cli else []
        if "--max-turns" not in cli:
            cli += ["--max-turns", str(self.max_turns)]
        if "--quiet" not in cli:
            cli += ["--quiet"]
        if cli:
            kw["cli_args"] = cli
        if self.cli_path:
            kw["cli_path"] = self.cli_path
        if not self.has_session_auth:
            if self.api_key:
                kw["api_key"] = self.api_key
            if self.api_url:
                kw["api_url"] = self.api_url

        listener, stats_fn = (None, lambda: (0, 0))
        if with_listener:
            listener, stats_fn = _build_listener()
            if listener is not None:
                kw["listener"] = listener
        return kw, stats_fn


# =============================================================================
# FACTORY
# =============================================================================
class AuggieUnavailable(RuntimeError):
    """Pakiet auggie-sdk nie jest zainstalowany."""


def _import_auggie():
    try:
        from auggie_sdk import Auggie
        return Auggie
    except ImportError as e:
        raise AuggieUnavailable(
            "Pakiet 'auggie-sdk' nie jest zainstalowany. Uruchom: pip install auggie-sdk"
        ) from e


@contextmanager
def auggie_call(tool_name: str, *, extra_cli: list[str] | None = None) -> Iterator:
    """Backward-compatible context manager — daje surowy obiekt Auggie.

    UWAGA: nie korzysta z cache (bo cache wymaga znajomości promptu/return_type).
    Dla pełnego stacka (cache+retry+cost) używaj `auggie_run()`.
    """
    Auggie = _import_auggie()
    cfg = AuggieConfig.from_env()
    kwargs, stats_fn = cfg.to_kwargs(with_listener=True, extra_cli=extra_cli)

    BREAKER.before()
    start = time.perf_counter()
    success = False
    error: str | None = None
    auggie = None
    try:
        auggie = Auggie(**kwargs)
        yield auggie
        success = True
        BREAKER.on_success()
    except Exception as e:  # noqa: BLE001
        error = f"{type(e).__name__}: {e}"
        BREAKER.on_failure(e)
        raise
    finally:
        if auggie is not None:
            try:
                auggie.close()
            except Exception:  # noqa: BLE001
                pass
        duration = time.perf_counter() - start
        tool_calls, func_calls = stats_fn()
        TELEMETRY.add(CallStats(
            tool=tool_name, duration_s=duration, success=success, cached=False,
            attempts=1, error=error, tool_calls=tool_calls, function_calls=func_calls,
        ))
        COST.record(tool=tool_name, model=cfg.model, duration_s=duration, cached=False)


def auggie_run(
    *,
    tool_name: str,
    prompt: str,
    return_type: type | None = None,
    extra_cli: list[str] | None = None,
    success_criteria: list[str] | None = None,
    max_verification_rounds: int = 3,
    functions: list | None = None,
    max_attempts: int = 3,
    workspace_override: str | pathlib.Path | None = None,
) -> Any:
    """Production-grade pojedyncze wywołanie Auggie.

    Pełny stack: cache → breaker → retry → run → telemetry/cost.
    Zwraca surową odpowiedź (str / dataclass / lista — zależnie od return_type).
    """
    cfg = AuggieConfig.from_env()
    if workspace_override is not None:
        ws = pathlib.Path(workspace_override).resolve()
        if ws.exists():
            cfg = dataclasses_replace(cfg, workspace=ws)
    rt_name = return_type.__name__ if return_type else "auto"

    # 1. CACHE
    cacheable = CACHE_ENABLED and is_cacheable(success_criteria=success_criteria, functions=functions)
    cache_key: str | None = None
    if cacheable:
        cache_key = CACHE.make_key(prompt, cfg.model, rt_name, extra_cli)
        cached = CACHE.get(cache_key)
        if cached is not None:
            logger.info("cache HIT for tool=%s (key=%s...)", tool_name, cache_key[:12])
            TELEMETRY.add(CallStats(
                tool=tool_name, duration_s=0.0, success=True, cached=True, attempts=0,
            ))
            COST.record(tool=tool_name, model=cfg.model, duration_s=0.0, cached=True)
            return cached
    elif CACHE_ENABLED:
        CACHE.mark_skipped()

    # 2. BREAKER
    BREAKER.before()

    # CLI fallback path — szybki, bezstanowy `auggie --print` (subprocess).
    # Aktywuj przez AUGGIE_USE_CLI=1. Działa tylko dla return_type=str
    # i bez success_criteria/functions (bo CLI nie obsługuje tych opcji).
    use_cli = os.getenv("AUGGIE_USE_CLI", "").lower() in ("1", "true", "yes")
    if use_cli and not success_criteria and not functions and (return_type is None or return_type is str):
        cli_path = cfg.cli_path or "auggie"
        cmd = [cli_path, "--print", prompt, "--model", cfg.model, "--quiet"]
        attempt_counter = {"n": 0}

        def _do_cli():
            attempt_counter["n"] += 1
            tid = threading.get_ident()
            _emit_log("info", f"$ {cli_path} --print <prompt {len(prompt)}c> --model {cfg.model}")
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace",
                bufsize=1,
            )
            with _ACTIVE_LOCK:
                _ACTIVE_PROCS[tid] = proc

            stdout_chunks: list[str] = []

            def _drain():
                # Stream lines as they appear; first non-empty lines also become the result.
                try:
                    assert proc.stdout is not None
                    for line in proc.stdout:
                        stdout_chunks.append(line)
                        stripped = line.rstrip()
                        if stripped:
                            _emit_log("debug", stripped[:500])
                except Exception:  # noqa: BLE001
                    pass

            drain_thread = threading.Thread(target=_drain, daemon=True)
            drain_thread.start()
            try:
                proc.wait(timeout=cfg.timeout)
            except subprocess.TimeoutExpired:
                proc.kill()
                drain_thread.join(timeout=2)
                _emit_log("error", f"timeout after {cfg.timeout}s — process killed")
                raise RuntimeError(f"auggie CLI timeout after {cfg.timeout}s")
            finally:
                drain_thread.join(timeout=2)
                with _ACTIVE_LOCK:
                    _ACTIVE_PROCS.pop(tid, None)

            output = "".join(stdout_chunks).strip()
            if proc.returncode == -9 or proc.returncode == -15 or (os.name == "nt" and proc.returncode == 1 and not output):
                _emit_log("warning", f"process killed (rc={proc.returncode})")
                raise RuntimeError("auggie CLI cancelled")
            if proc.returncode != 0:
                tail = output[-300:] if output else "(no output)"
                raise RuntimeError(f"auggie CLI exit {proc.returncode}: {tail}")
            return output

        start = time.perf_counter()
        success = False
        error: str | None = None
        result: Any = None
        try:
            result = retry_with_backoff(_do_cli, max_attempts=max_attempts)
            success = True
            BREAKER.on_success()
        except CircuitBreakerOpen:
            raise
        except Exception as e:  # noqa: BLE001
            error = f"{type(e).__name__}: {e}"
            BREAKER.on_failure(e)
            raise
        finally:
            duration = time.perf_counter() - start
            TELEMETRY.add(CallStats(
                tool=tool_name, duration_s=duration, success=success, cached=False,
                attempts=attempt_counter["n"], error=error,
            ))
            COST.record(tool=tool_name, model=cfg.model, duration_s=duration, cached=False)
        if cacheable and cache_key is not None:
            CACHE.put(cache_key, result, duration)
        return result

    Auggie = _import_auggie()
    kwargs, stats_fn = cfg.to_kwargs(with_listener=True, extra_cli=extra_cli)
    listener = kwargs.get("listener")  # TelemetryListener or None

    attempt_counter = {"n": 0}

    def _do_call():
        attempt_counter["n"] += 1
        rt_label = return_type.__name__ if return_type else "auto"
        crit = len(success_criteria or [])
        funcs = len(functions or [])

        # Capture the worker thread's callback DIRECTLY so that listener
        # callbacks fired on Auggie SDK's internal threads reach the right queue.
        tid = threading.get_ident()
        direct_cb = _ACTIVE_LOG_CBS.get(tid)
        if listener is not None and hasattr(listener, "set_emit"):
            listener.set_emit(direct_cb)

        def _emit(level: str, msg: str) -> None:
            if direct_cb is not None:
                try:
                    direct_cb(level, msg)
                except Exception:  # noqa: BLE001
                    pass
            else:
                _emit_log(level, msg)

        _emit(
            "info",
            f"[auggie SDK] tool={tool_name} model={cfg.model} workspace={cfg.workspace} "
            f"return_type={rt_label} prompt={len(prompt)}c criteria={crit} functions={funcs} "
            f"timeout={cfg.timeout}s attempt={attempt_counter['n']}",
        )
        t0 = time.perf_counter()

        # Heartbeat — emits every 12s so the log panel shows life
        stop_hb = threading.Event()

        def _heartbeat() -> None:
            while not stop_hb.wait(12.0):
                _emit("info", f"[auggie SDK] still running... {time.perf_counter() - t0:.0f}s elapsed")

        hb = threading.Thread(target=_heartbeat, daemon=True, name="auggie-hb")
        hb.start()

        auggie = Auggie(**kwargs)
        try:
            run_kwargs: dict = {"timeout": cfg.timeout}
            if return_type is not None:
                run_kwargs["return_type"] = return_type
            if success_criteria:
                run_kwargs["success_criteria"] = success_criteria
                run_kwargs["max_verification_rounds"] = max_verification_rounds
            if functions:
                run_kwargs["functions"] = functions
            try:
                out = auggie.run(prompt, **run_kwargs)
            except Exception as e:  # noqa: BLE001
                _emit(
                    "error",
                    f"[auggie SDK] {type(e).__name__} after {time.perf_counter()-t0:.1f}s: {str(e)[:300]}",
                )
                raise
            _emit("info", f"[auggie SDK] done in {time.perf_counter()-t0:.1f}s")
            return out
        finally:
            stop_hb.set()
            hb.join(timeout=1)
            try:
                auggie.close()
            except Exception:  # noqa: BLE001
                pass

    # 3. RETRY
    start = time.perf_counter()
    success = False
    error: str | None = None
    result: Any = None
    try:
        result = retry_with_backoff(_do_call, max_attempts=max_attempts)
        success = True
        BREAKER.on_success()
    except CircuitBreakerOpen:
        raise
    except Exception as e:  # noqa: BLE001
        error = f"{type(e).__name__}: {e}"
        BREAKER.on_failure(e)
        raise
    finally:
        duration = time.perf_counter() - start
        tool_calls, func_calls = stats_fn()
        TELEMETRY.add(CallStats(
            tool=tool_name, duration_s=duration, success=success, cached=False,
            attempts=attempt_counter["n"], error=error,
            tool_calls=tool_calls, function_calls=func_calls,
        ))
        COST.record(tool=tool_name, model=cfg.model, duration_s=duration, cached=False)

    # 4. STORE in cache (only on success + cacheable)
    if cacheable and cache_key is not None:
        CACHE.put(cache_key, result, duration)
    return result

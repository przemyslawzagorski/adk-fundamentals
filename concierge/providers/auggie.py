"""
Auggie SDK provider adapter.
=============================

Wraps ``auggie_sdk.Auggie`` behind the :class:`AgentProvider` protocol.
Supports all native Auggie features: structured returns, success criteria,
function calling, sessions, workspace access, streaming.

Config via env:
  AUGGIE_MODEL       — model name (default: sonnet4.5)
  AUGGIE_TIMEOUT     — seconds (default: 180)
  AUGGIE_MAX_TURNS   — max agent turns (default: 3)
  AUGGIE_WORKSPACE   — workspace root (default: concierge dir)
  AUGGIE_CLI_PATH    — explicit CLI path override
  AUGGIE_USE_CLI     — 1/true to force CLI subprocess mode
  AUGMENT_API_KEY    — API key (alternative to session auth)
  AUGMENT_API_URL    — custom API endpoint
  AUGMENT_SESSION_AUTH — session JSON auth
"""

from __future__ import annotations

import json
import logging
import os
import pathlib
import shutil
import subprocess
import threading
import time
from contextlib import contextmanager
from dataclasses import replace as dataclasses_replace
from typing import Any, Callable, Iterator

from .base import (
    AgentCapabilities,
    AgentSession,
    BaseSession,
    ProviderUnavailable,
    RunResult,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Config
# =============================================================================
class _AuggieConfig:
    """Reads Auggie-specific configuration from environment."""

    __slots__ = (
        "model", "timeout", "max_turns", "workspace",
        "api_key", "api_url", "cli_path", "has_session_auth",
    )

    def __init__(self) -> None:
        workspace = os.getenv("AUGGIE_WORKSPACE")
        self.workspace = pathlib.Path(workspace) if workspace else pathlib.Path(__file__).parent.parent
        self.model = os.getenv("AUGGIE_MODEL", "sonnet4.5")
        self.timeout = int(os.getenv("AUGGIE_TIMEOUT", "180"))
        self.max_turns = int(os.getenv("AUGGIE_MAX_TURNS", "3"))
        self.api_key = os.getenv("AUGMENT_API_KEY")
        self.api_url = os.getenv("AUGMENT_API_URL")
        self.has_session_auth = bool(os.getenv("AUGMENT_SESSION_AUTH"))

        cli_path = os.getenv("AUGGIE_CLI_PATH")
        if not cli_path:
            if os.name == "nt":
                candidates = ("auggie.cmd", "auggie.exe", "auggie")
            else:
                candidates = ("auggie", "auggie.exe", "auggie.cmd")
            for name in candidates:
                p = shutil.which(name)
                if p and not (os.name != "nt" and p.lower().endswith((".cmd", ".bat", ".exe"))):
                    cli_path = p
                    break
        self.cli_path = cli_path

    def to_kwargs(self, *, extra_cli: list[str] | None = None) -> dict:
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
        return kw


def _import_auggie():
    try:
        from auggie_sdk import Auggie
        return Auggie
    except ImportError as e:
        raise ProviderUnavailable(
            "Package 'auggie-sdk' is not installed. Run: pip install auggie-sdk"
        ) from e


# =============================================================================
# AuggieSession
# =============================================================================
class AuggieSession(BaseSession):
    """Multi-turn session backed by auggie_sdk.Auggie.session()."""

    def __init__(self, auggie_obj: Any, model: str) -> None:
        super().__init__()
        self._auggie = auggie_obj
        self._model = model
        self._sess = auggie_obj.session()
        self._sess.__enter__()

    def run(self, prompt: str, *, return_type: type | None = None) -> RunResult:
        t0 = time.perf_counter()
        kwargs: dict = {}
        if return_type is not None:
            kwargs["return_type"] = return_type
        out = self._sess.run(prompt, **kwargs)
        duration = time.perf_counter() - t0
        return RunResult(
            output=out,
            raw_text=str(out),
            duration_s=duration,
            model=self._model,
            provider="auggie",
        )

    def _close(self) -> None:
        try:
            self._sess.__exit__(None, None, None)
        except Exception:  # noqa: BLE001
            pass



# =============================================================================
# AuggieProvider
# =============================================================================
class AuggieProvider:
    """Auggie SDK adapter — full-featured provider.

    Supports: structured_returns, success_criteria, function_calling,
    session_context, workspace_access, streaming.
    """

    name = "auggie"
    capabilities = AgentCapabilities(
        structured_returns=True,
        success_criteria=True,
        function_calling=True,
        session_context=True,
        workspace_access=True,
        streaming=True,
    )

    def run(
        self,
        prompt: str,
        *,
        return_type: type | None = None,
        success_criteria: list[str] | None = None,
        max_verification_rounds: int = 3,
        functions: list[Callable] | None = None,
        timeout: int = 180,
        extra_cli: list[str] | None = None,
        workspace_override: str | None = None,
    ) -> RunResult:
        Auggie = _import_auggie()
        cfg = _AuggieConfig()
        if workspace_override:
            ws = pathlib.Path(workspace_override).resolve()
            if ws.exists():
                cfg.workspace = ws

        kwargs = cfg.to_kwargs(extra_cli=extra_cli)
        kwargs["timeout"] = timeout

        use_cli = os.getenv("AUGGIE_USE_CLI", "").lower() in ("1", "true", "yes")
        if use_cli and not success_criteria and not functions and (return_type is None or return_type is str):
            return self._run_cli(cfg, prompt, timeout)

        t0 = time.perf_counter()
        auggie = Auggie(**kwargs)
        try:
            run_kwargs: dict = {"timeout": timeout}
            if return_type is not None:
                run_kwargs["return_type"] = return_type
            if success_criteria:
                run_kwargs["success_criteria"] = success_criteria
                run_kwargs["max_verification_rounds"] = max_verification_rounds
            if functions:
                run_kwargs["functions"] = functions

            out = auggie.run(prompt, **run_kwargs)
            duration = time.perf_counter() - t0
            return RunResult(
                output=out, raw_text=str(out), duration_s=duration,
                model=cfg.model, provider="auggie",
            )
        finally:
            try:
                auggie.close()
            except Exception:  # noqa: BLE001
                pass

    def _run_cli(self, cfg: _AuggieConfig, prompt: str, timeout: int) -> RunResult:
        """CLI subprocess fallback — ``auggie --print``."""
        cli_path = cfg.cli_path or "auggie"
        cmd = [cli_path, "--print", prompt, "--model", cfg.model, "--quiet"]
        t0 = time.perf_counter()
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace",
        )
        try:
            stdout, _ = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.communicate(timeout=2)
            raise RuntimeError(f"auggie CLI timeout after {timeout}s")
        duration = time.perf_counter() - t0
        if proc.returncode != 0:
            raise RuntimeError(f"auggie CLI exit {proc.returncode}: {(stdout or '')[-300:]}")
        return RunResult(
            output=stdout.strip(), raw_text=stdout.strip(), duration_s=duration,
            model=cfg.model, provider="auggie",
        )

    @contextmanager
    def session(self, **kwargs) -> Iterator[AgentSession]:
        Auggie = _import_auggie()
        cfg = _AuggieConfig()
        extra_cli = kwargs.get("extra_cli")
        auggie_kwargs = cfg.to_kwargs(extra_cli=extra_cli)
        auggie = Auggie(**auggie_kwargs)
        sess = AuggieSession(auggie, cfg.model)
        try:
            yield sess
        finally:
            sess._close()
            try:
                auggie.close()
            except Exception:  # noqa: BLE001
                pass

    def close(self) -> None:
        pass

"""
Vendor-agnostic agent provider abstractions.
=============================================

Defines the contracts that every provider adapter must implement:
  - AgentProvider   — main protocol (run, session, close)
  - AgentSession    — multi-turn conversation
  - AgentCapabilities — feature negotiation flags
  - RunResult       — unified output envelope
  - ProviderUnavailable — raised when SDK not installed / misconfigured
"""

from __future__ import annotations

import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Iterator, List, Optional, Protocol, runtime_checkable


# =============================================================================
# Exceptions
# =============================================================================
class ProviderUnavailable(RuntimeError):
    """Provider SDK is not installed or misconfigured."""


# =============================================================================
# Capabilities — feature negotiation
# =============================================================================
@dataclass(frozen=True)
class AgentCapabilities:
    """Declares what a provider natively supports.

    Features not supported natively will be emulated client-side
    by AgentGateway (e.g. structured_returns via JSON parsing).
    """
    structured_returns: bool = False
    success_criteria: bool = False
    function_calling: bool = False
    session_context: bool = False
    workspace_access: bool = False
    streaming: bool = False


# =============================================================================
# RunResult — unified output
# =============================================================================
@dataclass
class RunResult:
    """Unified output envelope from any provider call."""
    output: Any
    raw_text: str
    duration_s: float
    model: str
    provider: str
    tool_calls: int = 0
    function_calls: int = 0
    cached: bool = False
    attempts: int = 1
    metadata: dict = field(default_factory=dict)


# =============================================================================
# AgentSession — multi-turn protocol
# =============================================================================
@runtime_checkable
class AgentSession(Protocol):
    """Multi-turn conversation session."""

    @property
    def session_id(self) -> str: ...

    def run(self, prompt: str, *, return_type: type | None = None) -> RunResult: ...


class BaseSession:
    """Default session base with auto-generated ID."""

    def __init__(self) -> None:
        self._session_id = uuid.uuid4().hex[:12]

    @property
    def session_id(self) -> str:
        return self._session_id


# =============================================================================
# AgentProvider — main protocol
# =============================================================================
@runtime_checkable
class AgentProvider(Protocol):
    """Contract that every vendor adapter must implement."""

    @property
    def name(self) -> str: ...

    @property
    def capabilities(self) -> AgentCapabilities: ...

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
    ) -> RunResult: ...

    @contextmanager
    def session(self, **kwargs) -> Iterator[AgentSession]: ...

    def close(self) -> None: ...

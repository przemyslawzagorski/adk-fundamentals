"""
Provider registry — auto-discovers available agent providers.
=============================================================

Usage:
    from concierge.providers import ProviderRegistry
    provider = ProviderRegistry.get()           # uses AGENT_PROVIDER env
    provider = ProviderRegistry.get("auggie")   # explicit
"""

from __future__ import annotations

import logging
import os
from typing import Dict, Optional, Type

from .base import (
    AgentCapabilities,
    AgentProvider,
    AgentSession,
    BaseSession,
    ProviderUnavailable,
    RunResult,
)

logger = logging.getLogger(__name__)

__all__ = [
    "AgentCapabilities",
    "AgentProvider",
    "AgentSession",
    "BaseSession",
    "ProviderRegistry",
    "ProviderUnavailable",
    "RunResult",
]


class ProviderRegistry:
    """Central registry of available agent providers.

    Providers are registered at import time. The active provider
    is selected via ``AGENT_PROVIDER`` env var (default: ``auggie``).
    """

    _providers: Dict[str, Type] = {}

    @classmethod
    def register(cls, name: str, provider_cls: Type) -> None:
        cls._providers[name] = provider_cls
        logger.debug("Registered provider: %s (%s)", name, provider_cls.__name__)

    @classmethod
    def get(cls, name: Optional[str] = None) -> AgentProvider:
        name = name or os.getenv("AGENT_PROVIDER", "auggie")
        if name not in cls._providers:
            available = list(cls._providers.keys())
            raise ProviderUnavailable(
                f"Unknown provider: {name!r}. Available: {available}"
            )
        return cls._providers[name]()

    @classmethod
    def available(cls) -> list[str]:
        return list(cls._providers.keys())

    @classmethod
    def is_registered(cls, name: str) -> bool:
        return name in cls._providers


# ── Auto-register available providers ────────────────────────────────────────
def _auto_register() -> None:
    """Try to import and register each known provider adapter."""
    _adapters = [
        ("auggie", ".auggie", "AuggieProvider"),
        ("adk", ".adk", "AdkProvider"),
    ]
    for reg_name, module_path, class_name in _adapters:
        try:
            import importlib
            mod = importlib.import_module(module_path, package=__package__)
            cls = getattr(mod, class_name)
            ProviderRegistry.register(reg_name, cls)
        except (ImportError, AttributeError) as e:
            logger.debug("Provider %r not available: %s", reg_name, e)


_auto_register()

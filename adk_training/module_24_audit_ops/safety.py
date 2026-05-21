"""Safety guard — domain allowlist, rate limiting, disclaimer enforcement."""
from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

from .config import AuditConfig

logger = logging.getLogger(__name__)


class SafetyError(Exception):
    """Raised when a safety check fails. Should HALT the run."""


@dataclass
class DisclaimerAck:
    """User must explicitly acknowledge legal authorization before any active probing."""
    acknowledged: bool
    user_id: str = "anonymous"
    target_url: str = ""
    timestamp: float = 0.0
    statement: str = (
        "I confirm I have explicit written authorization from the target system owner "
        "to perform security testing. I accept full legal responsibility for this audit."
    )


class RateLimiter:
    """Simple async token-bucket — at most `rps` actions per second across whole run."""

    def __init__(self, rps: float = 1.0):
        self.rps = max(0.1, rps)
        self._lock = asyncio.Lock()
        self._last = 0.0

    async def wait(self) -> None:
        async with self._lock:
            now = time.monotonic()
            wait_for = max(0.0, (self._last + 1.0 / self.rps) - now)
            if wait_for > 0:
                await asyncio.sleep(wait_for)
            self._last = time.monotonic()


def assert_url_allowed(url: str, cfg: AuditConfig) -> None:
    """Raise SafetyError if the URL is not in the allowlist (when one is configured)."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise SafetyError(f"Unsupported scheme: {parsed.scheme!r} (only http/https allowed)")
    if not parsed.hostname:
        raise SafetyError(f"URL has no hostname: {url!r}")
    if not cfg.is_domain_allowed(url):
        raise SafetyError(
            f"Domain {parsed.hostname!r} is not in AUDITOPS_ALLOWED_DOMAINS allowlist. "
            f"Configured: {cfg.allowed_domains or '(empty = all allowed)'}"
        )


def assert_disclaimer(ack: Optional[DisclaimerAck], cfg: AuditConfig) -> None:
    """Block the run if disclaimer is required but not acknowledged."""
    if not cfg.require_disclaimer:
        return
    if ack is None or not ack.acknowledged:
        raise SafetyError(
            "Legal authorization required. The user must acknowledge the pentest disclaimer "
            "before any active probing. Set AUDITOPS_REQUIRE_DISCLAIMER=0 only in CI/sandbox."
        )


def runtime_guard(url: str, cfg: AuditConfig, ack: Optional[DisclaimerAck]) -> None:
    """One-stop check before launching any scenario."""
    assert_disclaimer(ack, cfg)
    assert_url_allowed(url, cfg)
    logger.info(
        "audit safety OK · target=%s · rate=%s rps · aggressive=%s · readonly=%s",
        url, cfg.rate_limit_rps, cfg.aggressive, cfg.read_only,
    )

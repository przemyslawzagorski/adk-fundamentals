"""AuditOps configuration — env-driven, single source of truth."""
from __future__ import annotations

import os
import pathlib
from dataclasses import dataclass, field
from typing import List


def _csv(env: str, default: str = "") -> List[str]:
    raw = os.getenv(env, default).strip()
    if not raw:
        return []
    return [x.strip() for x in raw.split(",") if x.strip()]


def _bool_env(name: str, default: str) -> bool:
    return os.getenv(name, default).lower() in ("1", "true", "yes", "on")


@dataclass
class AuditConfig:
    """Configuration for an audit run.

    All fields use ``default_factory`` so env vars are read **at instantiation
    time**, not at class-definition time. This is critical because tests and
    the API mount may set env vars after the module has been imported.
    """
    # Safety
    allowed_domains: List[str] = field(default_factory=lambda: _csv("AUDITOPS_ALLOWED_DOMAINS"))
    require_disclaimer: bool = field(default_factory=lambda: _bool_env("AUDITOPS_REQUIRE_DISCLAIMER", "1"))
    rate_limit_rps: float = field(default_factory=lambda: float(os.getenv("AUDITOPS_RATE_LIMIT_RPS", "1.0")))
    aggressive: bool = field(default_factory=lambda: _bool_env("AUDITOPS_AGGRESSIVE", ""))
    read_only: bool = field(default_factory=lambda: _bool_env("AUDITOPS_READ_ONLY", ""))

    # Playwright runtime
    headless: bool = field(default_factory=lambda: _bool_env("AUDITOPS_HEADLESS", "1"))
    record_video: bool = field(default_factory=lambda: _bool_env("AUDITOPS_RECORD_VIDEO", "1"))
    browser: str = field(default_factory=lambda: os.getenv("AUDITOPS_BROWSER", "chromium"))
    viewport_width: int = field(default_factory=lambda: int(os.getenv("AUDITOPS_VIEWPORT_W", "1280")))
    viewport_height: int = field(default_factory=lambda: int(os.getenv("AUDITOPS_VIEWPORT_H", "720")))
    nav_timeout_ms: int = field(default_factory=lambda: int(os.getenv("AUDITOPS_NAV_TIMEOUT_MS", "15000")))
    action_timeout_ms: int = field(default_factory=lambda: int(os.getenv("AUDITOPS_ACTION_TIMEOUT_MS", "8000")))

    # Limits
    max_scenarios: int = field(default_factory=lambda: int(os.getenv("AUDITOPS_MAX_SCENARIOS", "8")))
    max_steps_per_scenario: int = field(default_factory=lambda: int(os.getenv("AUDITOPS_MAX_STEPS", "20")))
    total_budget_seconds: int = field(default_factory=lambda: int(os.getenv("AUDITOPS_BUDGET_S", "600")))

    # Storage
    artifacts_dir: pathlib.Path = field(
        default_factory=lambda: pathlib.Path(
            os.getenv("AUDITOPS_ARTIFACTS_DIR")
            or pathlib.Path(__file__).parent / "artifacts"
        ).resolve()
    )

    # LLM (delegates to module_23 Auggie)
    llm_model: str = field(default_factory=lambda: os.getenv("AUGGIE_MODEL", "claude-sonnet-4-5"))

    @classmethod
    def from_env(cls) -> "AuditConfig":
        cfg = cls()
        cfg.artifacts_dir.mkdir(parents=True, exist_ok=True)
        return cfg

    def is_domain_allowed(self, url: str) -> bool:
        """Check if URL host is in allowlist (if allowlist is empty -> allow all)."""
        if not self.allowed_domains:
            return True
        from urllib.parse import urlparse
        host = (urlparse(url).hostname or "").lower()
        for allowed in self.allowed_domains:
            allowed = allowed.lower().lstrip(".")
            if host == allowed or host.endswith("." + allowed):
                return True
        return False

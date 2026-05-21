"""Single source of truth for the executor DSL.

Both the LLM scenario parser and the playwright runner consult this module.
"""
from __future__ import annotations

from typing import Any, Dict, List, Set


# Every action understood by playwright_runner.run_scenario.
# Keep this set IN SYNC with the executor's dispatch ladder.
ALLOWED_ACTIONS: Set[str] = {
    # navigation / interaction
    "goto", "fill", "click", "press", "wait_for", "wait_for_load_state",
    "fetch_url", "screenshot", "eval", "note",
    # assertions
    "expect_status", "expect_header", "expect_text", "expect_origin",
    "expect_frame_ancestors_or_xfo", "expect_cookies_secure",
    "expect_cors_open", "expect_no_sql_error", "expect_no_mixed_content",
    "expect_storage_clean",
}

ALLOWED_SEVERITIES: Set[str] = {"critical", "high", "medium", "low", "info"}


class DSLValidationError(ValueError):
    """Raised when a scenario contains an unknown action or invalid step."""


def validate_scenario(scenario: Dict[str, Any]) -> None:
    """Strict structural validation. Raises :class:`DSLValidationError`.

    Used by:
    - the LLM parser, to reject hallucinated actions before execution,
    - the API, to reject hand-crafted scenarios from the UI.
    """
    if not isinstance(scenario, dict):
        raise DSLValidationError("scenario must be a JSON object")
    steps = scenario.get("steps")
    if not isinstance(steps, list) or not steps:
        raise DSLValidationError("scenario.steps must be a non-empty list")
    sev = scenario.get("severity", "info")
    if sev not in ALLOWED_SEVERITIES:
        raise DSLValidationError(f"invalid severity: {sev!r}")
    for i, step in enumerate(steps):
        if not isinstance(step, dict):
            raise DSLValidationError(f"step {i} is not an object")
        action = step.get("action")
        if action not in ALLOWED_ACTIONS:
            raise DSLValidationError(
                f"step {i} uses unknown action {action!r}. Allowed: {sorted(ALLOWED_ACTIONS)}"
            )
        if "fail_finding" in step:
            ff = step["fail_finding"]
            if not isinstance(ff, dict) or "title" not in ff:
                raise DSLValidationError(f"step {i} fail_finding requires a title")
            sev2 = ff.get("severity", "info")
            if sev2 not in ALLOWED_SEVERITIES:
                raise DSLValidationError(f"step {i} fail_finding has invalid severity {sev2!r}")

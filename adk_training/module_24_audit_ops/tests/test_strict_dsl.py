"""Tests for the strict DSL validator."""
import pytest

from adk_training.module_24_audit_ops.dsl import (
    ALLOWED_ACTIONS, DSLValidationError, validate_scenario,
)


def test_unknown_action_rejected():
    with pytest.raises(DSLValidationError) as ei:
        validate_scenario({"steps": [{"action": "rm_rf_slash"}]})
    assert "rm_rf_slash" in str(ei.value)


def test_empty_steps_rejected():
    with pytest.raises(DSLValidationError):
        validate_scenario({"steps": []})


def test_non_dict_step_rejected():
    with pytest.raises(DSLValidationError):
        validate_scenario({"steps": ["goto"]})


def test_invalid_severity_rejected():
    with pytest.raises(DSLValidationError):
        validate_scenario({"severity": "armageddon", "steps": [{"action": "goto"}]})


def test_fail_finding_must_have_title():
    with pytest.raises(DSLValidationError):
        validate_scenario({"steps": [{"action": "expect_status",
                                      "fail_finding": {"severity": "high"}}]})


def test_all_documented_actions_pass():
    for action in ALLOWED_ACTIONS:
        validate_scenario({"steps": [{"action": action}]})


def test_parser_rejects_unknown_action_in_pentest_agent():
    """The LLM parser must not accept hallucinated actions."""
    from adk_training.module_24_audit_ops.pentest_agent import _safe_parse_scenario
    raw = '{"id":"x","name":"x","steps":[{"action":"hack_the_planet"}]}'
    with pytest.raises(ValueError) as ei:
        _safe_parse_scenario(raw)
    assert "hack_the_planet" in str(ei.value)

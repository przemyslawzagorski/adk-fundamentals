"""Tests for the skills loader (V1)."""
from __future__ import annotations

from pathlib import Path

import pytest

from adk_training.module_24_audit_ops import skills_loader as sl


def test_default_registry_loads_five_skills():
    reg = sl.default_registry(reload=True)
    names = sorted(s.name for s in reg.list())
    assert "recon-helpers" in names
    assert "owasp-a01-access-control" in names
    assert "owasp-a02-crypto" in names
    assert "owasp-a03-injection" in names
    assert "owasp-a05-misconfig" in names


def test_skill_manifest_has_description_and_triggers():
    reg = sl.default_registry()
    sk = reg.get("owasp-a01-access-control")
    m = sk.manifest()
    assert m["name"] == "owasp-a01-access-control"
    assert m["description"]
    assert "access-control" in sk.triggers


def test_recon_signals_baseline_when_empty():
    assert sl.recon_signals(None) == ["baseline"]
    assert sl.recon_signals({}) == ["baseline"]


def test_recon_signals_missing_csp_and_hsts():
    recon = {"missing_headers": ["content-security-policy", "strict-transport-security"]}
    sigs = set(sl.recon_signals(recon))
    assert "missing:content-security-policy" in sigs
    assert "missing:strict-transport-security" in sigs
    assert "misconfig" in sigs
    assert "crypto" in sigs


def test_recon_signals_form_with_password_yields_auth_and_access_control():
    recon = {"forms": [{"action": "/login", "fields": [{"type": "password"}]}]}
    sigs = set(sl.recon_signals(recon))
    assert "forms" in sigs
    assert "auth" in sigs
    assert "access-control" in sigs


def test_select_skills_always_includes_recon_helpers():
    reg = sl.default_registry()
    selected = sl.select_skills_for_recon({}, reg)
    names = [s.name for s in selected]
    assert "recon-helpers" in names


def test_select_skills_includes_a05_when_csp_missing():
    reg = sl.default_registry()
    recon = {"missing_headers": ["content-security-policy"]}
    selected = sl.select_skills_for_recon(recon, reg)
    names = {s.name for s in selected}
    assert "owasp-a05-misconfig" in names


def test_render_planner_context_contains_l1_and_l2():
    block = sl.render_planner_context({"missing_headers": ["content-security-policy"]})
    assert "AVAILABLE SKILLS" in block
    assert "owasp-a05-misconfig" in block
    # body is included for selected skill
    assert "Misconfiguration" in block or "misconfig" in block.lower()


def test_render_planner_context_includes_extra_skill():
    extra = sl.Skill(
        name="audit-history",
        description="prior runs",
        instructions="History body here",
        directory=Path("."),
        triggers=[],
    )
    block = sl.render_planner_context({}, extra_skills=[extra])
    assert "audit-history" in block
    assert "History body here" in block


def test_load_resource_blocks_path_traversal():
    reg = sl.default_registry()
    sk = reg.get("owasp-a01-access-control")
    with pytest.raises(ValueError):
        sk.load_resource("../SKILL.md")
    with pytest.raises(ValueError):
        sk.load_resource("/etc/passwd")


def test_skill_load_resource_works_for_legitimate_file():
    reg = sl.default_registry()
    sk = reg.get("owasp-a01-access-control")
    resources = sk.list_resources()
    if resources:
        text = sk.load_resource(resources[0])
        assert text  # non-empty

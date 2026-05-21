"""Tests for the planner-context renderer (V1 + V3 integration)."""
from __future__ import annotations

from pathlib import Path

from adk_training.module_24_audit_ops import skills_loader as sl
from adk_training.module_24_audit_ops import wiki


def test_render_planner_context_baseline_minimum():
    block = sl.render_planner_context(None)
    assert "AVAILABLE SKILLS" in block
    assert "recon-helpers" in block


def test_render_planner_context_picks_a01_for_login_form():
    recon = {
        "forms": [
            {"action": "/login", "method": "POST",
             "inputs": [{"name": "u", "type": "text"}, {"name": "p", "type": "password"}]}
        ]
    }
    block = sl.render_planner_context(recon)
    assert "owasp-a01-access-control" in block
    assert "owasp-a03-injection" in block  # POST + form → injection signal


def test_render_planner_context_includes_history_skill_from_wiki(tmp_path):
    audit = {
        "run_id": "rh1",
        "target_url": "https://acme.test/",
        "started_at": "2026-04-17T10:00:00Z",
        "duration_s": 0.5,
        "findings": [{"severity": "high", "title": "Missing CSP",
                       "owasp": "A05:2021-Misconfiguration", "scenario_id": "s1"}],
    }
    wiki.record_run(tmp_path, audit)
    history_text = wiki.history_skill_text(tmp_path, "https://acme.test/")
    assert history_text  # sanity

    extra = sl.Skill(
        name="audit-history",
        description="Prior audit history",
        instructions=history_text,
        directory=tmp_path,
        triggers=[],
    )
    block = sl.render_planner_context({}, extra_skills=[extra])
    assert "audit-history" in block
    assert "Missing CSP" in block


def test_manifest_block_lists_all_bundled_skills():
    block = sl.render_manifest_block(sl.default_registry())
    for name in [
        "recon-helpers",
        "owasp-a01-access-control",
        "owasp-a02-crypto",
        "owasp-a03-injection",
        "owasp-a05-misconfig",
    ]:
        assert name in block

"""Tests for reporter — Markdown rendering, score computation."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from adk_training.module_24_audit_ops.config import AuditConfig
from adk_training.module_24_audit_ops.reporter import (
    compute_score,
    render_markdown,
    write_report,
)


def _audit(tmp_path: Path, findings=None, scenarios=None):
    return {
        "run_id": "test_run_001",
        "target_url": "https://example.com/",
        "started_at": 1700000000.0,
        "finished_at": 1700000060.0,
        "duration_s": 60.0,
        "recon": {
            "final_url": "https://example.com/",
            "status_code": 200,
            "server_header": "nginx/1.25",
            "technologies": ["react", "next.js"],
            "forms": [],
            "security_headers": {"Content-Security-Policy": None, "Strict-Transport-Security": "max-age=1"},
            "notes": ["No CSP — XSS impact will be higher."],
        },
        "scenarios": scenarios or [],
        "findings": findings or [],
    }


def test_score_empty():
    assert compute_score([]) == 0.0


def test_score_capped_at_100():
    findings = [{"severity": "critical"}] * 20
    assert compute_score(findings) == 100.0


def test_score_weighted_by_severity():
    s_low = compute_score([{"severity": "low"}])
    s_high = compute_score([{"severity": "high"}])
    s_critical = compute_score([{"severity": "critical"}])
    assert s_low < s_high < s_critical
    # info should not move score
    assert compute_score([{"severity": "info"}]) == 0.0


def test_score_unknown_severity_ignored():
    assert compute_score([{"severity": "bogus"}]) == 0.0


def test_render_markdown_includes_score_and_target(tmp_path):
    cfg = AuditConfig(artifacts_dir=tmp_path)
    audit = _audit(tmp_path, findings=[
        {"severity": "high", "title": "Missing HSTS", "scenario_id": "headers_baseline",
         "owasp": "A05", "evidence": {"header": "Strict-Transport-Security"}},
    ])
    md = render_markdown(audit, cfg)
    assert "AuditOps Report" in md
    assert "https://example.com/" in md
    assert "Risk score" in md
    assert "Missing HSTS" in md
    assert "A05" in md
    # JSON-encoded evidence block
    assert "Strict-Transport-Security" in md


def test_render_markdown_handles_no_findings(tmp_path):
    cfg = AuditConfig(artifacts_dir=tmp_path)
    audit = _audit(tmp_path)
    md = render_markdown(audit, cfg)
    assert "No security findings" in md


def test_write_report_writes_both_files(tmp_path):
    cfg = AuditConfig(artifacts_dir=tmp_path)
    audit = _audit(tmp_path, findings=[{"severity": "medium", "title": "x", "scenario_id": "y", "owasp": "Ax", "evidence": {}}])
    res = write_report(audit, cfg)
    assert Path(res["markdown_path"]).is_file()
    assert Path(res["json_path"]).is_file()
    assert res["markdown_url"].endswith("/report.md")
    assert res["json_url"].endswith("/report.json")
    parsed = json.loads(Path(res["json_path"]).read_text(encoding="utf-8"))
    assert parsed["run_id"] == "test_run_001"

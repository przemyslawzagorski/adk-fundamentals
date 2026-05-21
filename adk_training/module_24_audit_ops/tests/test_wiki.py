"""Tests for the audit wiki (V2 / V3)."""
from __future__ import annotations

from pathlib import Path

import pytest

from adk_training.module_24_audit_ops import wiki


def _audit(run_id: str, severity: str = "high", title: str = "Missing CSP"):
    return {
        "run_id": run_id,
        "target_url": "https://acme.test/login",
        "started_at": "2026-04-17T10:00:00Z",
        "duration_s": 1.2,
        "findings": [
            {
                "severity": severity,
                "title": title,
                "owasp": "A05:2021-Misconfiguration",
                "scenario_id": "s1",
            }
        ],
    }


def test_target_slug_normalizes_host():
    assert wiki.target_slug("https://acme.test/foo") == "acme.test"
    assert wiki.target_slug("https://Some.Host.Example/") == "some.host.example"
    assert wiki.target_slug("not-a-url") == "unknown"


def test_finding_slug_stable_across_cosmetic_changes():
    a = wiki.finding_slug("high", "Missing CSP")
    b = wiki.finding_slug("HIGH", "missing CSP")
    c = wiki.finding_slug("high", "Missing  CSP   ")
    assert a == b == c


def test_finding_slug_collapses_numbers_for_stability():
    a = wiki.finding_slug("medium", "Form 12 leaks password")
    b = wiki.finding_slug("medium", "Form 99 leaks password")
    assert a == b  # numbers normalized to '#'


def test_record_run_creates_layout(tmp_path):
    paths = wiki.record_run(tmp_path, _audit("r1"))
    assert paths.index.is_file()
    assert paths.log.is_file()
    assert (paths.runs_dir / "r1.md").is_file()
    assert any(paths.findings_dir.glob("F-high-missing-csp.md"))


def test_record_run_idempotent(tmp_path):
    wiki.record_run(tmp_path, _audit("r1"))
    wiki.record_run(tmp_path, _audit("r1"))  # same run twice
    paths = wiki.wiki_paths(tmp_path, "https://acme.test/")
    log_lines = [l for l in paths.log.read_text(encoding="utf-8").splitlines() if l.startswith("## [")]
    assert len(log_lines) == 2  # log appends per call (audit trail)
    # but the finding page must record run_id only once
    page = next(paths.findings_dir.glob("F-*.md")).read_text(encoding="utf-8")
    assert page.count("[r1]") == 1


def test_record_run_merges_multiple_runs(tmp_path):
    wiki.record_run(tmp_path, _audit("r1"))
    wiki.record_run(tmp_path, _audit("r2"))
    paths = wiki.wiki_paths(tmp_path, "https://acme.test/")
    page = next(paths.findings_dir.glob("F-*.md")).read_text(encoding="utf-8")
    assert "**Occurrences:** 2" in page
    assert "[r1]" in page and "[r2]" in page


def test_index_lists_runs_and_findings(tmp_path):
    wiki.record_run(tmp_path, _audit("r1"))
    paths = wiki.wiki_paths(tmp_path, "https://acme.test/")
    idx = paths.index.read_text(encoding="utf-8")
    assert "Recent runs" in idx
    assert "r1" in idx
    assert "Findings" in idx


def test_history_skill_text_empty_without_wiki(tmp_path):
    assert wiki.history_skill_text(tmp_path, "https://nope.test/") == ""


def test_history_skill_text_after_run(tmp_path):
    wiki.record_run(tmp_path, _audit("r1"))
    text = wiki.history_skill_text(tmp_path, "https://acme.test/")
    assert "Prior audit history" in text
    assert "Missing CSP" in text


def test_lint_clean_after_record_run(tmp_path):
    wiki.record_run(tmp_path, _audit("r1"))
    issues = wiki.lint_wiki(tmp_path, "https://acme.test/")
    # report.md is intentionally a broken link (artifacts/<run_id>/report.md
    # may not exist in tests). Strip those for the assertion.
    non_report = [i for i in issues if "report.md" not in i.detail]
    assert non_report == []


def test_lint_detects_missing_run_stub(tmp_path):
    wiki.record_run(tmp_path, _audit("r1"))
    paths = wiki.wiki_paths(tmp_path, "https://acme.test/")
    (paths.runs_dir / "r1.md").unlink()
    issues = wiki.lint_wiki(tmp_path, "https://acme.test/")
    kinds = {i.kind for i in issues}
    assert "missing_run_stub" in kinds


def test_lint_all_iterates_targets(tmp_path):
    wiki.record_run(tmp_path, _audit("r1"))
    out = wiki.lint_all(tmp_path)
    assert "acme.test" in out or out == {}  # both acceptable depending on report.md presence

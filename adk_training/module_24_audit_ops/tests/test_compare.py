"""Tests for run-to-run diff."""
from adk_training.module_24_audit_ops.compare import diff_runs, render_diff_markdown


def _run(run_id: str, findings, scenarios):
    return {
        "run_id": run_id,
        "target_url": "https://example.test",
        "findings": findings,
        "scenarios": scenarios,
    }


def test_diff_classifies_new_fixed_unchanged():
    base = _run("a",
                findings=[
                    {"scenario_id": "headers", "severity": "high", "title": "Missing CSP"},
                    {"scenario_id": "cookies", "severity": "medium", "title": "Cookie not Secure"},
                ],
                scenarios=[
                    {"id": "headers", "passed": False, "findings": []},
                    {"id": "cookies", "passed": False, "findings": []},
                ])
    cur = _run("b",
               findings=[
                   {"scenario_id": "headers", "severity": "high", "title": "Missing CSP"},
                   {"scenario_id": "cors", "severity": "high", "title": "CORS reflects origin"},
               ],
               scenarios=[
                   {"id": "headers", "passed": False, "findings": []},
                   {"id": "cookies", "passed": True, "findings": []},
                   {"id": "cors", "passed": False, "findings": []},
               ])
    d = diff_runs(base, cur)
    assert d["summary"]["new"] == 1
    assert d["summary"]["fixed"] == 1
    assert d["summary"]["unchanged"] == 1
    assert d["new_findings"][0]["scenario_id"] == "cors"
    assert d["fixed_findings"][0]["scenario_id"] == "cookies"
    kinds = {t["kind"] for t in d["scenario_transitions"]}
    assert "added" in kinds
    assert "recovered" in kinds


def test_diff_normalizes_numeric_titles():
    base = _run("a", findings=[{"scenario_id": "x", "severity": "low",
                                "title": "Found 3 issues"}], scenarios=[])
    cur = _run("b", findings=[{"scenario_id": "x", "severity": "low",
                               "title": "Found 5 issues"}], scenarios=[])
    d = diff_runs(base, cur)
    assert d["summary"]["unchanged"] == 1


def test_diff_severity_sensitive():
    base = _run("a", findings=[{"scenario_id": "x", "severity": "low",
                                "title": "issue"}], scenarios=[])
    cur = _run("b", findings=[{"scenario_id": "x", "severity": "high",
                               "title": "issue"}], scenarios=[])
    d = diff_runs(base, cur)
    assert d["summary"]["new"] == 1
    assert d["summary"]["fixed"] == 1


def test_render_markdown_smoke():
    d = diff_runs(_run("a", [], []), _run("b", [], []))
    md = render_diff_markdown(d)
    assert "AuditOps Diff" in md
    assert "a" in md and "b" in md

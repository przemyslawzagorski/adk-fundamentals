"""Integration tests — wiki hooked into CLI + planner uses skills."""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest

from adk_training.module_24_audit_ops import cli, wiki


class _FakeAudit:
    def __init__(self, run_id="r-int-1", severity="high"):
        self.run_id = run_id
        self.target_url = "https://acme.test/x"
        self.duration_s = 0.4
        self.findings = [{"severity": severity, "title": "Missing CSP",
                          "scenario_id": "s1", "owasp": "A05:2021-Misconfiguration"}]
        self.scenarios = [{"id": "s1", "name": "S1", "passed": False,
                           "duration_s": 0.1, "findings": list(self.findings),
                           "error": None}]
        self.started_at = time.time()
        self.finished_at = self.started_at + 0.4

    def to_dict(self):
        return {
            "run_id": self.run_id, "target_url": self.target_url,
            "duration_s": self.duration_s, "findings": self.findings,
            "scenarios": self.scenarios, "started_at": self.started_at,
            "finished_at": self.finished_at,
        }


@pytest.fixture()
def patched(monkeypatch, tmp_path):
    async def _fake_auto(url, cfg, ack=None, on_event=None, auth=None):
        return _FakeAudit()

    def _fake_write(audit, cfg):
        d = tmp_path / audit["run_id"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "report.json").write_text(json.dumps(audit), encoding="utf-8")
        (d / "report.md").write_text("# fake", encoding="utf-8")
        return {"markdown_path": str(d / "report.md"),
                "json_path":     str(d / "report.json")}

    monkeypatch.setattr(cli, "auto_pentest", _fake_auto)
    monkeypatch.setattr(cli, "write_report", _fake_write)
    monkeypatch.setenv("AUDITOPS_ALLOWED_DOMAINS", "acme.test")
    monkeypatch.setenv("AUDITOPS_ARTIFACTS_DIR", str(tmp_path))
    yield tmp_path


def test_cli_run_writes_wiki(patched, monkeypatch):
    rc = cli.main(["--url", "https://acme.test/x",
                   "--allow-domain", "acme.test",
                   "--fail-on", "critical"])  # do not fail on high finding
    assert rc == 0
    paths = wiki.wiki_paths(patched, "https://acme.test/")
    assert paths.index.is_file()
    assert paths.log.is_file()
    assert any(paths.findings_dir.glob("F-high-missing-csp.md"))


def test_cli_wiki_lint_returns_zero_when_clean(patched, capsys):
    cli.main(["--url", "https://acme.test/x",
              "--allow-domain", "acme.test",
              "--fail-on", "critical"])
    rc = cli.main(["wiki-lint", "--report-dir", str(patched), "--json"])
    out = capsys.readouterr().out
    # report.md *does* exist for this run, so wiki should be clean.
    assert rc == 0, f"expected clean wiki but got: {out}"


def test_cli_wiki_lint_detects_broken(patched):
    cli.main(["--url", "https://acme.test/x",
              "--allow-domain", "acme.test",
              "--fail-on", "critical"])
    paths = wiki.wiki_paths(patched, "https://acme.test/")
    # wreck a finding page link by deleting the run stub
    next(paths.runs_dir.glob("*.md")).unlink()
    rc = cli.main(["wiki-lint", "--report-dir", str(patched)])
    assert rc == 1

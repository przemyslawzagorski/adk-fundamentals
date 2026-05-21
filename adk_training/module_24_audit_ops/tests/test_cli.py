"""Tests for the CLI / CI mode."""
import json
import os
import time
from pathlib import Path

import pytest

from adk_training.module_24_audit_ops import cli


class _FakeAudit:
    """Minimal stand-in for AuditResult that the CLI needs."""

    def __init__(self, severity="info", scenarios=None, run_id="r1"):
        self.run_id = run_id
        self.target_url = "https://acme.test/"
        self.duration_s = 0.5
        self.findings = [{"severity": severity, "title": "x", "scenario_id": "s1"}] if severity != "none" else []
        self.scenarios = scenarios or [
            {"id": "s1", "name": "Scenario 1", "passed": severity == "none",
             "duration_s": 0.1, "findings": list(self.findings),
             "error": None}
        ]
        self.started_at = time.time()
        self.finished_at = self.started_at + 0.5

    def to_dict(self):
        return {
            "run_id": self.run_id,
            "target_url": self.target_url,
            "duration_s": self.duration_s,
            "findings": self.findings,
            "scenarios": self.scenarios,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
        }


@pytest.fixture()
def patched(monkeypatch, tmp_path):
    async def _fake_auto(url, cfg, ack=None, on_event=None, auth=None):
        return _FakeAudit(severity=os.environ.get("FAKE_SEVERITY", "info"))

    def _fake_write(audit, cfg):
        # Match real reporter signature: audit is a dict.
        d = tmp_path / audit["run_id"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "report.json").write_text(json.dumps(audit), encoding="utf-8")
        (d / "report.md").write_text("# fake", encoding="utf-8")
        return {"markdown_path": str(d / "report.md"), "json_path": str(d / "report.json")}

    monkeypatch.setattr(cli, "auto_pentest", _fake_auto)
    monkeypatch.setattr(cli, "write_report", _fake_write)
    monkeypatch.setenv("AUDITOPS_ALLOWED_DOMAINS", "acme.test")
    monkeypatch.setenv("AUDITOPS_ARTIFACTS_DIR", str(tmp_path))
    yield tmp_path


def test_cli_exits_zero_when_below_threshold(patched, monkeypatch, capsys):
    monkeypatch.setenv("FAKE_SEVERITY", "low")
    rc = cli.main(["--url", "https://acme.test/", "--allow-domain", "acme.test", "--fail-on", "high"])
    assert rc == 0


def test_cli_exits_one_when_at_or_above_threshold(patched, monkeypatch):
    monkeypatch.setenv("FAKE_SEVERITY", "critical")
    rc = cli.main(["--url", "https://acme.test/", "--allow-domain", "acme.test", "--fail-on", "high"])
    assert rc == 1


def test_cli_writes_junit_when_requested(patched, monkeypatch, tmp_path):
    monkeypatch.setenv("FAKE_SEVERITY", "high")
    junit = tmp_path / "out" / "junit.xml"
    rc = cli.main(["--url", "https://acme.test/", "--allow-domain", "acme.test",
                   "--fail-on", "high", "--junit", str(junit)])
    assert rc == 1
    assert junit.exists()
    txt = junit.read_text(encoding="utf-8")
    assert "<testsuite" in txt
    assert "<failure" in txt


def test_cli_rejects_guided_without_scenario(patched, capsys):
    rc = cli.main(["--url", "https://acme.test/", "--allow-domain", "acme.test", "--mode", "guided"])
    assert rc == 2


def test_parse_cookie_basic():
    c = cli._parse_cookie("sid=ABC;domain=.acme.test;path=/admin")
    assert c["name"] == "sid"
    assert c["value"] == "ABC"
    assert c["domain"] == ".acme.test"
    assert c["path"] == "/admin"


def test_build_auth_returns_none_when_no_credentials():
    args = cli._build_parser().parse_args(["--url", "https://x.test/"])
    assert cli._build_auth(args) is None

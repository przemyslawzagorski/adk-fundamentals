"""Tests for AuditConfig — env reading, allowlist, factory pattern."""
from __future__ import annotations

import os
import pathlib

import pytest

from adk_training.module_24_audit_ops.config import AuditConfig


def test_defaults_when_no_env(monkeypatch, tmp_path):
    for k in list(os.environ):
        if k.startswith("AUDITOPS_"):
            monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("AUDITOPS_ARTIFACTS_DIR", str(tmp_path))
    cfg = AuditConfig.from_env()
    assert cfg.allowed_domains == []
    assert cfg.require_disclaimer is True
    assert cfg.headless is True
    assert cfg.record_video is True
    assert cfg.browser == "chromium"
    assert cfg.max_scenarios == 8
    assert cfg.artifacts_dir == pathlib.Path(tmp_path).resolve()


def test_env_changes_apply_after_import(monkeypatch, tmp_path):
    """Critical: previous version captured env at class-definition time."""
    monkeypatch.setenv("AUDITOPS_RATE_LIMIT_RPS", "3.5")
    monkeypatch.setenv("AUDITOPS_ALLOWED_DOMAINS", "example.com, localhost ,example.org")
    monkeypatch.setenv("AUDITOPS_REQUIRE_DISCLAIMER", "0")
    monkeypatch.setenv("AUDITOPS_BROWSER", "firefox")
    monkeypatch.setenv("AUDITOPS_MAX_SCENARIOS", "2")
    monkeypatch.setenv("AUDITOPS_ARTIFACTS_DIR", str(tmp_path))

    cfg = AuditConfig.from_env()

    assert cfg.rate_limit_rps == 3.5
    assert cfg.allowed_domains == ["example.com", "localhost", "example.org"]
    assert cfg.require_disclaimer is False
    assert cfg.browser == "firefox"
    assert cfg.max_scenarios == 2


@pytest.mark.parametrize("url, allow, expected", [
    ("https://example.com/", ["example.com"], True),
    ("https://api.example.com/", ["example.com"], True),
    ("https://evil.com/", ["example.com"], False),
    ("https://localhost:8080/", ["localhost"], True),
    ("https://anything.test/", [], True),  # empty allowlist = all
    ("https://example.com.evil.com/", ["example.com"], False),  # not a real subdomain
    ("https://EXAMPLE.com/", ["example.com"], True),
])
def test_is_domain_allowed(url, allow, expected, monkeypatch, tmp_path):
    monkeypatch.setenv("AUDITOPS_ARTIFACTS_DIR", str(tmp_path))
    cfg = AuditConfig.from_env()
    cfg.allowed_domains = allow
    assert cfg.is_domain_allowed(url) is expected

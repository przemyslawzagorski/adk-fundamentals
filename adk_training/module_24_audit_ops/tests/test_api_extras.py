"""Tests for new API endpoints (auth, compare, junit)."""
import importlib
import json

from fastapi.testclient import TestClient


def _client(monkeypatch, tmp_path):
    monkeypatch.setenv("AUDITOPS_ALLOWED_DOMAINS", "example.test")
    monkeypatch.setenv("AUDITOPS_ARTIFACTS_DIR", str(tmp_path))
    monkeypatch.setenv("AUDITOPS_REQUIRE_DISCLAIMER", "0")
    from adk_training.module_24_audit_ops import config as cfg_mod
    importlib.reload(cfg_mod)
    from adk_training.module_24_audit_ops import api as api_mod
    importlib.reload(api_mod)
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(api_mod.router)
    return TestClient(app), api_mod, tmp_path


def test_register_auth_returns_id_no_secrets(monkeypatch, tmp_path):
    c, _, _ = _client(monkeypatch, tmp_path)
    r = c.post("/api/audit/auth", json={
        "label": "staging",
        "cookies": [{"name": "sid", "value": "topsecret", "domain": ".example.test"}],
        "headers": {"Authorization": "Bearer ZZZ"},
    })
    assert r.status_code == 200
    body = r.json()
    assert "id" in body
    # response must not echo back secret values
    assert "topsecret" not in r.text
    assert "ZZZ" not in r.text


def test_list_auth_omits_values(monkeypatch, tmp_path):
    c, _, _ = _client(monkeypatch, tmp_path)
    c.post("/api/audit/auth", json={"headers": {"X-Trace": "v1"}})
    r = c.get("/api/audit/auth")
    assert r.status_code == 200
    assert "v1" not in r.text


def test_delete_auth(monkeypatch, tmp_path):
    c, _, _ = _client(monkeypatch, tmp_path)
    auth_id = c.post("/api/audit/auth", json={"headers": {"X-A": "1"}}).json()["id"]
    assert c.delete(f"/api/audit/auth/{auth_id}").status_code == 200
    assert c.delete(f"/api/audit/auth/{auth_id}").status_code == 404


def test_register_auth_rejects_crlf_header(monkeypatch, tmp_path):
    c, _, _ = _client(monkeypatch, tmp_path)
    r = c.post("/api/audit/auth", json={"headers": {"X-Bad": "v\r\nInjected: 1"}})
    assert r.status_code == 400


def test_compare_endpoint(monkeypatch, tmp_path):
    c, _, root = _client(monkeypatch, tmp_path)
    for rid, sev in [("r_a", "high"), ("r_b", "low")]:
        d = root / rid
        d.mkdir()
        (d / "report.json").write_text(json.dumps({
            "run_id": rid, "target_url": "https://example.test/",
            "findings": [{"scenario_id": "x", "severity": sev, "title": "t"}],
            "scenarios": [{"id": "x", "passed": False, "findings": []}],
        }))
    r = c.get("/api/audit/compare", params={"a": "r_a", "b": "r_b"})
    assert r.status_code == 200
    body = r.json()
    assert body["summary"]["new"] == 1
    assert body["summary"]["fixed"] == 1


def test_compare_markdown_format(monkeypatch, tmp_path):
    c, _, root = _client(monkeypatch, tmp_path)
    for rid in ("r_a", "r_b"):
        d = root / rid
        d.mkdir()
        (d / "report.json").write_text(json.dumps({
            "run_id": rid, "target_url": "https://example.test/",
            "findings": [], "scenarios": [],
        }))
    r = c.get("/api/audit/compare", params={"a": "r_a", "b": "r_b", "fmt": "markdown"})
    assert r.status_code == 200
    assert "AuditOps Diff" in r.text


def test_compare_404_when_run_missing(monkeypatch, tmp_path):
    c, _, _ = _client(monkeypatch, tmp_path)
    r = c.get("/api/audit/compare", params={"a": "no", "b": "no"})
    assert r.status_code == 404


def test_junit_endpoint(monkeypatch, tmp_path):
    c, _, root = _client(monkeypatch, tmp_path)
    d = root / "rj"
    d.mkdir()
    (d / "report.json").write_text(json.dumps({
        "run_id": "rj", "target_url": "https://example.test/",
        "duration_s": 0.5,
        "findings": [{"scenario_id": "s1", "severity": "high", "title": "boom"}],
        "scenarios": [{"id": "s1", "name": "S1", "passed": False, "duration_s": 0.1,
                       "findings": [{"scenario_id": "s1", "severity": "high", "title": "boom"}],
                       "error": None}],
    }))
    r = c.get("/api/audit/runs/rj/junit", params={"fail_on": "high"})
    assert r.status_code == 200
    assert "<testsuite" in r.text
    assert "<failure" in r.text


def test_start_rejects_unknown_auth_id(monkeypatch, tmp_path):
    c, _, _ = _client(monkeypatch, tmp_path)
    r = c.post("/api/audit/start", json={
        "url": "https://example.test/", "auth_id": "nope",
    })
    assert r.status_code == 404

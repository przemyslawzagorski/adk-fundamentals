"""API smoke tests — disclaimer flow, ack-host binding, config endpoint, runs listing."""
from __future__ import annotations

import os
from pathlib import Path

import pytest

# We must set artifacts dir BEFORE importing api (it instantiates _CFG at import time)
@pytest.fixture(autouse=True)
def _set_artifacts(tmp_path, monkeypatch):
    monkeypatch.setenv("AUDITOPS_ARTIFACTS_DIR", str(tmp_path))
    monkeypatch.setenv("AUDITOPS_REQUIRE_DISCLAIMER", "1")
    # Force reimport to pick up new env
    import importlib
    import adk_training.module_24_audit_ops.config as cfg_mod
    import adk_training.module_24_audit_ops.api as api_mod
    importlib.reload(cfg_mod)
    importlib.reload(api_mod)
    yield


def _client():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from adk_training.module_24_audit_ops.api import router

    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_get_config():
    c = _client()
    r = c.get("/api/audit/config")
    assert r.status_code == 200
    data = r.json()
    for key in ("allowed_domains", "require_disclaimer", "rate_limit_rps", "playwright"):
        assert key in data
    assert "installed" in data["playwright"]


def test_disclaimer_must_accept():
    c = _client()
    r = c.post("/api/audit/disclaimer/ack", json={
        "target_url": "https://example.com/", "user_id": "u", "accepted": False,
    })
    assert r.status_code == 400


def test_disclaimer_returns_token():
    c = _client()
    r = c.post("/api/audit/disclaimer/ack", json={
        "target_url": "https://example.com/", "user_id": "u", "accepted": True,
    })
    assert r.status_code == 200
    body = r.json()
    assert body["token"]
    assert "authorization" in body["statement"].lower()


def test_start_rejects_when_ack_host_mismatch():
    c = _client()
    ack = c.post("/api/audit/disclaimer/ack", json={
        "target_url": "https://example.com/", "user_id": "u", "accepted": True,
    }).json()
    # Try to use the same token for a different host
    r = c.post("/api/audit/start", json={
        "url": "https://different-target.test/",
        "mode": "auto",
        "ack_token": ack["token"],
    })
    assert r.status_code == 400
    assert "host" in r.text.lower()


def test_runs_endpoint_empty():
    c = _client()
    r = c.get("/api/audit/runs")
    assert r.status_code == 200
    assert r.json() == {"runs": []}


def test_artifact_path_traversal_blocked():
    c = _client()
    # Prepare a fake run dir and a file outside
    from adk_training.module_24_audit_ops.api import _CFG  # noqa: PLC2701
    run_dir = _CFG.artifacts_dir / "test_run_x"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "ok.txt").write_text("inside", encoding="utf-8")
    outside = _CFG.artifacts_dir.parent / "secret.txt"
    outside.write_text("nope", encoding="utf-8")
    try:
        r = c.get("/api/audit/artifact/test_run_x/../secret.txt")
        # FastAPI route will not even match (the path:path eats `../`); confirm we don't leak content
        assert r.status_code in (400, 404)
        assert "nope" not in r.text
    finally:
        outside.unlink(missing_ok=True)

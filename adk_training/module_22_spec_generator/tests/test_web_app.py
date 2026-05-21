"""Test HTTP layer web/app.py (bez realnych MCP)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from web.app import app  # noqa: E402


@pytest.fixture
def client():
    return TestClient(app)


def test_health_should_return_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_index_should_return_html(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Spec Generator" in r.text


def test_generate_should_return_session_and_scaffold_hld(client):
    r = client.post("/api/generate", json={
        "issue_key": "SWOK-999",
        "enable_notebooklm": False,
        "max_critique_iterations": 2,
    })
    assert r.status_code == 200
    data = r.json()
    assert data["session_id"]
    assert "SWOK-999" in data["hld_markdown"]
    assert len(data["epics"]) >= 1
    assert data["status"] == "scaffold"


def test_publish_should_fail_without_approval(client):
    gen = client.post("/api/generate", json={
        "issue_key": "SWOK-1",
        "enable_notebooklm": False,
        "max_critique_iterations": 2,
    }).json()
    sid = gen["session_id"]

    r = client.post(f"/api/publish/{sid}", json={
        "session_id": sid, "approved": False,
    })
    assert r.status_code == 400


def test_publish_should_return_scaffold_for_unknown_session(client):
    r = client.post("/api/publish/unknown_sid", json={
        "session_id": "unknown_sid", "approved": True,
    })
    assert r.status_code == 404


def test_publish_should_echo_when_approved(client):
    gen = client.post("/api/generate", json={
        "issue_key": "SWOK-2",
        "enable_notebooklm": False,
        "max_critique_iterations": 1,
    }).json()
    sid = gen["session_id"]
    r = client.post(f"/api/publish/{sid}", json={
        "session_id": sid, "approved": True,
    })
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "scaffold"
    assert len(data["would_publish"]) >= 1


def test_generate_should_use_real_pipeline_when_flag_set(client, monkeypatch):
    """Gdy SPEC_GEN_USE_REAL_PIPELINE=1 + GOOGLE_CLOUD_PROJECT ustawione,
    endpoint powinien zawolac `_run_real_pipeline` zamiast scaffold."""
    import web.app as webapp

    async def fake_pipeline(req):
        return ("# HLD: REAL\n## 1. Cel biznesowy\nZrobione.", [
            {"title": "[FAKE-1] E1", "summary": "s", "acceptance_criteria": [],
             "priority": "High", "labels": [], "estimated_story_points": 3, "dependencies": []},
        ])

    monkeypatch.setenv("SPEC_GEN_USE_REAL_PIPELINE", "1")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "fake-project")
    monkeypatch.setattr(webapp, "_run_real_pipeline", fake_pipeline)

    r = client.post("/api/generate", json={
        "issue_key": "FAKE-1",
        "enable_notebooklm": False,
        "max_critique_iterations": 1,
    })
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "real"
    assert "REAL" in data["hld_markdown"]
    assert data["epics"][0]["title"] == "[FAKE-1] E1"


def test_generate_real_pipeline_error_returns_500(client, monkeypatch):
    import web.app as webapp

    async def boom(req):
        raise RuntimeError("gemini exploded")

    monkeypatch.setenv("SPEC_GEN_USE_REAL_PIPELINE", "1")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "fake-project")
    monkeypatch.setattr(webapp, "_run_real_pipeline", boom)

    r = client.post("/api/generate", json={
        "issue_key": "FAKE-2",
        "enable_notebooklm": False,
        "max_critique_iterations": 1,
    })
    assert r.status_code == 500
    assert "gemini exploded" in r.json()["detail"]


def test_health_reports_real_pipeline_flag(client, monkeypatch):
    monkeypatch.delenv("SPEC_GEN_USE_REAL_PIPELINE", raising=False)
    r = client.get("/health")
    assert r.json()["real_pipeline"] is False

    monkeypatch.setenv("SPEC_GEN_USE_REAL_PIPELINE", "1")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "x")
    r = client.get("/health")
    assert r.json()["real_pipeline"] is True

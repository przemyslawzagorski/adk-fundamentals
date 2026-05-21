"""Tests for video recording wiring in AuditOps.

User reported: "w audit nie nagrywaja sie filmiki".

These tests verify:
  1. Default ``AuditConfig`` enables recording (``record_video=True``).
  2. ``/api/audit/config`` exposes the same value to the frontend.
  3. The Playwright runner *would* pass ``record_video_dir`` to ``new_context``
     when recording is enabled.
  4. ``video_url_from_path`` correctly maps disk paths to ``/artifacts`` URLs.
  5. Mounted ``/artifacts/...`` static route serves files from the artifacts dir.

If 1-4 pass and the user still sees no videos, the cause is one of:
  - Playwright browsers not installed (``playwright install chromium``)
  - Scenarios returning an early DSL error (no browser context ever opened)
  - Frontend ignoring ``video`` field on ``scenario_finished`` events
"""
from __future__ import annotations

import importlib
import json
import os
from pathlib import Path

import pytest


@pytest.fixture
def fresh_cfg(tmp_path, monkeypatch):
    monkeypatch.setenv("AUDITOPS_ARTIFACTS_DIR", str(tmp_path))
    monkeypatch.delenv("AUDITOPS_RECORD_VIDEO", raising=False)
    import adk_training.module_24_audit_ops.config as cfg_mod
    importlib.reload(cfg_mod)
    return cfg_mod


def test_record_video_default_enabled(fresh_cfg):
    cfg = fresh_cfg.AuditConfig.from_env()
    assert cfg.record_video is True, \
        "Default must enable recording — otherwise the UI will never show videos."


def test_record_video_can_be_disabled_via_env(monkeypatch, tmp_path):
    monkeypatch.setenv("AUDITOPS_ARTIFACTS_DIR", str(tmp_path))
    monkeypatch.setenv("AUDITOPS_RECORD_VIDEO", "0")
    import adk_training.module_24_audit_ops.config as cfg_mod
    importlib.reload(cfg_mod)
    cfg = cfg_mod.AuditConfig.from_env()
    assert cfg.record_video is False


def test_api_config_reports_record_video(tmp_path, monkeypatch):
    """The /api/audit/config endpoint must expose ``record_video`` for the UI banner."""
    monkeypatch.setenv("AUDITOPS_ARTIFACTS_DIR", str(tmp_path))
    monkeypatch.delenv("AUDITOPS_RECORD_VIDEO", raising=False)
    import adk_training.module_24_audit_ops.config as cfg_mod
    import adk_training.module_24_audit_ops.api as api_mod
    importlib.reload(cfg_mod)
    importlib.reload(api_mod)

    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    app = FastAPI()
    app.include_router(api_mod.router)
    client = TestClient(app)

    r = client.get("/api/audit/config")
    assert r.status_code == 200
    data = r.json()
    assert data["record_video"] is True
    # Playwright availability is best-effort; never raise.
    assert "playwright" in data
    assert "installed" in data["playwright"]


def test_video_url_from_path_under_artifacts(fresh_cfg, tmp_path):
    """Files inside artifacts dir get mapped to /artifacts/... URL."""
    from adk_training.module_24_audit_ops import playwright_runner as pr

    cfg = fresh_cfg.AuditConfig.from_env()
    sample = cfg.artifacts_dir / "run_42" / "scn_a" / "video" / "vid.webm"
    sample.parent.mkdir(parents=True, exist_ok=True)
    sample.write_bytes(b"fake-webm")

    url = pr.video_url_from_path(str(sample), cfg)
    assert url is not None
    assert url.startswith("/artifacts/")
    assert url.endswith("vid.webm")


def test_video_url_from_path_outside_artifacts_returns_none(fresh_cfg, tmp_path):
    from adk_training.module_24_audit_ops import playwright_runner as pr
    cfg = fresh_cfg.AuditConfig.from_env()
    outside = tmp_path.parent / "elsewhere.webm"
    outside.write_bytes(b"x")
    assert pr.video_url_from_path(str(outside), cfg) is None


def test_video_url_from_path_handles_none(fresh_cfg):
    from adk_training.module_24_audit_ops import playwright_runner as pr
    cfg = fresh_cfg.AuditConfig.from_env()
    assert pr.video_url_from_path(None, cfg) is None


def test_artifacts_static_route_serves_files(tmp_path, monkeypatch):
    """``/artifacts/...`` mount in the concierge app must serve recorded videos."""
    monkeypatch.setenv("AUDITOPS_ARTIFACTS_DIR", str(tmp_path))
    monkeypatch.setenv("CONCIERGE_RUNS_DIR", str(tmp_path / "concierge_runs"))
    monkeypatch.setenv("AUGGIE_USE_CLI", "0")

    # Plant a fake video before importing the app so StaticFiles sees it
    sample = tmp_path / "demo_run" / "demo_scn" / "video" / "movie.webm"
    sample.parent.mkdir(parents=True, exist_ok=True)
    sample.write_bytes(b"VIDEO-BYTES")

    import adk_training.module_24_audit_ops.config as cfg_mod
    import adk_training.module_24_audit_ops.api as audit_api
    from adk_training.module_23_auggie_integration.web import app as app_mod
    importlib.reload(cfg_mod)
    importlib.reload(audit_api)
    importlib.reload(app_mod)

    from fastapi.testclient import TestClient
    client = TestClient(app_mod.app)

    r = client.get("/artifacts/demo_run/demo_scn/video/movie.webm")
    assert r.status_code == 200, \
        "Static /artifacts mount should serve files — videos depend on this."
    assert r.content == b"VIDEO-BYTES"


def test_playwright_context_kwargs_include_record_video_dir(monkeypatch, tmp_path):
    """Verify the runner *intends* to record video when cfg.record_video=True.

    We don't launch a real browser — instead we monkey-patch ``async_playwright``
    to capture the ``new_context`` kwargs and bail out early.
    """
    monkeypatch.setenv("AUDITOPS_ARTIFACTS_DIR", str(tmp_path))
    monkeypatch.setenv("AUDITOPS_RECORD_VIDEO", "1")

    import adk_training.module_24_audit_ops.config as cfg_mod
    import adk_training.module_24_audit_ops.playwright_runner as pr_mod
    importlib.reload(cfg_mod)
    importlib.reload(pr_mod)

    cfg = cfg_mod.AuditConfig.from_env()

    # Skip if Playwright not installed — this test cannot prove the wiring without it.
    try:
        import playwright  # noqa: F401
    except ImportError:
        pytest.skip("playwright not installed — wiring asserted indirectly via static mount test")

    captured: dict = {}

    class _FakeContext:
        async def add_cookies(self, *a, **kw): pass
        def set_default_navigation_timeout(self, *a, **kw): pass
        def set_default_timeout(self, *a, **kw): pass
        async def new_page(self):
            raise RuntimeError("__captured__")  # bail out fast
        async def close(self): pass

    class _FakeBrowser:
        async def new_context(self, **kwargs):
            captured.update(kwargs)
            return _FakeContext()
        async def close(self): pass

    class _FakeFactory:
        async def launch(self, *a, **kw):
            return _FakeBrowser()

    class _FakePW:
        chromium = _FakeFactory()
        firefox = _FakeFactory()
        webkit = _FakeFactory()
        async def __aenter__(self): return self
        async def __aexit__(self, *a): return False

    monkeypatch.setattr("playwright.async_api.async_playwright", lambda: _FakePW())

    import asyncio
    from adk_training.module_24_audit_ops.playwright_runner import run_scenario, RateLimiter

    scenario = {
        "id": "test_scenario",
        "name": "T",
        "owasp": "A01",
        "severity": "info",
        "steps": [{"action": "goto", "url": "http://example.com"}],
    }
    rl = RateLimiter(rps=cfg.rate_limit_rps)
    asyncio.get_event_loop().run_until_complete(
        run_scenario(scenario, cfg, rl, "test_run", on_event=None)
    )

    assert "record_video_dir" in captured, \
        "record_video=True must propagate to Playwright new_context kwargs"
    assert "video" in captured["record_video_dir"]
    assert captured["record_video_size"] == {
        "width": cfg.viewport_width, "height": cfg.viewport_height,
    }

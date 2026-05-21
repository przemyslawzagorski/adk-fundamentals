"""Backend API smoke + integration tests for Auggie Concierge web app.

These tests are designed to **pinpoint where the GUI problems originate**:
  - If the API endpoint returns 200 with correct shape but the UI shows nothing,
    the bug is in the React layer.
  - If the test fails (timeout, 500), the bug is in the backend / Auggie CLI.

We monkeypatch the heavy ``auggie_tools`` functions so the SSE pipeline can be
exercised in milliseconds without invoking the real CLI subprocess.
"""
from __future__ import annotations

import importlib
import json
import time
from typing import Any, Iterator

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def app_env(tmp_path, monkeypatch):
    """Isolate runs dir + ensure deterministic env."""
    monkeypatch.setenv("CONCIERGE_RUNS_DIR", str(tmp_path / "runs"))
    monkeypatch.setenv("AUGGIE_USE_CLI", "0")
    monkeypatch.delenv("AUGGIE_TIMEOUT", raising=False)
    yield


@pytest.fixture
def client(app_env):
    from adk_training.module_23_auggie_integration.web import runs as runs_mod
    from adk_training.module_23_auggie_integration.web import app as app_mod
    importlib.reload(runs_mod)
    importlib.reload(app_mod)
    # The runs_store reference inside app_mod must point at the reloaded copy.
    app_mod.runs_store = runs_mod
    return TestClient(app_mod.app)


@pytest.fixture
def patched_tools(monkeypatch):
    """Stub every tool function with a fast deterministic echo."""
    import tools as auggie_tools  # type: ignore

    def _echo(**kwargs: Any) -> str:
        return json.dumps({"echo": kwargs})

    for name in ("ask_specialist", "code_review_pr", "analyze_codebase",
                 "generate_implementation", "refactor_workflow", "security_audit"):
        monkeypatch.setattr(auggie_tools, name, lambda **kw: _echo(**kw), raising=True)

    monkeypatch.setattr(auggie_tools, "auggie_health",
                        lambda: json.dumps({"healthy": True, "checks": []}), raising=True)
    monkeypatch.setattr(auggie_tools, "auggie_telemetry",
                        lambda: json.dumps({"summary": {}, "cache": {}, "circuit_breaker": {},
                                             "last_calls": []}), raising=True)
    monkeypatch.setattr(auggie_tools, "auggie_cost_report",
                        lambda: json.dumps({"total_calls": 0}), raising=True)
    return auggie_tools


def _read_sse(resp) -> list[dict[str, Any]]:
    """Parse a streaming SSE response into a list of event dicts."""
    events: list[dict[str, Any]] = []
    for line in resp.iter_lines():
        if not line:
            continue
        text = line.decode() if isinstance(line, bytes) else line
        if not text.startswith("data:"):
            continue
        try:
            events.append(json.loads(text[5:].strip()))
        except json.JSONDecodeError:
            continue
    return events


# ---------------------------------------------------------------------------
# Meta endpoints
# ---------------------------------------------------------------------------
class TestHealth:
    def test_basic_health_alive(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_api_health_returns_shape(self, client, patched_tools):
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.json() == {"healthy": True, "checks": []}


class TestCatalog:
    def test_tools_catalog_lists_six_tools(self, client):
        r = client.get("/api/tools")
        assert r.status_code == 200
        data = r.json()
        assert data["count"] == 6
        ids = {t["id"] for t in data["tools"]}
        assert ids == {
            "ask_specialist", "code_review_pr", "analyze_codebase",
            "generate_implementation", "refactor_workflow", "security_audit",
        }

    def test_each_tool_has_required_metadata(self, client):
        data = client.get("/api/tools").json()
        for t in data["tools"]:
            assert {"id", "name", "category", "icon", "tagline",
                    "description", "inputs", "estimated_seconds"} <= t.keys()
            assert isinstance(t["inputs"], list)


class TestTelemetryAndCost:
    def test_telemetry_normalised(self, client, patched_tools):
        r = client.get("/api/telemetry")
        assert r.status_code == 200
        data = r.json()
        # Normalised even when patched stub returns minimal dicts
        assert data["summary"]["total"] == 0
        assert data["cache"]["hits"] == 0
        assert data["circuit_breaker"]["state"] == "closed"
        assert data["last_calls"] == []

    def test_cost_normalised(self, client, patched_tools):
        r = client.get("/api/cost")
        assert r.status_code == 200
        data = r.json()
        assert data["total_calls"] == 0
        assert "by_tool_usd" in data

    def test_cache_clear(self, client):
        r = client.post("/api/cache/clear")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


class TestConfig:
    def test_config_exposes_runtime_info(self, client):
        r = client.get("/api/config")
        assert r.status_code == 200
        data = r.json()
        for key in ("model", "timeout", "max_turns", "workspace",
                    "use_cli_fallback", "platform", "index"):
            assert key in data


class TestIndexStatus:
    def test_index_status_default_idle(self, client):
        r = client.get("/api/index/status")
        assert r.status_code == 200
        assert r.json()["status"] in ("idle", "ready", "running", "failed")


# ---------------------------------------------------------------------------
# Tool execution (SSE)
# ---------------------------------------------------------------------------
class TestToolRun:
    def test_unknown_tool_404(self, client):
        r = client.post("/api/tools/run", json={"tool_id": "does_not_exist", "inputs": {}})
        assert r.status_code == 404

    def test_security_audit_target_dot_rejected(self, client, patched_tools):
        """Critical safety guard — must reject workspace-wide scans."""
        for bad in [".", "./", "", "/"]:
            r = client.post("/api/tools/run",
                            json={"tool_id": "security_audit", "inputs": {"target": bad}})
            assert r.status_code == 400, f"target={bad!r} should be rejected"
            assert "konkretną ścieżkę" in r.json()["detail"]

    def test_security_audit_with_real_path_runs(self, client, patched_tools):
        with client.stream("POST", "/api/tools/run", json={
            "tool_id": "security_audit", "inputs": {"target": "src/"},
        }) as resp:
            assert resp.status_code == 200
            evs = _read_sse(resp)
        types = [e["type"] for e in evs]
        assert types[0] == "start"
        assert "result" in types
        assert types[-1] == "end"

    def test_ask_specialist_full_lifecycle(self, client, patched_tools):
        with client.stream("POST", "/api/tools/run", json={
            "tool_id": "ask_specialist",
            "inputs": {"question": "What is DI?"},
        }) as resp:
            assert resp.status_code == 200
            evs = _read_sse(resp)

        types = [e["type"] for e in evs]
        assert types[0] == "start"
        assert evs[0]["tool"] == "ask_specialist"
        assert "run_id" in evs[0]
        result = next(e for e in evs if e["type"] == "result")
        assert result["output_kind"] == "text"
        assert "echo" in result["output"]
        end = evs[-1]
        assert end["type"] == "end"
        assert end["success"] is True

    @pytest.mark.parametrize("tool_id, inputs", [
        ("ask_specialist", {"question": "ping"}),
        ("code_review_pr", {"diff": "diff --git a/x b/x\n+hi"}),
        ("analyze_codebase", {"focus_paths": "src/", "max_files": "5"}),
        ("generate_implementation", {"spec": "x"}),
        ("refactor_workflow", {"target_file": "a.py", "refactor_goal": "split"}),
        ("security_audit", {"target": "src/"}),
    ])
    def test_every_catalog_tool_streams_to_completion(self, client, patched_tools,
                                                      tool_id, inputs):
        """Each of the 6 production tools must be invokable via the SSE pipeline.

        If this fails for a specific tool but its stub is identical, the bug is
        in app.py routing or _coerce_inputs — not in the tool itself.
        """
        with client.stream("POST", "/api/tools/run",
                           json={"tool_id": tool_id, "inputs": inputs}) as resp:
            assert resp.status_code == 200
            evs = _read_sse(resp)
        types = [e["type"] for e in evs]
        assert types[0] == "start"
        assert types[-1] == "end"
        assert "result" in types or "error" in types

    def test_missing_required_input_400(self, client, patched_tools):
        r = client.post("/api/tools/run", json={
            "tool_id": "ask_specialist", "inputs": {},
        })
        assert r.status_code == 400
        assert "question" in r.json()["detail"]

    def test_tool_exception_is_streamed_as_error(self, client, monkeypatch):
        import tools as auggie_tools  # type: ignore

        def _boom(**_):
            raise RuntimeError("kaboom")

        monkeypatch.setattr(auggie_tools, "ask_specialist", _boom, raising=True)

        with client.stream("POST", "/api/tools/run", json={
            "tool_id": "ask_specialist", "inputs": {"question": "x"},
        }) as resp:
            assert resp.status_code == 200
            evs = _read_sse(resp)

        err = next(e for e in evs if e["type"] == "error")
        assert err["exception"] == "RuntimeError"
        assert "kaboom" in err["message"]
        end = evs[-1]
        assert end["type"] == "end"
        assert end["success"] is False


# ---------------------------------------------------------------------------
# Run history
# ---------------------------------------------------------------------------
class TestRunHistory:
    def test_runs_list_empty_initially(self, client):
        r = client.get("/api/runs")
        assert r.status_code == 200
        assert r.json() == {"runs": [], "count": 0}

    def test_run_persisted_after_tool_invocation(self, client, patched_tools):
        with client.stream("POST", "/api/tools/run", json={
            "tool_id": "ask_specialist", "inputs": {"question": "ping"},
        }) as resp:
            evs = _read_sse(resp)
        run_id = evs[0]["run_id"]

        # Listing
        rows = client.get("/api/runs").json()["runs"]
        assert any(r["run_id"] == run_id for r in rows)

        # Detail
        detail = client.get(f"/api/runs/{run_id}").json()
        assert detail["run_id"] == run_id
        assert detail["tool_id"] == "ask_specialist"
        assert detail["status"] == "ok"
        assert detail["inputs"] == {"question": "ping"}
        assert "echo" in detail["output"]
        assert isinstance(detail["events"], list)
        assert detail["events"][0]["type"] == "start"

    def test_run_filter_by_tool_id(self, client, patched_tools):
        for tid, inputs in [
            ("ask_specialist", {"question": "a"}),
            ("security_audit", {"target": "src/"}),
        ]:
            with client.stream("POST", "/api/tools/run",
                               json={"tool_id": tid, "inputs": inputs}) as resp:
                _read_sse(resp)

        only = client.get("/api/runs", params={"tool_id": "ask_specialist"}).json()
        assert all(r["tool_id"] == "ask_specialist" for r in only["runs"])
        assert len(only["runs"]) >= 1

    def test_run_detail_404(self, client):
        r = client.get("/api/runs/nonexistent")
        assert r.status_code == 404

    def test_failed_run_persists_with_error(self, client, monkeypatch):
        import tools as auggie_tools  # type: ignore
        monkeypatch.setattr(auggie_tools, "ask_specialist",
                            lambda **_: (_ for _ in ()).throw(ValueError("nope")),
                            raising=True)

        with client.stream("POST", "/api/tools/run", json={
            "tool_id": "ask_specialist", "inputs": {"question": "x"},
        }) as resp:
            evs = _read_sse(resp)
        run_id = evs[0]["run_id"]

        detail = client.get(f"/api/runs/{run_id}").json()
        assert detail["status"] == "error"
        assert detail["error"]["exception"] == "ValueError"
        assert "nope" in detail["error"]["message"]

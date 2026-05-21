"""Unit tests for web/runs.py — file-backed run history store."""
from __future__ import annotations

import importlib
import json
import os
import time
from pathlib import Path

import pytest


@pytest.fixture
def runs(tmp_path, monkeypatch):
    """Reload the runs module against a temporary CONCIERGE_RUNS_DIR."""
    monkeypatch.setenv("CONCIERGE_RUNS_DIR", str(tmp_path / "concierge_runs"))
    from adk_training.module_23_auggie_integration.web import runs as runs_mod
    importlib.reload(runs_mod)
    return runs_mod


def _record(runs_mod, **overrides):
    rid = runs_mod.new_run_id()
    rec = runs_mod.make_pending(rid, "ask_specialist", "Ask Specialist",
                                {"question": "ping"})
    rec.update(overrides)
    return rec


def test_new_run_id_unique(runs):
    a = runs.new_run_id()
    b = runs.new_run_id()
    assert a != b
    assert len(a) == 12


def test_make_pending_shape(runs):
    rec = runs.make_pending("abc123", "tid", "Tool", {"k": "v"})
    assert rec["run_id"] == "abc123"
    assert rec["status"] == "running"
    assert rec["inputs"] == {"k": "v"}
    assert rec["inputs_summary"] == "k=v"
    assert isinstance(rec["started_at"], float)
    assert rec["logs"] == []
    assert rec["events"] == []


def test_summarize_inputs_truncates(runs):
    rec = runs.make_pending("x", "t", "T", {"diff": "a" * 200})
    assert "..." in rec["inputs_summary"]
    assert len(rec["inputs_summary"]) <= 240


def test_save_and_get_run_roundtrip(runs):
    rec = _record(runs, status="ok", duration_s=1.23, output="hello",
                  finished_at=time.time())
    runs.save_run(rec)

    fetched = runs.get_run(rec["run_id"])
    assert fetched is not None
    assert fetched["status"] == "ok"
    assert fetched["output"] == "hello"
    assert fetched["duration_s"] == 1.23


def test_list_runs_newest_first(runs):
    for i in range(3):
        rec = _record(runs)
        rec["status"] = "ok"
        rec["started_at"] = 1000.0 + i
        runs.save_run(rec)

    rows = runs.list_runs(limit=10)
    assert len(rows) == 3
    assert rows[0]["started_at"] >= rows[1]["started_at"] >= rows[2]["started_at"]


def test_list_runs_filter_by_tool(runs):
    a = _record(runs)
    a["tool_id"] = "ask_specialist"
    a["status"] = "ok"
    runs.save_run(a)
    b = _record(runs)
    b["tool_id"] = "security_audit"
    b["status"] = "ok"
    runs.save_run(b)

    asks = runs.list_runs(tool_id="ask_specialist")
    assert len(asks) == 1
    assert asks[0]["tool_id"] == "ask_specialist"


def test_get_run_unknown_returns_none(runs):
    assert runs.get_run("nonexistent_id") is None


def test_save_run_persists_full_record_to_disk(runs, tmp_path):
    rec = _record(runs, status="ok", logs=[{"ts": 1.0, "level": "info", "message": "hi"}])
    runs.save_run(rec)
    fp = Path(os.environ["CONCIERGE_RUNS_DIR"]) / f"{rec['run_id']}.json"
    assert fp.is_file()
    on_disk = json.loads(fp.read_text(encoding="utf-8"))
    assert on_disk["logs"] == [{"ts": 1.0, "level": "info", "message": "hi"}]


def test_load_index_picks_up_existing_files(runs, tmp_path):
    # Write a file directly, then reload module to trigger _load_index
    d = Path(os.environ["CONCIERGE_RUNS_DIR"])
    d.mkdir(parents=True, exist_ok=True)
    (d / "manual123.json").write_text(json.dumps({
        "run_id": "manual123",
        "tool_id": "ask_specialist",
        "tool_name": "Ask Specialist",
        "status": "ok",
        "started_at": 999.0,
        "duration_s": 0.1,
    }), encoding="utf-8")

    importlib.reload(runs)
    rows = runs.list_runs()
    assert any(r["run_id"] == "manual123" for r in rows)

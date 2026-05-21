"""Concierge run history — file-backed store for tool runs.

Each run is persisted as a single JSON file under ``<artifacts>/concierge_runs/``.
A small in-memory index keeps the last N records hot for fast listing.

This module is intentionally tiny — no DB dependency. Format is forward
compatible (extra keys are preserved).
"""
from __future__ import annotations

import json
import logging
import os
import threading
import time
import uuid
from pathlib import Path
from typing import Any

logger = logging.getLogger("concierge.runs")


def _runs_dir() -> Path:
    """Resolve the on-disk directory for concierge run history."""
    base = os.environ.get("CONCIERGE_RUNS_DIR")
    if base:
        return Path(base).expanduser()
    art = os.environ.get("CONCIERGE_ARTIFACTS_DIR")
    if art:
        return Path(art).expanduser() / "concierge_runs"
    # Fallback: artifacts/ sibling to the repo root OR next to backend package.
    # Resolves correctly both in adk-fundamentals and in a standalone repository.
    _here = Path(__file__).resolve()
    # Walk up to find a directory that contains an 'artifacts' folder or .git root.
    for candidate in [_here.parent.parent, *_here.parents]:
        if (candidate / ".git").exists() or (candidate / "artifacts").exists():
            return candidate / "artifacts" / "concierge_runs"
    # Last resort: sibling of the web/ package dir
    return _here.parent.parent / "artifacts" / "concierge_runs"


_LOCK = threading.Lock()
_INDEX: list[dict[str, Any]] = []   # newest first
_MAX_INDEX = 500
_LOADED = False


def _load_index() -> None:
    global _LOADED
    if _LOADED:
        return
    d = _runs_dir()
    d.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for fp in d.glob("*.json"):
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            logger.warning("skip unreadable run %s: %s", fp.name, e)
            continue
        rows.append({
            "run_id": data.get("run_id") or fp.stem,
            "tool_id": data.get("tool_id"),
            "tool_name": data.get("tool_name"),
            "status": data.get("status"),
            "started_at": data.get("started_at"),
            "duration_s": data.get("duration_s"),
            "cached": data.get("cached"),
            "inputs_summary": data.get("inputs_summary"),
            "error": (data.get("error") or {}).get("message") if data.get("error") else None,
        })
    rows.sort(key=lambda r: r.get("started_at") or 0, reverse=True)
    _INDEX[:] = rows[:_MAX_INDEX]
    _LOADED = True


def new_run_id() -> str:
    return uuid.uuid4().hex[:12]


def _summarize_inputs(inputs: dict[str, Any]) -> str:
    if not inputs:
        return ""
    parts = []
    for k, v in inputs.items():
        s = str(v)
        if len(s) > 60:
            s = s[:57] + "..."
        parts.append(f"{k}={s}")
    out = " ".join(parts)
    return out[:240]


def save_run(record: dict[str, Any]) -> None:
    """Persist a complete run record. Updates in-memory index."""
    _load_index()
    run_id = record.get("run_id")
    if not run_id:
        return
    d = _runs_dir()
    d.mkdir(parents=True, exist_ok=True)
    fp = d / f"{run_id}.json"
    try:
        fp.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        logger.exception("failed to persist run %s: %s", run_id, e)
        return

    summary = {
        "run_id": run_id,
        "tool_id": record.get("tool_id"),
        "tool_name": record.get("tool_name"),
        "status": record.get("status"),
        "started_at": record.get("started_at"),
        "duration_s": record.get("duration_s"),
        "cached": record.get("cached"),
        "inputs_summary": record.get("inputs_summary") or _summarize_inputs(record.get("inputs") or {}),
        "error": (record.get("error") or {}).get("message") if record.get("error") else None,
    }
    with _LOCK:
        _INDEX[:] = [r for r in _INDEX if r.get("run_id") != run_id]
        _INDEX.insert(0, summary)
        del _INDEX[_MAX_INDEX:]


def list_runs(limit: int = 50, tool_id: str | None = None) -> list[dict[str, Any]]:
    _load_index()
    with _LOCK:
        rows = list(_INDEX)
    if tool_id:
        rows = [r for r in rows if r.get("tool_id") == tool_id]
    return rows[:limit]


def get_run(run_id: str) -> dict[str, Any] | None:
    fp = _runs_dir() / f"{run_id}.json"
    if not fp.is_file():
        return None
    try:
        return json.loads(fp.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        logger.warning("failed reading run %s: %s", run_id, e)
        return None


def make_pending(run_id: str, tool_id: str, tool_name: str, inputs: dict[str, Any]) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "tool_id": tool_id,
        "tool_name": tool_name,
        "inputs": inputs,
        "inputs_summary": _summarize_inputs(inputs),
        "status": "running",
        "started_at": time.time(),
        "logs": [],
        "events": [],
    }

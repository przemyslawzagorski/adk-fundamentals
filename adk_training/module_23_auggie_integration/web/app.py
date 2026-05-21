"""Web UI dla module_23 Auggie Concierge.

FastAPI + Vite/React frontend (blue/navy "Netflix vibe").

Endpointy:
  GET  /                           — entrypoint (HTML wrapper / link do frontendu)
  GET  /health                     — basic liveness
  GET  /api/health                 — pełny `auggie_health()` (CLI present, session, model, breaker)
  GET  /api/tools                  — katalog 9 narzędzi z metadanymi (kategoria, ikona, opis, schemat input)
  POST /api/index/start            — SSE: warm-up workspace index (`auggie --print noop --wait-for-indexing`)
  GET  /api/index/status           — status ostatniego warm-upa (in-memory)
  POST /api/tools/run              — SSE: uruchamia tool i streamuje progress + final result
  GET  /api/telemetry              — `auggie_telemetry()` JSON
  GET  /api/cost                   — `auggie_cost_report()` JSON
  POST /api/cache/clear            — czyści cache (do testów)

Uruchomienie:
  uvicorn adk_training.module_23_auggie_integration.web.app:app --port 8770 --reload

Frontend (dev):
  cd adk_training/module_23_auggie_integration/web/frontend && npm run dev
  → http://localhost:5173 (Vite proxy do 8770)
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import queue
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any, AsyncIterator, Optional

from fastapi import FastAPI, HTTPException
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Module root → sys.path (żeby `from auggie_factory ...` działało)
_MOD_ROOT = Path(__file__).resolve().parent.parent
if str(_MOD_ROOT) not in sys.path:
    sys.path.insert(0, str(_MOD_ROOT))

# Załaduj .env modułu (jeśli istnieje)
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv(_MOD_ROOT / ".env", override=False)
except ImportError:
    pass

import tools as auggie_tools  # noqa: E402
from auggie_factory import AuggieConfig, AuggieUnavailable  # noqa: E402
from auggie_factory import (  # noqa: E402
    register_log_cb, unregister_log_cb, kill_thread_subprocess,
)
from caching import CACHE  # noqa: E402

from . import runs as runs_store  # noqa: E402

logging.basicConfig(
    level=os.environ.get("CONCIERGE_LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    force=True,
)
logger = logging.getLogger("concierge.web")

app = FastAPI(title="Auggie Concierge", version="0.1.0")

_cors_origins = os.environ.get(
    "CONCIERGE_CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _cors_origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------------
# AuditOps — optional pentest/QA agent.
# Supports two import paths:
#   1. Standalone repo:    from audit_ops.api import ...
#   2. adk-fundamentals:  from adk_training.module_24_audit_ops.api import ...
# -----------------------------------------------------------------------------
try:
    try:
        from audit_ops.api import (  # standalone repo layout
            router as audit_router,
            get_artifacts_root as _audit_artifacts_root,
        )
    except ModuleNotFoundError:
        from adk_training.module_24_audit_ops.api import (  # adk-fundamentals layout
            router as audit_router,
            get_artifacts_root as _audit_artifacts_root,
        )
    app.include_router(audit_router)
    _ART_DIR = _audit_artifacts_root()
    _ART_DIR.mkdir(parents=True, exist_ok=True)
    app.mount("/artifacts", StaticFiles(directory=str(_ART_DIR)), name="artifacts")
    logger.info("AuditOps router mounted at /api/audit (artifacts: %s)", _ART_DIR)
except Exception as _audit_err:
    logger.warning("AuditOps router not loaded: %s", _audit_err)


# -----------------------------------------------------------------------------
# Analyst System (module_20) — Jira ticket -> HLD -> Epics pipeline.
# -----------------------------------------------------------------------------
try:
    from .api_analyst import router as analyst_router
    app.include_router(analyst_router)
    logger.info("Analyst router mounted at /api/analyst")
except Exception as _analyst_err:
    logger.warning("Analyst router not loaded: %s", _analyst_err)


# =============================================================================
# Tool catalog (metadane dla frontendu)
# =============================================================================
TOOL_CATALOG: list[dict[str, Any]] = [
    {
        "id": "ask_specialist",
        "name": "Ask Specialist",
        "category": "general",
        "icon": "MessageSquare",
        "tagline": "Zadaj pytanie ekspertowi (Claude Sonnet 4.5)",
        "description": "Generic delegation — najszybsza ścieżka. Cache + retry. Use-case: 'Wyjaśnij wzorzec X'.",
        "inputs": [
            {"name": "question", "type": "textarea", "label": "Pytanie", "required": True,
             "placeholder": "Wyjaśnij Dependency Injection w 3 zdaniach"},
        ],
        "estimated_seconds": 12,
    },
    {
        "id": "code_review_pr",
        "name": "Code Review PR",
        "category": "review",
        "icon": "GitPullRequest",
        "tagline": "Strukturalny review diffu z severity i sugestiami",
        "description": "Pełny stack: success_criteria + dataclass return. Wynik: lista ReviewIssue z severity/file/line.",
        "inputs": [
            {"name": "diff", "type": "textarea", "label": "Unified diff", "required": True,
             "placeholder": "diff --git a/src/foo.py b/src/foo.py\n@@ -1,3 +1,5 @@..."},
            {"name": "repo_context", "type": "input", "label": "Kontekst repo (opcjonalny)", "required": False,
             "placeholder": "FastAPI + SQLAlchemy backend"},
        ],
        "estimated_seconds": 30,
    },
    {
        "id": "analyze_codebase",
        "name": "Analyze Codebase",
        "category": "analysis",
        "icon": "Microscope",
        "tagline": "Audyt jakości kodu — typed return List[Finding]",
        "description": "Skanuje pliki i zwraca listę findings (komplikacja, duplikacja, antywzorce).",
        "inputs": [
            {"name": "target_path", "type": "input", "label": "Katalog do analizy", "required": False,
             "placeholder": "C:\\Users\\...\\module_23_auggie_integration"},
            {"name": "max_files", "type": "input", "label": "Max plików", "required": False,
             "default": "20", "input_type": "number"},
        ],
        "estimated_seconds": 60,
    },
    {
        "id": "generate_implementation",
        "name": "Generate Implementation",
        "category": "generate",
        "icon": "Code2",
        "tagline": "Spec → kod (success criteria, max 3 rounds verification)",
        "description": "Iteracyjna generacja kodu z weryfikacją kontraktu.",
        "inputs": [
            {"name": "spec", "type": "textarea", "label": "Specyfikacja", "required": True,
             "placeholder": "Funkcja parse_iso_date(s: str) -> datetime, raises ValueError dla bad input"},
            {"name": "language", "type": "input", "label": "Język", "required": False,
             "default": "python"},
            {"name": "must_have_csv", "type": "input", "label": "Must-have (CSV)", "required": False,
             "placeholder": "type hints, docstring, raises ValueError"},
        ],
        "estimated_seconds": 45,
    },
    {
        "id": "refactor_workflow",
        "name": "Refactor Workflow",
        "category": "refactor",
        "icon": "Wand2",
        "tagline": "Multi-step refactor z zachowaniem kontekstu między krokami",
        "description": "session() — agent pamięta co już zrobił. Idealne dla legacy.",
        "inputs": [
            {"name": "target_file", "type": "input", "label": "Plik docelowy", "required": True,
             "placeholder": "src/legacy/orders.py"},
            {"name": "refactor_goal", "type": "textarea", "label": "Cel refaktoryzacji", "required": True,
             "placeholder": "Wydziel klasę OrdersRepository, dodaj type hints, pokrycie testami 80%"},
        ],
        "estimated_seconds": 90,
    },
    {
        "id": "security_audit",
        "name": "Security Audit",
        "category": "security",
        "icon": "ShieldAlert",
        "tagline": "OWASP / sekrety / CVE — function calling",
        "description": "Wykrywa hardcoded credentials, SQL injection, niebezpieczne deserializacje.",
        "inputs": [
            {"name": "target", "type": "input", "label": "Ścieżka do skanu", "required": False,
             "default": ".", "placeholder": "src/"},
        ],
        "estimated_seconds": 60,
    },
]


# =============================================================================
# Index warm-up state (in-memory)
# =============================================================================
_INDEX_STATE: dict[str, Any] = {
    "status": "idle",          # idle | running | ready | failed
    "started_at": None,
    "finished_at": None,
    "duration_s": None,
    "workspace": None,
    "error": None,
    "exit_code": None,
}


def _set_index(**kwargs):
    _INDEX_STATE.update(kwargs)


# =============================================================================
# Models
# =============================================================================
class IndexStartRequest(BaseModel):
    workspace: Optional[str] = Field(None, description="Ścieżka do indeksowania (default: AUGGIE_WORKSPACE lub cwd)")
    additional: list[str] = Field(default_factory=list, description="--add-workspace (powtarzalne)")


class ToolRunRequest(BaseModel):
    tool_id: str
    inputs: dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# Routes — meta
# =============================================================================
@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}


@app.get("/api/health")
def api_health():
    """Pełny health snapshot (CLI, session, breaker)."""
    try:
        raw = auggie_tools.auggie_health()
        return json.loads(raw) if isinstance(raw, str) else raw
    except Exception as e:
        logger.exception("auggie_health failed")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/api/tools")
def list_tools():
    return {"tools": TOOL_CATALOG, "count": len(TOOL_CATALOG)}


@app.get("/api/telemetry")
def get_telemetry():
    raw = auggie_tools.auggie_telemetry()
    data = json.loads(raw) if isinstance(raw, str) else raw
    # Normalize shape so the frontend never sees missing keys
    summary = data.get("summary") or {}
    data["summary"] = {
        "total": summary.get("total", 0),
        "success": summary.get("success", 0),
        "failed": summary.get("failed", 0),
        "cached_hits": summary.get("cached_hits", 0),
        "avg_duration_s": summary.get("avg_duration_s", 0.0),
        "total_tool_calls": summary.get("total_tool_calls", 0),
        "total_func_calls": summary.get("total_func_calls", 0),
    }
    cache = data.get("cache") or {}
    data["cache"] = {
        "hits": cache.get("hits", 0),
        "misses": cache.get("misses", 0),
        "skipped_uncacheable": cache.get("skipped_uncacheable", 0),
        "hit_rate": cache.get("hit_rate", 0.0),
        "saved_seconds": cache.get("saved_seconds", 0.0),
        "evictions": cache.get("evictions", 0),
    }
    breaker = data.get("circuit_breaker") or {}
    data["circuit_breaker"] = {
        "state": breaker.get("state", "closed"),
        "consecutive_failures": breaker.get("consecutive_failures", 0),
        "opened_at": breaker.get("opened_at", 0.0),
    }
    data["last_calls"] = data.get("last_calls") or []
    return data


@app.get("/api/cost")
def get_cost():
    raw = auggie_tools.auggie_cost_report()
    data = json.loads(raw) if isinstance(raw, str) else raw
    return {
        "total_calls": data.get("total_calls", 0),
        "cached_calls": data.get("cached_calls", 0),
        "total_estimated_usd": data.get("total_estimated_usd", 0.0),
        "avg_per_call_usd": data.get("avg_per_call_usd", 0.0),
        "by_tool_usd": data.get("by_tool_usd", {}),
        "by_model_usd": data.get("by_model_usd", {}),
        "note": data.get("note", ""),
    }


@app.post("/api/cache/clear")
def clear_cache():
    CACHE.clear()
    return {"status": "ok", "message": "cache cleared"}


@app.get("/api/config")
def get_config():
    cfg = AuggieConfig.from_env()
    return {
        "model": cfg.model,
        "timeout": cfg.timeout,
        "max_turns": cfg.max_turns,
        "workspace": str(cfg.workspace),
        "cli_path": cfg.cli_path,
        "has_session_auth": cfg.has_session_auth,
        "use_cli_fallback": os.getenv("AUGGIE_USE_CLI", "").lower() in ("1", "true", "yes"),
        "platform": "windows" if os.name == "nt" else "posix",
        "index": _INDEX_STATE,
    }


@app.get("/api/workspace/suggestions")
def workspace_suggestions():
    """Sugestie ścieżek dla inputów typu path/focus_paths/target.

    Zwraca rozsądny zestaw kandydatów (repo root, moduły, cwd) — frontend
    wyświetla je jako klikalne presety, by użytkownik nie musiał zgadywać
    czy wpisywać ścieżkę względną czy absolutną.
    """
    cfg = AuggieConfig.from_env()
    workspace = cfg.workspace.resolve()
    # Heurystyka: repo root = pierwszy katalog w górę z pyproject/.git
    repo_root = workspace
    for parent in [workspace, *workspace.parents]:
        if (parent / "pyproject.toml").exists() or (parent / ".git").exists():
            repo_root = parent
            break

    suggestions: list[dict[str, str]] = []
    seen: set[str] = set()

    def _add(label: str, path: Path, hint: str = "") -> None:
        try:
            resolved = str(path.resolve())
        except OSError:
            return
        if resolved in seen or not path.exists():
            return
        seen.add(resolved)
        suggestions.append({"label": label, "path": resolved, "hint": hint})

    _add("Workspace (Auggie)", workspace, "AUGGIE_WORKSPACE - default for all tools")
    _add("Repo root", repo_root, "Whole project; careful - large index, long time")
    _add("module_23 - Concierge", repo_root / "adk_training" / "module_23_auggie_integration", "This module")
    _add("module_24 - AuditOps", repo_root / "adk_training" / "module_24_audit_ops")
    _add("Current directory", Path.cwd(), "Where backend was started")
    return {
        "workspace_default": str(workspace),
        "repo_root": str(repo_root),
        "suggestions": suggestions,
    }


# =============================================================================
# Index warm-up (SSE)
# =============================================================================
@app.get("/api/index/status")
def index_status():
    return _INDEX_STATE


@app.post("/api/index/start")
async def index_start(req: IndexStartRequest):
    """SSE: uruchamia warm-up indexu Augment dla workspace.

    Komenda: `auggie --print "ping" --quiet --wait-for-indexing --workspace-root <path> [--add-workspace <path>...]`

    Indeksowanie jest inkrementalne i transparentne — flagą `--wait-for-indexing` blokujemy do końca,
    żeby pierwsze produkcyjne wywołanie tool'a miało już gotowy semantic index.
    """
    cfg = AuggieConfig.from_env()
    workspace = req.workspace or str(cfg.workspace)
    cli_path = cfg.cli_path or "auggie"

    cmd = [
        cli_path, "--print", "Reply with single word: ready",
        "--quiet", "--model", cfg.model,
        "--wait-for-indexing", "--allow-indexing",
        "--workspace-root", workspace,
    ]
    for extra in req.additional:
        cmd += ["--add-workspace", extra]

    async def stream() -> AsyncIterator[bytes]:
        def _ev(typ: str, **kw) -> bytes:
            return f"data: {json.dumps({'type': typ, 'ts': time.time(), **kw}, ensure_ascii=False)}\n\n".encode("utf-8")

        yield _ev("start", workspace=workspace, command=" ".join(cmd[:6] + ["..."]))
        _set_index(status="running", started_at=time.time(), finished_at=None,
                   duration_s=None, workspace=workspace, error=None, exit_code=None)

        # Heartbeat task — emituje "tick" co 2s żeby UI nie zamarzło
        proc: subprocess.Popen | None = None
        start_t = time.perf_counter()

        def _spawn():
            return subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, encoding="utf-8", errors="replace",
            )

        try:
            proc = await asyncio.get_running_loop().run_in_executor(None, _spawn)
        except FileNotFoundError as e:
            err = f"Auggie CLI not found ({cli_path}). Install: npm i -g @augmentcode/auggie"
            _set_index(status="failed", finished_at=time.time(), error=err, exit_code=-1,
                       duration_s=time.perf_counter() - start_t)
            yield _ev("error", message=err, hint="Sprawdź AUGGIE_CLI_PATH lub instalację npm")
            yield _ev("end")
            return

        # Pętla: poll proc + heartbeat
        last_tick = 0.0
        while proc.poll() is None:
            await asyncio.sleep(0.5)
            now = time.perf_counter() - start_t
            if now - last_tick >= 2.0:
                yield _ev("tick", elapsed_s=round(now, 1),
                          message=f"Indeksowanie workspace... {now:.1f}s")
                last_tick = now

        stdout, stderr = proc.communicate()
        duration = time.perf_counter() - start_t
        rc = proc.returncode

        if rc == 0:
            _set_index(status="ready", finished_at=time.time(), duration_s=duration,
                       error=None, exit_code=0)
            yield _ev("ok", duration_s=round(duration, 2),
                      response=(stdout or "").strip()[:200],
                      message=f"Index gotowy w {duration:.1f}s")
        else:
            err = (stderr or stdout or "unknown error").strip()[:500]
            _set_index(status="failed", finished_at=time.time(), duration_s=duration,
                       error=err, exit_code=rc)
            yield _ev("error", exit_code=rc, message=err, duration_s=round(duration, 2))

        yield _ev("end", status=_INDEX_STATE["status"])

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no", "Connection": "keep-alive"},
    )


# =============================================================================
# Tool execution (SSE)
# =============================================================================
def _resolve_tool(tool_id: str):
    fn = getattr(auggie_tools, tool_id, None)
    if not callable(fn) or tool_id.startswith("_"):
        raise HTTPException(status_code=404, detail=f"Unknown tool: {tool_id}")
    if tool_id not in {t["id"] for t in TOOL_CATALOG}:
        raise HTTPException(status_code=403, detail=f"Tool not exposed: {tool_id}")
    return fn


def _coerce_inputs(meta: dict, inputs: dict) -> dict:
    """Wymuś typy z metadanych (number → int)."""
    out: dict[str, Any] = {}
    for spec in meta["inputs"]:
        name = spec["name"]
        if name not in inputs:
            if spec.get("default") is not None:
                inputs[name] = spec["default"]
            elif not spec.get("required"):
                continue
            else:
                raise HTTPException(status_code=400, detail=f"Missing input: {name}")
        val = inputs[name]
        if spec.get("input_type") == "number":
            try:
                val = int(val)
            except (TypeError, ValueError):
                raise HTTPException(status_code=400, detail=f"{name} must be int")
        out[name] = val
    return out


@app.post("/api/tools/run")
async def run_tool(req: ToolRunRequest, request: Request):
    """SSE: uruchamia tool w wątku, emituje progress, logi z CLI, log-evnts.

    Cancel-on-disconnect: gdy klient zamknie EventSource, zabijamy podprocess
    Auggie i zapisujemy run jako ``cancelled``.
    """
    meta = next((t for t in TOOL_CATALOG if t["id"] == req.tool_id), None)
    if not meta:
        raise HTTPException(status_code=404, detail=f"Unknown tool: {req.tool_id}")
    fn = _resolve_tool(req.tool_id)
    coerced = _coerce_inputs(meta, dict(req.inputs))

    # Walidacja niebezpiecznych domyślnych wartości — security_audit z target='.'
    # Skanowanie całego workspace (z .venv, node_modules, artifacts) zawsze
    # przekracza AUGGIE_TIMEOUT i nigdy nie zwraca użytecznego wyniku.
    if req.tool_id == "security_audit":
        target = str(coerced.get("target") or "").strip()
        if target in {"", ".", "./", "/"} or target.endswith((":\\", ":/")):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Podaj konkretną ścieżkę do skanu — np. 'adk_training/module_23_auggie_integration/tools.py' "
                    "albo 'src/'. Skanowanie całego workspace ('.') trwa minutami i przekracza timeout."
                ),
            )

    run_id = runs_store.new_run_id()
    record = runs_store.make_pending(run_id, meta["id"], meta["name"], coerced)

    if _INDEX_STATE["status"] not in ("ready", "idle"):
        index_warning = f"Index status: {_INDEX_STATE['status']}. Wynik może być niepełny."
    else:
        index_warning = None

    log_q: "queue.Queue[tuple[str, dict[str, Any]]]" = queue.Queue()
    worker_tid: dict[str, Optional[int]] = {"tid": None}
    worker_done = threading.Event()
    result_holder: dict[str, Any] = {}

    def _worker() -> None:
        tid = threading.get_ident()
        worker_tid["tid"] = tid

        def _cb(level: str, message: str) -> None:
            log_q.put(("log", {"level": level, "message": message}))

        register_log_cb(tid, _cb)
        try:
            result_holder["result"] = fn(**coerced)
        except Exception as e:  # noqa: BLE001
            result_holder["error"] = e
        finally:
            unregister_log_cb(tid)
            worker_done.set()

    async def stream() -> AsyncIterator[bytes]:
        events_log: list[dict[str, Any]] = []
        logs_log: list[dict[str, Any]] = []

        def _ev(typ: str, **kw) -> bytes:
            payload = {"type": typ, "ts": time.time(), **kw}
            events_log.append(payload)
            return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n".encode("utf-8")

        yield _ev("start", tool=req.tool_id, run_id=run_id, eta_s=meta["estimated_seconds"])
        if index_warning:
            yield _ev("warning", message=index_warning)

        thread = threading.Thread(
            target=_worker, daemon=True, name=f"tool-{req.tool_id}-{run_id}",
        )
        thread.start()

        start = time.perf_counter()
        last_tick = 0.0
        cancelled = False

        while not worker_done.is_set():
            # 1. Drain log queue
            drained = 0
            while drained < 50:
                try:
                    evt_type, payload = log_q.get_nowait()
                except queue.Empty:
                    break
                logs_log.append({"ts": time.time(), **payload})
                yield _ev(evt_type, **payload)
                drained += 1

            # 2. Disconnect → kill subprocess
            try:
                disconnected = await request.is_disconnected()
            except Exception:  # noqa: BLE001
                disconnected = False
            if disconnected:
                cancelled = True
                tid = worker_tid.get("tid")
                if tid is not None:
                    killed = kill_thread_subprocess(tid)
                    logger.info("client disconnect — killed subprocess: %s (run=%s)", killed, run_id)
                break

            # 3. Tick
            now = time.perf_counter() - start
            if now - last_tick >= 2.0:
                yield _ev("tick", elapsed_s=round(now, 1),
                          eta_s=meta["estimated_seconds"],
                          progress=min(0.95, now / max(meta["estimated_seconds"], 1)))
                last_tick = now

            await asyncio.sleep(0.5)

        # Final log drain
        while True:
            try:
                evt_type, payload = log_q.get_nowait()
            except queue.Empty:
                break
            logs_log.append({"ts": time.time(), **payload})
            yield _ev(evt_type, **payload)

        duration = time.perf_counter() - start
        record["duration_s"] = round(duration, 2)
        record["logs"] = logs_log

        if cancelled:
            record["status"] = "cancelled"
            record["error"] = {"message": "Anulowano przez użytkownika.", "exception": "Cancelled"}
            yield _ev("error", duration_s=record["duration_s"],
                      message="Anulowano przez użytkownika.", exception="Cancelled")
            yield _ev("end", success=False, run_id=run_id)
        elif "error" in result_holder:
            err = result_holder["error"]
            record["status"] = "error"
            record["error"] = {"message": str(err)[:2000], "exception": type(err).__name__}
            logger.exception("tool %s failed (run=%s)", req.tool_id, run_id)
            yield _ev("error", duration_s=record["duration_s"], message=str(err),
                      exception=type(err).__name__)
            yield _ev("end", success=False, run_id=run_id)
        else:
            r = result_holder.get("result")
            cached = duration < 0.5
            record["status"] = "ok"
            record["cached"] = cached
            record["output"] = str(r) if r is not None else ""
            yield _ev("result", duration_s=record["duration_s"], cached=cached,
                      output=record["output"], output_kind="text")
            yield _ev("end", success=True, run_id=run_id)

        record["finished_at"] = time.time()
        record["events"] = events_log
        try:
            runs_store.save_run(record)
        except Exception:  # noqa: BLE001
            logger.exception("failed to persist run %s", run_id)

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no", "Connection": "keep-alive"},
    )


# =============================================================================
# Run history (concierge_runs/*.json)
# =============================================================================
@app.get("/api/runs")
def api_list_runs(limit: int = 50, tool_id: Optional[str] = None):
    """List recent tool runs (newest first). Used by the History page."""
    rows = runs_store.list_runs(limit=max(1, min(int(limit), 200)), tool_id=tool_id)
    return {"runs": rows, "count": len(rows)}


@app.get("/api/runs/{run_id}")
def api_get_run(run_id: str):
    """Full record for a single run, including logs and events."""
    rec = runs_store.get_run(run_id)
    if rec is None:
        raise HTTPException(status_code=404, detail=f"Unknown run: {run_id}")
    return rec


# =============================================================================
# Static frontend (production build) — opcjonalnie
# =============================================================================
_FRONTEND_DIST = Path(__file__).parent / "frontend" / "dist"
if _FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=_FRONTEND_DIST / "assets"), name="assets")

    @app.get("/", response_class=HTMLResponse)
    def serve_index():
        return (_FRONTEND_DIST / "index.html").read_text(encoding="utf-8")
else:
    @app.get("/", response_class=HTMLResponse)
    def fallback_index():
        return """<!doctype html><html><head><title>Auggie Concierge — Backend</title>
<style>body{font-family:system-ui;background:#020617;color:#e2e8f0;padding:3em;max-width:780px;margin:auto}
h1{background:linear-gradient(120deg,#3b82f6,#22d3ee);-webkit-background-clip:text;color:transparent;font-size:2.5em;margin:0}
code{background:#0f172a;padding:.2em .5em;border-radius:.3em;color:#60a5fa}
.box{border:1px solid #1e293b;border-radius:.75em;padding:1.5em;margin:1em 0;background:#0b1224}
a{color:#60a5fa}</style></head><body>
<h1>⚡ Auggie Concierge</h1>
<p>Backend działa. Frontend nie jest jeszcze zbudowany.</p>
<div class="box"><b>Dev:</b><br><code>cd web/frontend && npm install && npm run dev</code><br>
→ <a href="http://localhost:5173">http://localhost:5173</a> (Vite proxy do tego API)</div>
<div class="box"><b>Prod:</b><br><code>cd web/frontend && npm run build</code> — odśwież tę stronę.</div>
<div class="box"><b>API:</b> <a href="/docs">/docs</a> (Swagger), <a href="/api/health">/api/health</a>,
<a href="/api/tools">/api/tools</a>, <a href="/api/telemetry">/api/telemetry</a>, <a href="/api/cost">/api/cost</a></div>
</body></html>"""


def main():
    import uvicorn
    port = int(os.environ.get("CONCIERGE_PORT", "8770"))
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")


if __name__ == "__main__":
    main()

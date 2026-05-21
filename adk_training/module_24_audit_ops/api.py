"""FastAPI router for AuditOps — mounted by module_23 web/app.py."""
from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from pathlib import Path
from typing import Any, AsyncIterator, Dict, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

from .ack_store import AckStore
from .auth import AuthContext, AuthStore, make_auth
from .compare import diff_runs, load_run, render_diff_markdown
from .config import AuditConfig
from .pentest_agent import auto_pentest, guided_pentest
from .playwright_runner import available as playwright_available
from .reporter import write_report
from .safety import DisclaimerAck, SafetyError
from .skills_loader import default_registry
from . import wiki as wiki_mod

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/api/audit", tags=["audit"])
_CFG = AuditConfig.from_env()

# Persistent ack store (SQLite under artifacts_dir/acks.db)
_ACKS = AckStore(_CFG.artifacts_dir / "acks.db")
# In-memory auth vault — secrets never persisted to disk.
_AUTH = AuthStore()
# In-memory completed audits, keyed by run_id
_RUNS: Dict[str, Dict[str, Any]] = {}


# ----------------------------- models ----------------------------------------


class AckRequest(BaseModel):
    target_url: str
    user_id: str = "anonymous"
    accepted: bool = True


class AckResponse(BaseModel):
    token: str
    statement: str


class StartRequest(BaseModel):
    url: str
    mode: str = Field("auto", pattern="^(auto|guided)$")
    scenario_nl: Optional[str] = None
    ack_token: Optional[str] = None
    auth_id: Optional[str] = None


class AuthRegisterRequest(BaseModel):
    label: str = ""
    cookies: list = Field(default_factory=list)
    headers: Dict[str, str] = Field(default_factory=dict)
    basic_auth_user: Optional[str] = None
    basic_auth_pass: Optional[str] = None


# ----------------------------- helpers ---------------------------------------


def _get_ack(token: Optional[str]) -> Optional[DisclaimerAck]:
    if not token:
        return None
    return _ACKS.get(token)


def _sse(event_obj: Dict[str, Any]) -> str:
    payload = json.dumps(event_obj, default=str)
    return f"data: {payload}\n\n"


# ----------------------------- endpoints -------------------------------------


@router.get("/config")
async def get_config():
    avail = playwright_available()
    return {
        "allowed_domains": _CFG.allowed_domains,
        "require_disclaimer": _CFG.require_disclaimer,
        "rate_limit_rps": _CFG.rate_limit_rps,
        "headless": _CFG.headless,
        "record_video": _CFG.record_video,
        "max_scenarios": _CFG.max_scenarios,
        "max_steps_per_scenario": _CFG.max_steps_per_scenario,
        "total_budget_seconds": _CFG.total_budget_seconds,
        "playwright": avail,
        "llm_model": _CFG.llm_model,
    }


@router.post("/disclaimer/ack", response_model=AckResponse)
async def post_disclaimer(req: AckRequest):
    if not req.accepted:
        raise HTTPException(400, "Disclaimer must be explicitly accepted.")
    ack = DisclaimerAck(
        acknowledged=True,
        user_id=req.user_id,
        target_url=req.target_url,
        timestamp=time.time(),
    )
    token = _ACKS.register(ack)
    return AckResponse(token=token, statement=ack.statement)


@router.post("/start")
async def start_audit(req: StartRequest):
    """SSE-streamed audit run. Returns text/event-stream."""
    ack = _get_ack(req.ack_token)
    # Bind ack to target host: an ack issued for one host MUST NOT authorize another.
    if ack is not None and ack.target_url:
        from urllib.parse import urlparse
        ack_host = (urlparse(ack.target_url).hostname or "").lower()
        req_host = (urlparse(req.url).hostname or "").lower()
        if ack_host and req_host and ack_host != req_host:
            raise HTTPException(
                400,
                f"Disclaimer ack was issued for host {ack_host!r}, but request targets {req_host!r}. "
                "Re-acknowledge for the new target.",
            )
    queue: asyncio.Queue = asyncio.Queue()
    final_holder: Dict[str, Any] = {}
    auth_ctx = _AUTH.get(req.auth_id)
    if req.auth_id and auth_ctx is None:
        raise HTTPException(404, f"Unknown auth_id {req.auth_id!r}")

    async def on_event(ev: Dict[str, Any]) -> None:
        await queue.put(ev)

    async def runner():
        try:
            if req.mode == "guided":
                if not req.scenario_nl:
                    raise SafetyError("Mode 'guided' requires scenario_nl.")
                audit = await guided_pentest(req.url, req.scenario_nl, _CFG, ack,
                                             on_event=on_event, auth=auth_ctx)
            else:
                audit = await auto_pentest(req.url, _CFG, ack,
                                           on_event=on_event, auth=auth_ctx)
            audit_dict = audit.to_dict()
            paths = write_report(audit_dict, _CFG)
            audit_dict["report"] = paths
            _RUNS[audit.run_id] = audit_dict
            # V2: update the per-target wiki — best-effort, never blocks the run.
            try:
                wiki_mod.record_run(_CFG.artifacts_dir, audit_dict)
            except Exception:
                logger.exception("wiki.record_run failed (non-fatal)")
            await queue.put({"type": "report_ready", "run_id": audit.run_id, **paths})
            final_holder["audit"] = audit_dict
        except SafetyError as se:
            await queue.put({"type": "safety_error", "message": str(se)})
        except Exception as e:
            logger.exception("audit run crashed")
            await queue.put({"type": "error", "message": str(e)})
        finally:
            await queue.put({"type": "__done__"})

    async def stream() -> AsyncIterator[str]:
        task = asyncio.create_task(runner())
        try:
            while True:
                ev = await queue.get()
                if ev.get("type") == "__done__":
                    break
                yield _sse(ev)
        finally:
            if not task.done():
                task.cancel()

    return StreamingResponse(stream(), media_type="text/event-stream", headers={
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
    })


@router.get("/runs/{run_id}")
async def get_run(run_id: str):
    audit = _RUNS.get(run_id)
    if not audit:
        # try from disk
        report_json = _CFG.artifacts_dir / run_id / "report.json"
        if report_json.exists():
            return json.loads(report_json.read_text(encoding="utf-8"))
        raise HTTPException(404, f"Run {run_id} not found")
    return audit


@router.get("/runs")
async def list_runs(limit: int = Query(50, ge=1, le=200)):
    runs = []
    if _CFG.artifacts_dir.exists():
        for d in sorted(_CFG.artifacts_dir.iterdir(), reverse=True)[:limit]:
            if not d.is_dir():
                continue
            j = d / "report.json"
            if not j.exists():
                continue
            try:
                a = json.loads(j.read_text(encoding="utf-8"))
                runs.append({
                    "run_id": a.get("run_id"),
                    "target_url": a.get("target_url"),
                    "duration_s": a.get("duration_s"),
                    "findings": len(a.get("findings", [])),
                    "started_at": a.get("started_at"),
                })
            except Exception:
                continue
    return {"runs": runs}


@router.get("/artifact/{run_id}/{path:path}")
async def get_artifact(run_id: str, path: str):
    base = (_CFG.artifacts_dir / run_id).resolve()
    target = (base / path).resolve()
    if not str(target).startswith(str(base)):
        raise HTTPException(400, "Path traversal blocked.")
    if not target.exists() or not target.is_file():
        raise HTTPException(404, "Artifact not found.")
    return FileResponse(target)


def get_artifacts_root() -> Path:
    """Used by app.py to mount /artifacts as static."""
    return _CFG.artifacts_dir


# ----------------------------- auth vault -----------------------------------


@router.post("/auth")
async def register_auth(req: AuthRegisterRequest):
    """Register an auth context. Returns an opaque id; secrets stay server-side."""
    basic = None
    if req.basic_auth_user and req.basic_auth_pass:
        basic = (req.basic_auth_user, req.basic_auth_pass)
    try:
        ctx = make_auth(label=req.label, cookies=req.cookies, headers=req.headers,
                        basic_auth=basic)
    except ValueError as e:
        raise HTTPException(400, str(e))
    _AUTH.add(ctx)
    return {"id": ctx.id, "label": ctx.label, **ctx.fingerprint()}


@router.get("/auth")
async def list_auth():
    return {"auth": _AUTH.list()}


@router.delete("/auth/{auth_id}")
async def delete_auth(auth_id: str):
    if not _AUTH.remove(auth_id):
        raise HTTPException(404, f"Unknown auth_id {auth_id!r}")
    return {"ok": True}


# ----------------------------- compare / diff -------------------------------


def _load_run_any(run_id: str) -> Dict[str, Any]:
    if run_id in _RUNS:
        return _RUNS[run_id]
    return load_run(_CFG.artifacts_dir, run_id)


@router.get("/compare")
async def compare_runs(a: str = Query(..., description="baseline run_id"),
                       b: str = Query(..., description="current run_id"),
                       fmt: str = Query("json", pattern="^(json|markdown)$")):
    try:
        baseline = _load_run_any(a)
        current = _load_run_any(b)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))
    diff = diff_runs(baseline, current)
    if fmt == "markdown":
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(render_diff_markdown(diff), media_type="text/markdown")
    return diff


# ----------------------------- JUnit ---------------------------------------


@router.get("/runs/{run_id}/junit")
async def junit_for_run(run_id: str, fail_on: str = Query("high", pattern="^(info|low|medium|high|critical)$")):
    try:
        audit = _load_run_any(run_id)
    except FileNotFoundError:
        raise HTTPException(404, f"Run {run_id} not found")
    # Local import to avoid pulling argparse at module load
    from .cli import _to_junit

    class _A:
        pass
    a = _A()
    a.scenarios = audit.get("scenarios", [])
    a.findings = audit.get("findings", [])
    a.duration_s = audit.get("duration_s", 0.0)
    from fastapi.responses import Response
    return Response(content=_to_junit(a, fail_on), media_type="application/xml")


# ----------------------------- skills (V1) ----------------------------------


@router.get("/skills")
async def list_skills():
    """L1 manifest of all bundled OWASP skills (always cheap)."""
    reg = default_registry()
    return {"skills": [{**s.manifest(), "triggers": s.triggers,
                         "resources": s.list_resources()} for s in reg.list()]}


@router.get("/skills/{name}")
async def get_skill(name: str):
    """L2 — full instructions body for a single skill."""
    try:
        sk = default_registry().get(name)
    except KeyError:
        raise HTTPException(404, f"unknown skill {name!r}")
    return {
        "name": sk.name,
        "description": sk.description,
        "triggers": sk.triggers,
        "instructions": sk.instructions,
        "resources": sk.list_resources(),
    }


@router.get("/skills/{name}/resource")
async def get_skill_resource(name: str, path: str = Query(..., description="relative path under references/")):
    """L3 — fetch a reference file."""
    try:
        sk = default_registry().get(name)
    except KeyError:
        raise HTTPException(404, f"unknown skill {name!r}")
    try:
        return {"name": name, "path": path, "content": sk.load_resource(path)}
    except (FileNotFoundError, ValueError) as e:
        raise HTTPException(404, str(e))


# ----------------------------- wiki (V2 / V3 / V4) --------------------------


@router.get("/wiki")
async def list_wiki_targets():
    base = _CFG.artifacts_dir / "wiki"
    if not base.is_dir():
        return {"targets": []}
    targets = []
    for child in sorted(base.iterdir()):
        if not child.is_dir():
            continue
        runs = list((child / "runs").glob("*.md")) if (child / "runs").is_dir() else []
        findings = list((child / "findings").glob("F-*.md")) if (child / "findings").is_dir() else []
        targets.append({"slug": child.name, "runs": len(runs), "findings": len(findings)})
    return {"targets": targets}


@router.get("/wiki/{slug}/index")
async def wiki_index(slug: str):
    base = _CFG.artifacts_dir / "wiki" / slug / "index.md"
    if not base.is_file():
        raise HTTPException(404, f"no wiki for {slug!r}")
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(base.read_text(encoding="utf-8"), media_type="text/markdown")


@router.get("/wiki/{slug}/file")
async def wiki_file(slug: str, path: str = Query(..., description="relative path inside the wiki")):
    base = (_CFG.artifacts_dir / "wiki" / slug).resolve()
    target = (base / path).resolve()
    if not str(target).startswith(str(base)):
        raise HTTPException(400, "path traversal blocked")
    if not target.is_file():
        raise HTTPException(404, "not found")
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(target.read_text(encoding="utf-8"), media_type="text/markdown")


@router.get("/wiki/{slug}/lint")
async def wiki_lint(slug: str):
    base = _CFG.artifacts_dir / "wiki" / slug
    if not base.is_dir():
        raise HTTPException(404, f"no wiki for {slug!r}")
    issues = wiki_mod.lint_wiki(_CFG.artifacts_dir, f"https://{slug}/")
    return {"slug": slug, "issues": [i.to_dict() for i in issues]}


class SynthesizeRequest(BaseModel):
    slug: str
    question: str = "Summarize regressions and recurring findings."
    accept: bool = False  # HITL gate — must be true to persist


@router.post("/wiki/synthesize")
async def wiki_synthesize(req: SynthesizeRequest):
    """LLM-authored synthesis page. Persisted only when ``accept=true``.

    The LLM is given index.md + the most recent N finding pages as context,
    never raw report bodies. Output goes to ``synthesis/<timestamp>.md``.
    """
    base = _CFG.artifacts_dir / "wiki" / req.slug
    if not base.is_dir():
        raise HTTPException(404, f"no wiki for {req.slug!r}")
    index_text = (base / "index.md").read_text(encoding="utf-8") if (base / "index.md").is_file() else ""
    findings_dir = base / "findings"
    finding_blobs = []
    if findings_dir.is_dir():
        for fp in sorted(findings_dir.glob("F-*.md"))[:20]:
            finding_blobs.append(f"--- {fp.name} ---\n" + fp.read_text(encoding="utf-8"))

    prompt = (
        "You are a senior security analyst. Using ONLY the wiki context below, "
        "answer the question. Cite finding pages by file name. Do not invent "
        "facts. If the wiki has too few runs to answer, say so explicitly.\n\n"
        f"QUESTION: {req.question}\n\n"
        f"=== index.md ===\n{index_text}\n\n"
        + "\n\n".join(finding_blobs)
    )
    try:
        try:
            from auggie_factory import auggie_run  # standalone repo layout
        except ModuleNotFoundError:
            from adk_training.module_23_auggie_integration.auggie_factory import auggie_run  # adk-fundamentals layout
        answer = auggie_run(tool_name="auditops_wiki_synthesize", prompt=prompt, return_type=str)
    except Exception as e:
        raise HTTPException(500, f"auggie failed: {e}")

    if not req.accept:
        return {"accepted": False, "preview": answer,
                "note": "Set accept=true to persist this synthesis page."}

    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    syn_path = base / "synthesis" / f"{ts}.md"
    syn_path.parent.mkdir(parents=True, exist_ok=True)
    body = (
        f"# Synthesis — {req.question}\n\n"
        f"_Generated {ts} · question: `{req.question}`_\n\n"
        f"{answer}\n"
    )
    syn_path.write_text(body, encoding="utf-8")
    # rebuild index so the new synthesis page is listed
    wiki_mod._write(base / "index.md", wiki_mod._rebuild_index(
        wiki_mod.wiki_paths(_CFG.artifacts_dir, f"https://{req.slug}/"),
        f"https://{req.slug}/",
    ))
    return {"accepted": True, "path": str(syn_path), "url": f"/api/audit/wiki/{req.slug}/file?path=synthesis/{ts}.md"}

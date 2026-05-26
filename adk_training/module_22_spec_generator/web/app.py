"""Web UI dla Spec Generator - MVP (HITL).

Endpointy:
  GET  /                 - formularz: issue_key + opcje
  POST /api/generate     - uruchamia pipeline (ticket -> HLD -> Epiki), zwraca preview JSON
  POST /api/publish/{id} - publikuje zaakceptowane epiki do Jira (wymaga approved=True)
  GET  /health

Pipeline:
  - SPEC_GEN_USE_REAL_PIPELINE=1 + GOOGLE_CLOUD_PROJECT ustawione  -> realne Gemini
  - inaczej -> tryb SCAFFOLD (placeholder) - bezpieczny default dla dev/CI
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time
import uuid
from pathlib import Path
from typing import AsyncIterator, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

# Upewniamy sie ze module_22 root jest na sys.path (dla `agents.*` i `config`)
_MOD_ROOT = Path(__file__).resolve().parent.parent
if str(_MOD_ROOT) not in sys.path:
    sys.path.insert(0, str(_MOD_ROOT))

# adk_training root na sys.path (zeby `from notebooklm_agent...` dzialalo)
_ADK_TRAINING_ROOT = _MOD_ROOT.parent
if str(_ADK_TRAINING_ROOT) not in sys.path:
    sys.path.insert(0, str(_ADK_TRAINING_ROOT))

# Zaladuj .env z adk_training/ (klucze MCP Comarch + NotebookLM)
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv(_ADK_TRAINING_ROOT / ".env", override=False)
    # Sklejamy z .env modulu notebooklm_agent (USE_COOKIE_AUTH, COOKIES_PATH,
    # PLAYWRIGHT_BROWSER_CHANNEL itp.). override=False -> adk_training/.env wygrywa.
    load_dotenv(_ADK_TRAINING_ROOT / "notebooklm_agent" / ".env", override=False)
except ImportError:  # pragma: no cover
    pass


# Konfiguracja logowania: nasze loggery (spec_generator.*, notebooklm_agent.*) na INFO,
# zeby uvicorn pokazywal RAW ANSWER, QUESTION itp. (uvicorn ustawia tylko `uvicorn.*`).
_log_level = os.environ.get("SPEC_GEN_LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=_log_level,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    force=True,
)
for _name in ("spec_generator", "notebooklm_agent", "tools"):
    logging.getLogger(_name).setLevel(_log_level)

logger = logging.getLogger("spec_generator.web")


app = FastAPI(title="Spec Generator", version="0.2.0-mvp")

# CORS dla frontendu Vite (dev: 5173). W produkcji frontend jest serwowany z tego samego origin.
_cors_origins = os.environ.get(
    "SPEC_GEN_CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
).split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _cors_origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache sesji: session_id -> {"hld": str, "epics": list, "approved": bool, "mode": "real"|"scaffold"}
_SESSIONS: dict[str, dict] = {}


class GenerateRequest(BaseModel):
    issue_key: str = Field(..., description="Jira issue key, np. SWOK-1234")
    enable_notebooklm: bool = False
    max_critique_iterations: int = Field(3, ge=1, le=5)
    notebook_url: Optional[str] = Field(None, description="NotebookLM URL lub ID (override)")


class GenerateResponse(BaseModel):
    session_id: str
    hld_markdown: str
    epics: list[dict]
    status: str


class PublishRequest(BaseModel):
    session_id: str
    approved: bool = True
    edited_epics: Optional[list[dict]] = None


INDEX_HTML = """<!DOCTYPE html>
<html lang="pl">
<head>
  <meta charset="utf-8"/>
  <title>Spec Generator</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 900px; margin: 2em auto; padding: 0 1em; }
    h1 { color: #1a365d; }
    .warn { background: #fff3cd; border-left: 4px solid #f0ad4e; padding: 1em; margin: 1em 0; }
    .ok   { background: #d1fae5; border-left: 4px solid #10b981; padding: 1em; margin: 1em 0; }
    pre { background: #f7fafc; padding: 1em; overflow-x: auto; }
    button { padding: 0.5em 1em; }
  </style>
</head>
<body>
  <h1>Spec Generator — MVP</h1>
  <div class="warn">
    <b>Tryb:</b> ustaw <code>SPEC_GEN_USE_REAL_PIPELINE=1</code> + <code>GOOGLE_CLOUD_PROJECT</code>
    aby uruchomic realne Gemini. Bez tego dziala tryb <b>scaffold</b> (placeholder).
    MCP Jira: ticket jest fetchowany tylko jesli ustawisz <code>COMARCH_MCP_URL</code> (Sprint 2).
  </div>
  <h2>Generuj HLD + Epiki z ticketu</h2>
  <form id="f">
    <label>Issue key: <input name="issue_key" placeholder="SWOK-1234" required/></label><br/>
    <label><input type="checkbox" name="enable_notebooklm"/> Uzyj NotebookLM (opcjonalnie)</label><br/>
    <label>Notebook URL/ID: <input name="notebook_url" placeholder="ec182696-22e7-4c58-9f85-6f7acc06cf8d" style="width:400px"/></label><br/>
    <label>Max iteracje krytyki: <input type="number" name="max_iter" value="3" min="1" max="5"/></label><br/>
    <button type="submit">Generuj</button>
  </form>
  <hr/>
  <div id="out"></div>
  <script>
    document.getElementById('f').addEventListener('submit', async (e) => {
      e.preventDefault();
      const fd = new FormData(e.target);
      const body = {
        issue_key: fd.get('issue_key'),
        enable_notebooklm: fd.get('enable_notebooklm') === 'on',
        max_critique_iterations: parseInt(fd.get('max_iter'), 10),
        notebook_url: fd.get('notebook_url') || null,
      };
      document.getElementById('out').innerText = 'Generuje...';
      const r = await fetch('/api/generate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(body),
      });
      const data = await r.json();
      document.getElementById('out').innerHTML =
        '<h3>Status: ' + data.status + ' (session: ' + data.session_id + ')</h3>' +
        '<h3>HLD</h3><pre>' + (data.hld_markdown || '').replace(/</g,'&lt;') + '</pre>' +
        '<h3>Epiki</h3><pre>' + JSON.stringify(data.epics, null, 2) + '</pre>';
    });
  </script>
</body>
</html>
"""


def _should_use_real_pipeline() -> bool:
    return (
        os.getenv("SPEC_GEN_USE_REAL_PIPELINE", "0") == "1"
        and bool(os.getenv("GOOGLE_CLOUD_PROJECT"))
    )


async def _run_real_pipeline(req: GenerateRequest) -> tuple[str, list[dict]]:
    """Uruchom realny SequentialAgent spec_generatora przez Runner (non-streaming wrapper).

    Zwraca (hld_markdown, epics_list). W razie bledow parsowania epik - zwraca [].
    """
    final_hld = ""
    final_epics: list[dict] = []
    async for ev in _run_real_pipeline_streaming(req):
        if ev.get("type") == "done":
            final_hld = ev.get("hld_markdown", "")
            final_epics = ev.get("epics", [])
    return final_hld, final_epics


async def _run_real_pipeline_streaming(req: GenerateRequest) -> AsyncIterator[dict]:
    """Streamujaca wersja pipeline'u - emituje eventy ze stage'ami i finalny snapshot.

    Eventy:
      {"type": "stage_start", "stage": "<author>", "ts": float}
      {"type": "stage_event", "stage": "<author>", "preview": "<text fragment>", "ts": float}
      {"type": "stage_end",   "stage": "<author>", "ts": float}
      {"type": "done", "hld_markdown": str, "epics": list, "iterations": int}
    """
    from google.adk.runners import Runner  # type: ignore
    from google.adk.sessions import InMemorySessionService  # type: ignore
    from google.genai import types as genai_types  # type: ignore

    from agents.spec_generator import build_spec_generator, parse_epics_json  # noqa: E402
    from tools.comarch_mcp import get_jira_tools  # noqa: E402

    # Dynamic notebook URL override
    if req.notebook_url and req.enable_notebooklm:
        from tools.notebooklm_tool import set_notebook_url
        nb_url = req.notebook_url
        if not nb_url.startswith("http"):
            nb_url = f"https://notebooklm.google.com/notebook/{nb_url}"
        set_notebook_url(nb_url)

    jira_tools = get_jira_tools()
    agent = build_spec_generator(
        jira_tools=jira_tools,
        enable_notebooklm=req.enable_notebooklm,
        max_critique_iterations=req.max_critique_iterations,
    )
    runner = Runner(
        agent=agent,
        app_name="spec_generator_web",
        session_service=InMemorySessionService(),
    )
    session = await runner.session_service.create_session(
        app_name="spec_generator_web", user_id="web",
    )
    content = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=req.issue_key)],
    )

    current_stage: str | None = None
    iterations = 0

    async for ev in runner.run_async(
        user_id="web", session_id=session.id, new_message=content,
    ):
        author = getattr(ev, "author", None) or "agent"
        if author != current_stage:
            if current_stage is not None:
                yield {"type": "stage_end", "stage": current_stage, "ts": time.time()}
            current_stage = author
            if author == "hld_critic":
                iterations += 1
            yield {"type": "stage_start", "stage": current_stage, "ts": time.time(),
                   "iteration": iterations if author == "hld_critic" else None}
        # Wyciagnij text fragment z eventu (ADK content/parts)
        preview = ""
        try:
            content = getattr(ev, "content", None)
            if content and getattr(content, "parts", None):
                for p in content.parts:
                    t = getattr(p, "text", None)
                    if t:
                        preview = (preview + t)[:500]
        except Exception:  # pragma: no cover
            pass
        if preview:
            yield {"type": "stage_event", "stage": current_stage, "preview": preview,
                   "ts": time.time()}

    if current_stage is not None:
        yield {"type": "stage_end", "stage": current_stage, "ts": time.time()}

    final_session = await runner.session_service.get_session(
        app_name="spec_generator_web", user_id="web", session_id=session.id,
    )
    state = final_session.state if final_session else {}
    hld = str(state.get("current_hld") or "").strip()
    epics = parse_epics_json(state.get("epics_json"))
    yield {"type": "done", "hld_markdown": hld, "epics": epics, "iterations": iterations}


async def _run_scaffold_streaming(req: GenerateRequest) -> AsyncIterator[dict]:
    """Emuluje pipeline w trybie scaffold - stage'y z opoznieniami zeby UI mial co pokazac."""
    stages = [
        ("ticket_fetcher", 0.4, "Pobieram ticket z Jira (mock)..."),
        ("hld_writer", 0.7, "Pisze HLD na podstawie ticketu..."),
        ("hld_critic", 0.5, "Krytyk ocenia HLD (placeholder)..."),
        ("epic_extractor", 0.5, "Wyciagam epiki z HLD..."),
    ]
    for stage, delay, preview in stages:
        yield {"type": "stage_start", "stage": stage, "ts": time.time(), "iteration": None}
        await asyncio.sleep(delay)
        yield {"type": "stage_event", "stage": stage, "preview": preview, "ts": time.time()}
        yield {"type": "stage_end", "stage": stage, "ts": time.time()}

    hld = (
        f"# HLD: {req.issue_key} (SCAFFOLD)\n\n"
        "## 1. Cel biznesowy\n"
        "Tryb scaffold - ustaw SPEC_GEN_USE_REAL_PIPELINE=1 + GOOGLE_CLOUD_PROJECT "
        "aby wygenerowac realny HLD.\n"
    )
    epics = [
        {
            "title": f"[{req.issue_key}] Epik demo",
            "summary": "Placeholder epika przed podlaczeniem Gemini.",
            "acceptance_criteria": ["GIVEN... WHEN... THEN..."],
            "priority": "Medium",
            "labels": ["scaffold"],
            "estimated_story_points": 5,
            "dependencies": [],
        }
    ]
    yield {"type": "done", "hld_markdown": hld, "epics": epics, "iterations": 0}


@app.get("/", response_class=HTMLResponse)
def index():
    return INDEX_HTML


@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": "0.2.0-mvp",
        "real_pipeline": _should_use_real_pipeline(),
    }


@app.post("/api/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest):
    """Generuje HLD + Epiki. W trybie scaffold zwraca placeholdery, w real - odpalenie Runnera."""
    session_id = uuid.uuid4().hex[:12]

    if _should_use_real_pipeline():
        try:
            hld, epics = await _run_real_pipeline(req)
            status = "real" if hld else "real_empty"
        except Exception as e:  # pragma: no cover - zalezne od srodowiska
            logger.exception("Real pipeline failure")
            raise HTTPException(status_code=500, detail=f"pipeline error: {e}") from e
    else:
        hld = (
            f"# HLD: {req.issue_key} (SCAFFOLD)\n\n"
            "## 1. Cel biznesowy\n"
            "Tryb scaffold - ustaw SPEC_GEN_USE_REAL_PIPELINE=1 + GOOGLE_CLOUD_PROJECT "
            "aby wygenerowac realny HLD.\n"
        )
        epics = [
            {
                "title": f"[{req.issue_key}] Epik demo",
                "summary": "Placeholder epika przed podlaczeniem Gemini.",
                "acceptance_criteria": ["GIVEN... WHEN... THEN..."],
                "priority": "Medium",
                "labels": ["scaffold"],
                "estimated_story_points": 5,
                "dependencies": [],
            }
        ]
        status = "scaffold"

    _SESSIONS[session_id] = {"hld": hld, "epics": epics, "approved": False, "mode": status}
    return GenerateResponse(
        session_id=session_id,
        hld_markdown=hld,
        epics=epics,
        status=status,
    )


@app.post("/api/generate/stream")
async def generate_stream(req: GenerateRequest):
    """Streamuje progress generacji przez SSE.

    Format SSE: `data: <json>\\n\\n`. Eventy: stage_start, stage_event, stage_end, done, error.
    Frontend uzywa fetch + ReadableStream (EventSource nie wspiera POST).
    Sesja jest zapisana do _SESSIONS w evencie `done` aby pozniej mozna bylo opublikowac.
    """
    session_id = uuid.uuid4().hex[:12]
    use_real = _should_use_real_pipeline()

    async def event_stream() -> AsyncIterator[bytes]:
        # Zaczynamy od session_id zeby UI mial za co zlapac
        first = {"type": "session", "session_id": session_id,
                 "mode": "real" if use_real else "scaffold"}
        yield f"data: {json.dumps(first)}\n\n".encode("utf-8")

        events_log: list[dict] = []
        final_hld = ""
        final_epics: list[dict] = []
        try:
            iterator = _run_real_pipeline_streaming(req) if use_real else _run_scaffold_streaming(req)
            async for ev in iterator:
                events_log.append(ev)
                if ev.get("type") == "done":
                    final_hld = ev.get("hld_markdown", "")
                    final_epics = ev.get("epics", [])
                yield f"data: {json.dumps(ev, ensure_ascii=False)}\n\n".encode("utf-8")
        except Exception as e:  # pragma: no cover - zalezne od srodowiska
            logger.exception("Streaming pipeline failure")
            err = {"type": "error", "message": str(e)}
            yield f"data: {json.dumps(err)}\n\n".encode("utf-8")
            return

        status = "real" if (use_real and final_hld) else ("real_empty" if use_real else "scaffold")
        _SESSIONS[session_id] = {
            "hld": final_hld,
            "epics": final_epics,
            "approved": False,
            "mode": status,
            "events_log": events_log,
        }
        end = {"type": "end", "session_id": session_id, "status": status}
        yield f"data: {json.dumps(end)}\n\n".encode("utf-8")

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # disable buffering w nginx
            "Connection": "keep-alive",
        },
    )


@app.get("/api/sessions/{session_id}")
def get_session(session_id: str):
    sess = _SESSIONS.get(session_id)
    if sess is None:
        raise HTTPException(status_code=404, detail="session not found")
    return {
        "session_id": session_id,
        "hld_markdown": sess.get("hld", ""),
        "epics": sess.get("epics", []),
        "approved": sess.get("approved", False),
        "mode": sess.get("mode", "scaffold"),
    }


class SaveEditsRequest(BaseModel):
    epics: list[dict]
    hld_markdown: Optional[str] = None


@app.put("/api/sessions/{session_id}")
def save_edits(session_id: str, req: SaveEditsRequest):
    sess = _SESSIONS.get(session_id)
    if sess is None:
        raise HTTPException(status_code=404, detail="session not found")
    sess["epics"] = req.epics
    if req.hld_markdown is not None:
        sess["hld"] = req.hld_markdown
    return {"status": "ok", "session_id": session_id, "epics_count": len(req.epics)}


def _build_export_markdown(session_id: str, sess: dict) -> str:
    """Buduje pelny dokument MD: HLD + sekcja epikow."""
    lines: list[str] = []
    lines.append(f"<!-- Spec Generator session: {session_id} mode: {sess.get('mode')} -->\n")
    lines.append(sess.get("hld", "").rstrip())
    lines.append("\n\n---\n\n# Epiki\n")
    for i, epic in enumerate(sess.get("epics", []), start=1):
        lines.append(f"\n## {i}. {epic.get('title', '(bez tytulu)')}\n")
        lines.append(f"**Priorytet:** {epic.get('priority', 'Medium')}  ")
        lines.append(f"**Story points:** {epic.get('estimated_story_points', 0)}\n")
        if epic.get("summary"):
            lines.append(f"\n{epic['summary']}\n")
        ac = epic.get("acceptance_criteria") or []
        if ac:
            lines.append("\n**Acceptance criteria:**\n")
            for c in ac:
                lines.append(f"- {c}")
        labels = epic.get("labels") or []
        if labels:
            lines.append("\n\n**Labels:** " + ", ".join(f"`{l}`" for l in labels))
        deps = epic.get("dependencies") or []
        if deps:
            lines.append("\n**Dependencies:** " + ", ".join(f"`{d}`" for d in deps))
        lines.append("\n")
    return "\n".join(lines)


@app.get("/api/sessions/{session_id}/export.md")
def export_markdown(session_id: str):
    sess = _SESSIONS.get(session_id)
    if sess is None:
        raise HTTPException(status_code=404, detail="session not found")
    md = _build_export_markdown(session_id, sess)
    return StreamingResponse(
        iter([md.encode("utf-8")]),
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="spec-{session_id}.md"'},
    )


@app.get("/api/sessions/{session_id}/export.json")
def export_json(session_id: str):
    sess = _SESSIONS.get(session_id)
    if sess is None:
        raise HTTPException(status_code=404, detail="session not found")
    payload = {
        "session_id": session_id,
        "mode": sess.get("mode"),
        "approved": sess.get("approved", False),
        "hld_markdown": sess.get("hld", ""),
        "epics": sess.get("epics", []),
    }
    body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    return StreamingResponse(
        iter([body]),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="spec-{session_id}.json"'},
    )


@app.post("/api/publish/{session_id}")
def publish(session_id: str, req: PublishRequest):
    sess = _SESSIONS.get(session_id)
    if sess is None:
        raise HTTPException(status_code=404, detail="session not found")
    if not req.approved:
        raise HTTPException(status_code=400, detail="approved=False - nothing to publish")
    # Zapisz edytowane epiki w sesji jezeli przyszly
    if req.edited_epics is not None:
        sess["epics"] = req.edited_epics
    sess["approved"] = True
    # TODO Sprint 2: wywolaj build_jira_publisher z MCP tools
    return JSONResponse({
        "status": "scaffold",
        "mode": sess.get("mode", "scaffold"),
        "note": "Real publish do Jira bedzie po podlaczeniu Comarch MCP (rotate tokens first).",
        "would_publish": sess["epics"],
        "epics_count": len(sess["epics"]),
    })


if __name__ == "__main__":  # pragma: no cover
    import uvicorn
    from config import get_settings
    s = get_settings()
    uvicorn.run(app, host=s.web_host, port=s.web_port)

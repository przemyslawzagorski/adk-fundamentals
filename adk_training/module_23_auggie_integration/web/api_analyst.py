"""FastAPI router dla module_20 Analyst System.

Endpointy:
  GET  /api/analyst/config                                — co jest skonfigurowane (jira/conf/nblm)
  POST /api/analyst/generate                              — SSE: pipeline ticket -> HLD -> epiki
  GET  /api/analyst/sessions                              — lista ostatnich sesji (in-memory)
  GET  /api/analyst/sessions/{id}                         — pełne artefakty (ticket/HLD/epiki)
  POST /api/analyst/sessions/{id}/publish/jira            — HITL approval -> Jira create_issue per epik
  POST /api/analyst/sessions/{id}/publish/confluence      — HITL approval -> Confluence create_page

Sesje trzymamy w pamięci (proces FastAPI). Restart = utrata historii.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import time
import uuid
from typing import Any, AsyncIterator, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from adk_training.module_20_analyst_system.agents.epic_decomposer import parse_epics_json
from adk_training.module_20_analyst_system.clients import (
    get_jira_client,
    get_confluence_client,
    JiraError,
    ConfluenceError,
)
from adk_training.module_20_analyst_system.orchestrators.ticket_to_hld import (
    build_ticket_to_hld_orchestrator,
)
from adk_training.module_20_analyst_system.tools import notebooklm_tool

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/analyst", tags=["analyst"])

_APP_NAME = "module_20_analyst"
_USER_ID = "analyst-ui"
_SESSION_TTL_SECONDS = 60 * 60 * 6  # 6h
_MAX_SESSIONS = 50

_SESSIONS: Dict[str, Dict[str, Any]] = {}

# Stage display order (matches sub_agent order in orchestrator)
_PIPELINE_STAGES = [
    "ticket_fetcher",
    "context_gatherer",
    "hld_writer",
    "critique_loop",
    "epic_decomposer",
]


# ----------------------------- models ----------------------------------------


class GenerateRequest(BaseModel):
    issue_key: str = Field(..., description="Klucz Jira, np. SWOK-1234.")
    max_critique_iterations: int = Field(3, ge=1, le=5)
    enable_notebooklm: Optional[bool] = Field(
        None, description="Override env NOTEBOOKLM_ENABLED dla tej sesji."
    )
    notebooklm_url: Optional[str] = Field(
        None, description="Override env NOTEBOOKLM_NOTEBOOK_URL dla tej sesji."
    )
    model: Optional[str] = Field(None, description="Override ADK_MODEL dla tej sesji.")


class PublishJiraRequest(BaseModel):
    project_key: str = Field(..., description="Klucz projektu Jira, np. SWOK.")
    epics: List[Dict[str, Any]] = Field(
        ..., description="Lista epików (po edycji w UI) — ten sam schemat co z epic_decomposer."
    )
    parent_key: Optional[str] = Field(
        None, description="Klucz ticketu nadrzędnego (np. inicjatywa)."
    )
    add_acceptance_criteria_in_description: bool = True


class PublishConfluenceRequest(BaseModel):
    space_key: str
    title: str
    parent_id: Optional[str] = None
    labels: Optional[List[str]] = None


# ----------------------------- helpers ---------------------------------------


_ISSUE_KEY_RE = re.compile(r"^[A-Z][A-Z0-9_]+-\d+$")


def _validate_issue_key(key: str) -> str:
    key = (key or "").strip().upper()
    if not _ISSUE_KEY_RE.match(key):
        raise HTTPException(400, f"Invalid Jira issue key: {key!r}")
    return key


def _sse(event_obj: Dict[str, Any]) -> str:
    return f"data: {json.dumps(event_obj, default=str, ensure_ascii=False)}\n\n"


def _gc_sessions() -> None:
    """Drop sessions older than TTL or beyond cap (keep newest)."""
    now = time.time()
    expired = [sid for sid, s in _SESSIONS.items() if now - s.get("created", now) > _SESSION_TTL_SECONDS]
    for sid in expired:
        _SESSIONS.pop(sid, None)
    if len(_SESSIONS) > _MAX_SESSIONS:
        sorted_ids = sorted(_SESSIONS.items(), key=lambda kv: kv[1].get("created", 0))
        for sid, _ in sorted_ids[: len(_SESSIONS) - _MAX_SESSIONS]:
            _SESSIONS.pop(sid, None)


def _markdown_to_storage_xhtml(md: str) -> str:
    """Best-effort konwersja Markdown -> Confluence storage (XHTML).

    Preferujemy `markdown` (jeśli zainstalowany) — inaczej zwracamy markdown
    opakowany w `<ac:structured-macro name='markdown'>` jeśli macro jest
    dostępne na instancji, lub plain `<pre>` jako fallback bezpieczny.
    """
    try:
        import markdown as _md  # type: ignore
        html = _md.markdown(md, extensions=["fenced_code", "tables", "toc"])
        return html
    except ImportError:
        # plain fallback — zachowuje treść, choć bez formatowania
        from html import escape
        return f"<pre>{escape(md)}</pre>"


def _epic_to_jira_description(epic: Dict[str, Any], add_ac: bool) -> str:
    """Buduje pełny opis Jira (Markdown — Jira DC obsługuje gdy włączony Markdown
    parser; inaczej widoczny jako tekst). Trzymamy się czytelnego layoutu."""
    parts: List[str] = []
    summary = epic.get("summary") or ""
    if summary:
        parts.append(str(summary))

    scope = epic.get("scope") or []
    if scope:
        parts.append("## Zakres\n" + "\n".join(f"- {x}" for x in scope))

    out_of_scope = epic.get("out_of_scope") or []
    if out_of_scope:
        parts.append("## Poza zakresem\n" + "\n".join(f"- {x}" for x in out_of_scope))

    user_stories = epic.get("user_stories") or []
    if user_stories:
        lines = ["## User Stories"]
        for us in user_stories:
            if isinstance(us, dict):
                lines.append(
                    f"- Jako **{us.get('as_a', '?')}** chcę **{us.get('i_want', '?')}**, "
                    f"aby **{us.get('so_that', '?')}**."
                )
            else:
                lines.append(f"- {us}")
        parts.append("\n".join(lines))

    if add_ac:
        ac = epic.get("acceptance_criteria") or []
        if ac:
            parts.append("## Acceptance Criteria\n" + "\n".join(f"- {x}" for x in ac))

    deps = epic.get("dependencies") or []
    if deps:
        parts.append("## Zależności\n" + "\n".join(f"- {x}" for x in deps))

    refs = epic.get("hld_section_refs") or []
    if refs:
        parts.append("## Powiązane sekcje HLD\n" + ", ".join(str(r) for r in refs))

    estimate = epic.get("estimate_t_shirt")
    if estimate:
        parts.append(f"_Estymata (t-shirt): **{estimate}**_")

    return "\n\n".join(parts).strip()


# ----------------------------- endpoints -------------------------------------


@router.get("/config")
async def get_config() -> Dict[str, Any]:
    jira = get_jira_client()
    conf = get_confluence_client()
    return {
        "jira": {
            "configured": jira is not None,
            "base_url": (jira.base_url if jira else None),
        },
        "confluence": {
            "configured": conf is not None,
            "base_url": (conf.base_url if conf else None),
        },
        "notebooklm": {
            "enabled": notebooklm_tool.is_enabled(),
            "notebook_url": os.getenv("NOTEBOOKLM_NOTEBOOK_URL"),
        },
        "model": os.getenv("ADK_MODEL", "gemini-2.5-flash"),
        "defaults": {
            "max_critique_iterations": int(os.getenv("ANALYST_MAX_CRITIQUE_ITERATIONS", "3")),
        },
    }


@router.post("/generate")
async def generate(req: GenerateRequest):
    """SSE pipeline: ticket -> kontekst -> HLD -> samokrytyka -> epiki."""
    issue_key = _validate_issue_key(req.issue_key)
    _gc_sessions()
    session_id = uuid.uuid4().hex[:12]

    _SESSIONS[session_id] = {
        "id": session_id,
        "created": time.time(),
        "issue_key": issue_key,
        "model": req.model or os.getenv("ADK_MODEL", "gemini-2.5-flash"),
        "max_critique_iterations": req.max_critique_iterations,
        "ticket": "",
        "wiki_context": "",
        "domain_context": "",
        "current_hld": "",
        "epics_json_raw": "",
        "epics": [],
        "status": "running",
        "error": None,
        "stages": [],
    }
    record = _SESSIONS[session_id]

    # Apply per-request NotebookLM overrides BEFORE building agent (env-driven).
    if req.enable_notebooklm is not None:
        os.environ["NOTEBOOKLM_ENABLED"] = "1" if req.enable_notebooklm else "0"
    if req.notebooklm_url:
        notebooklm_tool.set_notebook_url(req.notebooklm_url)

    orchestrator = build_ticket_to_hld_orchestrator(
        max_critique_iterations=req.max_critique_iterations,
        model=req.model,
    )

    queue: asyncio.Queue = asyncio.Queue()

    async def runner_task():
        session_service = InMemorySessionService()
        adk_session = await session_service.create_session(
            app_name=_APP_NAME,
            user_id=_USER_ID,
            state={},
        )
        runner = Runner(
            agent=orchestrator,
            app_name=_APP_NAME,
            session_service=session_service,
        )
        # Wiadomość użytkownika — dostarcza klucz ticketu do ticket_fetcher
        user_msg = genai_types.Content(
            role="user",
            parts=[genai_types.Part(text=f"Pobierz i przeanalizuj ticket Jira: {issue_key}")],
        )

        seen_authors: set[str] = set()
        try:
            await queue.put({"type": "session_start", "session_id": session_id})
            await queue.put({"type": "stages", "stages": _PIPELINE_STAGES})

            async for event in runner.run_async(
                user_id=adk_session.user_id,
                session_id=adk_session.id,
                new_message=user_msg,
            ):
                author = getattr(event, "author", None)
                if author and author not in seen_authors and author in _PIPELINE_STAGES:
                    seen_authors.add(author)
                    await queue.put({"type": "stage_active", "stage": author})

                # Surface text snippets for live preview
                content = getattr(event, "content", None)
                if content and getattr(content, "parts", None):
                    text_chunks = [
                        p.text for p in content.parts if getattr(p, "text", None)
                    ]
                    if text_chunks and author:
                        await queue.put({
                            "type": "text",
                            "stage": author,
                            "text": "".join(text_chunks),
                        })

            # Po zakończeniu odczyt finalnego stanu
            final_session = await session_service.get_session(
                app_name=_APP_NAME, user_id=_USER_ID, session_id=adk_session.id
            )
            state = dict(final_session.state) if final_session else {}

            record["ticket"] = state.get("ticket", "")
            record["wiki_context"] = state.get("wiki_context", "")
            record["domain_context"] = state.get("domain_context", "")
            record["current_hld"] = state.get("current_hld", "")
            record["epics_json_raw"] = state.get("epics_json", "")
            record["epics"] = parse_epics_json(state.get("epics_json"))
            record["status"] = "ready"
            record["stages"] = list(seen_authors)

            await queue.put({
                "type": "done",
                "session_id": session_id,
                "epics_count": len(record["epics"]),
                "hld_chars": len(record["current_hld"]),
            })
        except Exception as exc:
            logger.exception("Pipeline failed for session %s", session_id)
            record["status"] = "error"
            record["error"] = str(exc)
            await queue.put({"type": "error", "session_id": session_id, "message": str(exc)})
        finally:
            await queue.put({"type": "__done__"})

    async def stream() -> AsyncIterator[str]:
        task = asyncio.create_task(runner_task())
        try:
            while True:
                ev = await queue.get()
                if ev.get("type") == "__done__":
                    break
                yield _sse(ev)
        finally:
            if not task.done():
                task.cancel()

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/sessions")
async def list_sessions() -> List[Dict[str, Any]]:
    """Najnowsze sesje, posortowane DESC."""
    _gc_sessions()
    items = [
        {
            "id": s["id"],
            "created": s["created"],
            "issue_key": s["issue_key"],
            "status": s["status"],
            "hld_chars": len(s.get("current_hld", "")),
            "epics_count": len(s.get("epics", [])),
        }
        for s in _SESSIONS.values()
    ]
    items.sort(key=lambda x: x["created"], reverse=True)
    return items


@router.get("/sessions/{session_id}")
async def get_session(session_id: str) -> Dict[str, Any]:
    s = _SESSIONS.get(session_id)
    if not s:
        raise HTTPException(404, f"Session {session_id} not found")
    return s


@router.post("/sessions/{session_id}/publish/jira")
async def publish_jira(session_id: str, req: PublishJiraRequest) -> Dict[str, Any]:
    s = _SESSIONS.get(session_id)
    if not s:
        raise HTTPException(404, f"Session {session_id} not found")
    client = get_jira_client()
    if client is None:
        raise HTTPException(400, "Jira client not configured (set JIRA_DC_BASE_URL + JIRA_DC_PAT).")

    if not req.epics:
        raise HTTPException(400, "Epics list is empty.")

    created: List[Dict[str, Any]] = []
    failures: List[Dict[str, Any]] = []
    key_map: Dict[str, str] = {}  # title -> created Jira key (for linking dependencies)

    for idx, epic in enumerate(req.epics):
        title = (epic.get("title") or "").strip()
        if not title:
            failures.append({"index": idx, "error": "Missing 'title'"})
            continue
        try:
            description = _epic_to_jira_description(
                epic, add_ac=req.add_acceptance_criteria_in_description
            )
            issue_key_str = client.create_issue(
                project_key=req.project_key,
                summary=title[:240],  # Jira limit ~255
                description=description,
                issue_type="Epic",
                labels=epic.get("labels") or None,
                priority=epic.get("priority") or None,
                epic_name=title[:240],
                parent_key=req.parent_key,
            )
            issue_url = f"{client.base_url}/browse/{issue_key_str}"
            key_map[title] = issue_key_str
            created.append({
                "index": idx,
                "title": title,
                "key": issue_key_str,
                "url": issue_url,
            })
        except JiraError as je:
            failures.append({"index": idx, "title": title, "error": str(je)})
        except Exception as exc:
            logger.exception("Unexpected Jira create failure (idx=%s)", idx)
            failures.append({"index": idx, "title": title, "error": f"unexpected: {exc}"})

    s.setdefault("published_jira", []).extend(created)
    s["jira_failures"] = failures

    return {
        "session_id": session_id,
        "created": created,
        "failures": failures,
        "ok": len(failures) == 0,
    }


@router.post("/sessions/{session_id}/publish/confluence")
async def publish_confluence(session_id: str, req: PublishConfluenceRequest) -> Dict[str, Any]:
    s = _SESSIONS.get(session_id)
    if not s:
        raise HTTPException(404, f"Session {session_id} not found")
    client = get_confluence_client()
    if client is None:
        raise HTTPException(400, "Confluence client not configured (set CONFLUENCE_DC_BASE_URL + CONFLUENCE_DC_PAT).")

    hld = s.get("current_hld") or ""
    if not hld.strip():
        raise HTTPException(400, "Session has no HLD to publish.")

    body = _markdown_to_storage_xhtml(hld)
    try:
        page = client.create_page(
            space_key=req.space_key,
            title=req.title,
            body_storage_xhtml=body,
            parent_id=req.parent_id,
            labels=req.labels,
        )
    except ConfluenceError as ce:
        raise HTTPException(502, f"Confluence error: {ce}") from ce

    published = {
        "id": page.id,
        "title": page.title,
        "url": page.url,
        "version": page.version,
    }
    s["published_confluence"] = published
    return {"session_id": session_id, "ok": True, "page": published}

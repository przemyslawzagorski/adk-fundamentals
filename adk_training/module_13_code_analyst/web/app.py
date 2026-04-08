"""
Code Analyst - Agentic Web UI
==============================
System agentowy do analizy kodu z workflow'ami biznesowymi.

Agentic pipeline:
  SequentialAgent: code_analyst -> solution_architect
  - code_analyst:      RAG search + MCP (Jira/Wiki/GitLab)
  - solution_architect: propozycje, diagramy, stories

Start:
    cd adk_training/module_13_code_analyst/web
    python app.py
"""

import os
import sys
import asyncio
import time
import json
from typing import Optional

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

# --- Path setup ---
_web_dir = os.path.dirname(os.path.abspath(__file__))
_module_dir = os.path.dirname(_web_dir)

# Load Vertex AI credentials
load_dotenv(os.path.join(_module_dir, ".env"))

# Enable imports from parent module (code_indexer, etc.)
if _module_dir not in sys.path:
    sys.path.insert(0, _module_dir)

from repo_manager import RepoManager, RepoInfo
from code_indexer import CodeIndexer
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# MCP imports (optional — only when Comarch MCP tokens are configured AND reachable)
_MCP_CONFIGURED = False  # tokens present in .env
_MCP_AVAILABLE = False   # tokens present AND network reachable
try:
    from google.adk.tools.mcp_tool.mcp_toolset import (
        McpToolset,
        StdioConnectionParams,
        StdioServerParameters,
    )
    if os.environ.get("JIRA_BEARER_TOKEN"):
        _MCP_CONFIGURED = True
        _mcp_enabled_env = os.environ.get("MCP_ENABLED", "auto").lower()
        if _mcp_enabled_env == "false" or _mcp_enabled_env == "0":
            _MCP_AVAILABLE = False
        elif _mcp_enabled_env == "true" or _mcp_enabled_env == "1":
            _MCP_AVAILABLE = True
        else:
            # Auto-detect: TCP connect in a thread (DNS can hang on Windows)
            import socket
            from urllib.parse import urlparse
            from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

            def _check_host(url: str) -> bool:
                parsed = urlparse(url)
                host = parsed.hostname or ""
                port = parsed.port or (443 if parsed.scheme == "https" else 80)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                try:
                    sock.connect((host, port))
                    return True
                except Exception:
                    return False
                finally:
                    sock.close()

            _jira_url = os.environ.get("JIRA_BASE_URL", "")
            if _jira_url:
                try:
                    with ThreadPoolExecutor(max_workers=1) as _pool:
                        _MCP_AVAILABLE = _pool.submit(_check_host, _jira_url).result(timeout=3)
                except (FuturesTimeout, Exception):
                    _MCP_AVAILABLE = False
except ImportError:
    pass

# =========================================================================
# Configuration
# =========================================================================

DATA_DIR = os.environ.get(
    "CODE_ANALYST_DATA", os.path.join(_module_dir, "web_data")
)
HOST = os.environ.get("CODE_ANALYST_HOST", "127.0.0.1")
PORT = int(os.environ.get("CODE_ANALYST_PORT", "8088"))

# =========================================================================
# Application State
# =========================================================================

repo_manager = RepoManager(data_dir=DATA_DIR)
session_service = InMemorySessionService()

_indexers: dict[str, CodeIndexer] = {}
_runners: dict[str, Runner] = {}
_session_ids: dict[str, str] = {}  # repo_id -> session_id
_indexing_status: dict[str, dict] = {}  # repo_id -> {status, message, ...}

# =========================================================================
# Helpers
# =========================================================================


def get_indexer(repo_id: str) -> CodeIndexer:
    """Lazily create or retrieve a CodeIndexer for the given repo."""
    if repo_id not in _indexers:
        repo = repo_manager.get(repo_id)
        if not repo:
            raise HTTPException(status_code=404, detail="Repo nie znalezione")
        _indexers[repo_id] = CodeIndexer(
            project_dir=repo.path,
            persist_dir=repo_manager.get_index_dir(repo_id),
        )
    return _indexers[repo_id]


def _refresh_repo(repo_id: str) -> Optional[RepoInfo]:
    """Load repo and attach up-to-date index stats if available."""
    repo = repo_manager.get(repo_id)
    if not repo:
        return None
    try:
        indexer = get_indexer(repo_id)
        if indexer._has_persisted_index():
            stats = indexer.get_stats()
            repo.total_chunks = stats["total_chunks"]
            repo.indexed_files = stats["indexed_files"]
            if repo.status == "new":
                repo.status = "ready"
    except Exception:
        pass
    return repo


# =========================================================================
# Agent Factory — SequentialAgent (agentic pipeline)
# =========================================================================

# Workflow scenario definitions — each has a prompt template
WORKFLOWS = {
    "onboarding": {
        "name": "Onboarding developera",
        "icon": "&#128100;",
        "description": "Opisz architekture, kluczowe klasy i flow danych w projekcie",
        "prompt": (
            "Przeprowadz onboarding nowego developera dla tego projektu. "
            "1) Przeszukaj kod i opisz architekture (warstwy, moduly). "
            "2) Wypisz kluczowe klasy/serwisy z ich odpowiedzialnoscia. "
            "3) Opisz glowne flow danych (np. request -> controller -> service -> repo). "
            "4) Wygeneruj diagram Mermaid z architektura."
        ),
    },
    "impact": {
        "name": "Analiza wplywu zmian",
        "icon": "&#128269;",
        "description": "Podaj opis zmiany — agent znajdzie dotykane pliki i oceni ryzyko",
        "prompt_template": (
            "Przeprowadz analize wplywu dla zmiany: '{user_input}'. "
            "1) Przeszukaj kod pod katem powiazanych plikow. "
            "2) Zidentyfikuj wszystkie dotykane klasy/metody. "
            "3) Znajdz powiazane testy. "
            "4) Ocen ryzyko regresji (niskie/srednie/wysokie). "
            "5) Wygeneruj raport z lista plikow do modyfikacji."
        ),
        "input_placeholder": "Opisz zmiane, np. 'zmiana formatu daty w API zamowien'",
    },
    "security": {
        "name": "Audyt bezpieczenstwa",
        "icon": "&#128274;",
        "description": "Przeskanuj kod pod katem podatnosci (SQL injection, hardcoded secrets, itp.)",
        "prompt": (
            "Przeprowadz audyt bezpieczenstwa kodu. "
            "1) Szukaj: SQL injection (string concatenation w zapytaniach). "
            "2) Szukaj: hardcoded secrets, tokeny, hasla. "
            "3) Szukaj: brak walidacji inputu uzytkownika. "
            "4) Szukaj: niebezpieczne operacje na plikach. "
            "5) Dla kazdego znaleziska podaj: plik, linia, opis podatnosci, rekomendacja naprawy. "
            "6) Podsumuj: ile krytycznych, ile srednich, ile niskich."
        ),
    },
    "stories": {
        "name": "Generuj stories",
        "icon": "&#128221;",
        "description": "Opisz feature — agent wygeneruje stories z AC i DoD",
        "prompt_template": (
            "Na podstawie opisu feature: '{user_input}'. "
            "1) Przeszukaj istniejacy kod aby zrozumiec kontekst. "
            "2) Zaproponuj rozwiazanie techniczne z diagramem Mermaid. "
            "3) Rozbij na stories (3-6 sztuk). Kazda story ma: "
            "   - Tytul, Opis (2-3 zdania), Acceptance Criteria, Definition of Done. "
            "4) Oszacuj zlozonosc kazdej story (S/M/L/XL). "
            "5) Podaj kolejnosc implementacji."
        ),
        "input_placeholder": "Opisz feature, np. 'eksport raportow do PDF'",
    },
    "document": {
        "name": "Generuj dokumentacje",
        "icon": "&#128196;",
        "description": "Wygeneruj dokumentacje techniczna modulu",
        "prompt_template": (
            "Wygeneruj dokumentacje techniczna dla: '{user_input}'. "
            "1) Przeszukaj kod i znajdz powiazane pliki. "
            "2) Opisz odpowiedzialnosc modulu. "
            "3) Wylistuj publiczne API/endpointy/metody. "
            "4) Wygeneruj diagram klas (Mermaid classDiagram). "
            "5) Wygeneruj diagram sekwencji glownego flow (Mermaid sequenceDiagram). "
            "6) Opisz zaleznosci zewnetrzne."
        ),
        "input_placeholder": "Nazwa modulu lub klasy, np. 'modul autoryzacji'",
    },
    "debug": {
        "name": "Debugging z kontekstem",
        "icon": "&#128027;",
        "description": "Podaj blad/stacktrace — agent znajdzie przyczyne w kodzie",
        "prompt_template": (
            "Pomoz zdebugowac problem: '{user_input}'. "
            "1) Przeszukaj kod pod katem klas/metod z opisu bledu. "
            "2) Zidentyfikuj prawdopodobna przyczyne. "
            "3) Sprawdz czy sa testy pokrywajace ten scenariusz. "
            "4) Zaproponuj fix z konkretnymi zmianami w kodzie. "
            "5) Zaproponuj dodatkowy test zapobiegajacy regresji."
        ),
        "input_placeholder": "Opis bledu lub stacktrace, np. 'NullPointerException w OrderService.processOrder'",
    },
}

# --- SequentialAgent instructions ---

_CODE_ANALYST_INSTRUCTION = """\
Jestes ekspertem od analizy kodu. Twoja rola w pipeline to ANALIZA — zbierz fakty.

## Narzedzia
- **search_code(query, top_k)** - Semantyczne przeszukiwanie zaindeksowanego kodu
- **get_index_stats()** - Statystyki indeksu (ile plikow, chunkow)
{mcp_section}

## Zasady
1. ZAWSZE uzyj search_code() — szukaj wielokrotnie z roznymi zapytaniami
2. Cytuj DOKLADNE sciezki plikow z wynikow (nie wymyslaj)
3. Podaj numery linii tam gdzie to mozliwe
4. Szukaj powiazanych testow automatycznie
5. Odpowiadaj po polsku
6. Na koncu stworz podsumowanie: jakie pliki znalazles i dlaczego sa istotne"""

_ARCHITECT_INSTRUCTION = """\
Jestes architektem oprogramowania. Twoja rola w pipeline to PROPOZYCJA — na podstawie
analizy kodu z poprzedniego kroku, wygeneruj konkretne rozwiazanie.

## Twoje zadania
1. Zaproponuj rozwiazanie techniczne (konkretne klasy, metody, zmiany)
2. Wygeneruj diagram Mermaid (sequence, class lub flowchart — wybierz najlepszy)
3. Jesli wymaga to stories — rozbij na 3-6 stories z AC i DoD
4. Oszacuj zlozonosc (S/M/L/XL) i ryzyko regresji (niskie/srednie/wysokie)

## Zasady
1. Badz KONKRETNY — podaj nazwy klas, metod, plikow (z analizy)
2. NIE wymyslaj plikow ktorych nie bylo w analizie
3. Diagramy Mermaid musza byc poprawne skladniowo
4. Odpowiadaj po polsku
5. Formatuj odpowiedz w Markdown z naglowkami"""

_MCP_INSTRUCTION_SECTION = """- **Narzedzia Jira** z MCP - wyszukiwanie ticketow, odczyt szczegolow
- **Narzedzia Wiki** z MCP - przeszukiwanie dokumentacji Confluence
- **Narzedzia GitLab** z MCP - projekty, MR, issues"""


def _build_mcp_toolset() -> Optional["McpToolset"]:
    """Create Comarch MCP toolset if tokens are configured."""
    if not _MCP_AVAILABLE:
        return None

    ca_cert = os.environ.get(
        "NODE_EXTRA_CA_CERTS",
        os.path.expanduser(r"~\Documents\cert\GK_COMARCH_ROOT_CA.crt"),
    )
    return McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="npx",
                args=[
                    "--registry",
                    os.environ.get(
                        "COMARCH_MCP_REGISTRY",
                        "https://nexus.czk.comarch/repository/ai-npm",
                    ),
                    "@comarch/mcp-integration-tool",
                ],
                env={
                    "MCP_MODE": "stdio",
                    "NODE_EXTRA_CA_CERTS": ca_cert,
                    "NODE_TLS_REJECT_UNAUTHORIZED": "0",
                    "HTTP_REJECT_UNAUTHORIZED": "false",
                    "JIRA_BASE_URL": os.environ.get("JIRA_BASE_URL", ""),
                    "JIRA_BEARER_TOKEN": os.environ.get("JIRA_BEARER_TOKEN", ""),
                    "WIKI_BASE_URL": os.environ.get("WIKI_BASE_URL", ""),
                    "WIKI_BEARER_TOKEN": os.environ.get("WIKI_BEARER_TOKEN", ""),
                    "GITLAB_BASE_URL": os.environ.get("GITLAB_BASE_URL", ""),
                    "GITLAB_TOKEN": os.environ.get("GITLAB_TOKEN", ""),
                },
            ),
            timeout=30.0,
        ),
    )


def _create_agent(indexer: CodeIndexer) -> SequentialAgent:
    """Create a SequentialAgent pipeline bound to a specific CodeIndexer.

    Pipeline: code_analyst (RAG + MCP) -> solution_architect (propozycje)
    """

    def search_code(query: str, top_k: int = 5) -> dict:
        """Przeszukaj zaindeksowany kod zrodlowy semantycznie.

        Uzyj tego narzedzia aby znalezc fragmenty kodu powiazane
        z opisem problemu lub funkcjonalnosci.

        Args:
            query: Opis tego czego szukasz, np. 'autoryzacja JWT'
            top_k: Ile najbardziej trafnych wynikow zwrocic (domyslnie 5)
        """
        results = indexer.query(query, top_k=top_k)
        stats = indexer.get_stats()
        return {
            "results": results,
            "total_files": stats["indexed_files"],
            "total_chunks": stats["total_chunks"],
        }

    def get_index_stats() -> dict:
        """Pokaz statystyki indeksu kodu - ile plikow i chunkow zaindeksowano."""
        return indexer.get_stats()

    # --- Build tool list ---
    analyst_tools: list = [
        FunctionTool(func=search_code),
        FunctionTool(func=get_index_stats),
    ]
    mcp_section = ""

    mcp_toolset = _build_mcp_toolset()
    if mcp_toolset:
        analyst_tools.append(mcp_toolset)
        mcp_section = _MCP_INSTRUCTION_SECTION

    analyst_instruction = _CODE_ANALYST_INSTRUCTION.format(
        mcp_section=mcp_section,
    )

    # --- Sub-agents ---
    code_analyst = LlmAgent(
        name="code_analyst",
        model="gemini-2.0-flash",
        instruction=analyst_instruction,
        tools=analyst_tools,
    )

    architect_tools: list = []
    if mcp_toolset:
        architect_tools.append(mcp_toolset)

    solution_architect = LlmAgent(
        name="solution_architect",
        model="gemini-2.0-flash",
        instruction=_ARCHITECT_INSTRUCTION,
        tools=architect_tools,
    )

    # --- Pipeline ---
    return SequentialAgent(
        name="code_analyst_pipeline",
        sub_agents=[code_analyst, solution_architect],
        description="Pipeline agentowy: analiza kodu -> propozycja rozwiazania",
    )


async def _get_runner(repo_id: str) -> Runner:
    """Get or create an ADK Runner for the repo."""
    if repo_id not in _runners:
        indexer = get_indexer(repo_id)
        agent = _create_agent(indexer)
        _runners[repo_id] = Runner(
            agent=agent,
            app_name=f"analyst_{repo_id}",
            session_service=session_service,
        )
    return _runners[repo_id]


async def _get_session_id(runner: Runner, repo_id: str) -> str:
    """Get or create a chat session for the repo."""
    if repo_id not in _session_ids:
        session = await session_service.create_session(
            app_name=runner.app_name,
            user_id="web_user",
        )
        _session_ids[repo_id] = session.id
    return _session_ids[repo_id]


# =========================================================================
# FastAPI App
# =========================================================================

app = FastAPI(title="Code Analyst")

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(_web_dir, "static")),
    name="static",
)

templates = Jinja2Templates(directory=os.path.join(_web_dir, "templates"))


# --- Jinja2 Custom Filters ---

def _format_time(timestamp: Optional[float]) -> str:
    if not timestamp:
        return "nigdy"
    elapsed = time.time() - timestamp
    if elapsed < 60:
        return "przed chwila"
    if elapsed < 3600:
        return f"{int(elapsed // 60)} min temu"
    if elapsed < 86400:
        return f"{int(elapsed // 3600)}h temu"
    return f"{int(elapsed // 86400)}d temu"


templates.env.filters["format_time"] = _format_time


# =========================================================================
# Routes: Full Pages
# =========================================================================


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    repos = repo_manager.list_all()
    return templates.TemplateResponse(
        "dashboard.html", {
            "request": request,
            "repos": repos,
            "mcp_available": _MCP_AVAILABLE,
            "mcp_configured": _MCP_CONFIGURED,
        }
    )


@app.get("/repos/{repo_id}", response_class=HTMLResponse)
async def repo_detail(request: Request, repo_id: str):
    repo = _refresh_repo(repo_id)
    if not repo:
        raise HTTPException(404)
    return templates.TemplateResponse(
        "repo.html", {
            "request": request,
            "repo": repo,
            "workflows": WORKFLOWS,
            "mcp_available": _MCP_AVAILABLE,
            "mcp_configured": _MCP_CONFIGURED,
        }
    )


# =========================================================================
# Routes: HTMX Actions
# =========================================================================


@app.post("/repos", response_class=HTMLResponse)
async def add_repo(
    request: Request,
    path: str = Form(..., max_length=500),
    name: str = Form("", max_length=100),
):
    repo, error = repo_manager.add(path, name)
    if error:
        return HTMLResponse(
            f'<div class="alert error">{error}</div>',
            status_code=422,
        )
    return HTMLResponse(
        status_code=200,
        headers={"HX-Redirect": f"/repos/{repo.id}"},
    )


@app.delete("/repos/{repo_id}", response_class=HTMLResponse)
async def remove_repo(repo_id: str):
    repo_manager.remove(repo_id)
    _indexers.pop(repo_id, None)
    _runners.pop(repo_id, None)
    _session_ids.pop(repo_id, None)
    return HTMLResponse(
        status_code=200,
        headers={"HX-Redirect": "/"},
    )


@app.post("/repos/{repo_id}/index", response_class=HTMLResponse)
async def index_repo(
    request: Request,
    repo_id: str,
    incremental: str = Form("true"),
):
    """Index or re-index a repository. Runs in thread pool."""
    repo = repo_manager.get(repo_id)
    if not repo:
        raise HTTPException(404)

    is_incremental = incremental.lower() not in ("false", "0", "no")
    indexer = get_indexer(repo_id)

    # Pre-count files to show estimate
    file_count = len(indexer._collect_files())
    _indexing_status[repo_id] = {
        "status": "running",
        "total_files": file_count,
        "message": f"Skanowanie {file_count} plikow...",
    }
    repo_manager.set_status(repo_id, "indexing")
    print(f"[Web] Indeksowanie startu: {repo.name} ({file_count} plikow, incremental={is_incremental})")

    try:
        stats = await asyncio.to_thread(
            indexer.index_project, None, None, is_incremental
        )
        repo_manager.update_stats(repo_id, stats)
        _indexing_status[repo_id] = {"status": "done"}
        print(f"[Web] Indeksowanie zakonczone: {repo.name} -> {stats}")

        # Invalidate cached runner — agent tools need fresh index data
        _runners.pop(repo_id, None)

        refreshed = _refresh_repo(repo_id)
        return templates.TemplateResponse("_stats.html", {
            "request": request,
            "repo": refreshed,
            "message": (
                f"Zaindeksowano {stats['indexed']} plikow, "
                f"pominieto {stats['skipped']}, "
                f"razem {stats['total_chunks']} chunkow "
                f"({stats.get('time_seconds', '?')}s)"
            ),
        })
    except Exception as e:
        repo_manager.set_status(repo_id, "error")
        _indexing_status[repo_id] = {"status": "error", "message": str(e)}
        import traceback
        traceback.print_exc()
        return HTMLResponse(
            f'<div class="alert error">Blad indeksowania: {e}</div>',
            status_code=500,
        )


@app.get("/repos/{repo_id}/index/status", response_class=HTMLResponse)
async def index_status(repo_id: str):
    """Check indexing status (polled by HTMX)."""
    status = _indexing_status.get(repo_id, {})
    if not status or status.get("status") == "done":
        return HTMLResponse("")
    msg = status.get("message", "Indeksowanie...")
    return HTMLResponse(
        f'<div class="indexing-progress">'
        f'<span class="progress-pulse"></span> {msg}'
        f'</div>'
    )


@app.post("/repos/{repo_id}/search", response_class=HTMLResponse)
async def search_repo(
    request: Request,
    repo_id: str,
    query: str = Form(..., min_length=1, max_length=500),
    top_k: int = Form(5),
):
    """Semantic code search in the indexed repository."""
    top_k = max(1, min(top_k, 20))
    indexer = get_indexer(repo_id)

    try:
        results = await asyncio.to_thread(indexer.query, query, top_k)
    except Exception as e:
        return HTMLResponse(
            f'<div class="alert error">Blad wyszukiwania: {e}</div>',
            status_code=500,
        )

    return templates.TemplateResponse("_search_results.html", {
        "request": request,
        "results": results,
        "query": query,
    })


async def _run_agent_pipeline(
    runner: Runner,
    session_id: str,
    message: str,
) -> dict:
    """Run the SequentialAgent pipeline and collect structured results.

    Returns dict with:
      - steps: list of {agent, action, detail} for each pipeline event
      - final_response: the last agent's text output
    """
    steps = []
    final_response = ""
    current_agent = ""

    content = types.Content(
        role="user",
        parts=[types.Part(text=message)],
    )

    async for event in runner.run_async(
        user_id="web_user",
        session_id=session_id,
        new_message=content,
    ):
        # Track which sub-agent is active
        author = getattr(event, "author", "") or ""
        if author and author != current_agent:
            current_agent = author
            steps.append({
                "agent": current_agent,
                "action": "start",
                "detail": f"Agent '{current_agent}' rozpoczal prace",
            })

        # Track tool calls
        if hasattr(event, "content") and event.content and event.content.parts:
            for part in event.content.parts:
                # Function call (tool invocation)
                if hasattr(part, "function_call") and part.function_call:
                    fc = part.function_call
                    tool_name = getattr(fc, "name", "?")
                    tool_args = getattr(fc, "args", {})
                    # Summarize args
                    args_summary = ""
                    if isinstance(tool_args, dict):
                        for k, v in list(tool_args.items())[:3]:
                            val_str = str(v)[:60]
                            args_summary += f" {k}={val_str}"
                    steps.append({
                        "agent": current_agent,
                        "action": "tool_call",
                        "detail": f"{tool_name}({args_summary.strip()})",
                    })

                # Function response (tool result)
                if hasattr(part, "function_response") and part.function_response:
                    fr = part.function_response
                    tool_name = getattr(fr, "name", "?")
                    steps.append({
                        "agent": current_agent,
                        "action": "tool_result",
                        "detail": f"{tool_name} -> wynik",
                    })

                # Text output  
                if hasattr(part, "text") and part.text:
                    final_response = part.text  # last text wins

    return {
        "steps": steps,
        "final_response": final_response,
    }


@app.post("/repos/{repo_id}/chat", response_class=HTMLResponse)
async def chat(
    request: Request,
    repo_id: str,
    message: str = Form(..., min_length=1, max_length=2000),
):
    """Chat with the SequentialAgent pipeline about the repo's code."""
    runner = await _get_runner(repo_id)
    session_id = await _get_session_id(runner, repo_id)

    try:
        result = await _run_agent_pipeline(runner, session_id, message)
        return templates.TemplateResponse("_chat_message.html", {
            "request": request,
            "user_message": message,
            "agent_response": result["final_response"] or "(brak odpowiedzi)",
            "steps": result["steps"],
        })
    except Exception as e:
        return templates.TemplateResponse("_chat_message.html", {
            "request": request,
            "user_message": message,
            "agent_response": f"Blad agenta: {e}",
            "steps": [],
        })


@app.post("/repos/{repo_id}/workflow", response_class=HTMLResponse)
async def run_workflow(
    request: Request,
    repo_id: str,
    workflow_id: str = Form(...),
    user_input: str = Form(""),
):
    """Execute a predefined agentic workflow scenario."""
    workflow = WORKFLOWS.get(workflow_id)
    if not workflow:
        return HTMLResponse(
            f'<div class="alert error">Nieznany workflow: {workflow_id}</div>',
            status_code=400,
        )

    # Build prompt from template
    if "prompt_template" in workflow:
        if not user_input.strip():
            return HTMLResponse(
                '<div class="alert error">Podaj dane wejsciowe dla tego scenariusza.</div>',
                status_code=422,
            )
        prompt = workflow["prompt_template"].format(user_input=user_input.strip())
    else:
        prompt = workflow["prompt"]

    # Use a fresh session for each workflow execution
    runner = await _get_runner(repo_id)
    session = await session_service.create_session(
        app_name=runner.app_name,
        user_id="web_user",
    )

    try:
        result = await _run_agent_pipeline(runner, session.id, prompt)
        return templates.TemplateResponse("_workflow_result.html", {
            "request": request,
            "workflow": workflow,
            "user_input": user_input,
            "steps": result["steps"],
            "response": result["final_response"] or "(brak odpowiedzi)",
        })
    except Exception as e:
        return templates.TemplateResponse("_workflow_result.html", {
            "request": request,
            "workflow": workflow,
            "user_input": user_input,
            "steps": [],
            "response": f"Blad pipeline: {e}",
        })


@app.post("/repos/{repo_id}/chat/reset", response_class=HTMLResponse)
async def reset_chat(repo_id: str):
    """Reset chat session for a repo."""
    _session_ids.pop(repo_id, None)
    _runners.pop(repo_id, None)
    return HTMLResponse('<div class="chat-info">Sesja czatu zresetowana.</div>')


# =========================================================================
# Entry Point
# =========================================================================

if __name__ == "__main__":
    import uvicorn

    print(f"\n  Code Analyst Web UI")
    print(f"  http://{HOST}:{PORT}\n")
    uvicorn.run("app:app", host=HOST, port=PORT, reload=True)

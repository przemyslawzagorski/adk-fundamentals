"""
Code Analyst — Produkcyjny system agentowy do analizy i modyfikacji kodu
=========================================================================
Multi-agent architecture:

  CLI (adk web):
    root_agent — pojedynczy LlmAgent z pełnym zestawem narzędzi

  Web UI (web/app.py):
    SequentialAgent pipeline z sub-agentami (code_analyst → senior_reviewer → implementer)

Tryby pracy:
  1. ANALIZA  — RAG search, onboarding, impact analysis, security audit
  2. BUG FIX — analiza → fix → test regresji → review → branch + commit
  3. CR/FEATURE — analiza → implementacja → testy → review → branch + commit
  4. TESTY   — analiza kodu → generowanie testów → review → branch + commit

Konfiguracja w .env — patrz .env.template.
"""

import os
import sys
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

# --- Path setup (pozwala na import z tego samego katalogu) ---
_module_dir = os.path.dirname(os.path.abspath(__file__))
if _module_dir not in sys.path:
    sys.path.insert(0, _module_dir)

load_dotenv(os.path.join(_module_dir, ".env"))

from code_retrieval_tool import search_code, index_project, get_index_stats  # noqa: E402
from git_tools import git_status, git_create_branch, git_commit, git_diff, git_log, git_checkout_back  # noqa: E402
from file_tools import read_project_file, write_project_file, list_project_files  # noqa: E402
from build_tools import run_build, run_tests  # noqa: E402

# =============================================================================
# NARZĘDZIA
# =============================================================================

# RAG (zawsze)
tool_search_code = FunctionTool(func=search_code)
tool_index_project = FunctionTool(func=index_project)
tool_get_stats = FunctionTool(func=get_index_stats)

# Git (lokalne operacje — branch + commit, nigdy push/merge)
tool_git_status = FunctionTool(func=git_status)
tool_git_create_branch = FunctionTool(func=git_create_branch)
tool_git_commit = FunctionTool(func=git_commit)
tool_git_diff = FunctionTool(func=git_diff)
tool_git_log = FunctionTool(func=git_log)
tool_git_checkout_back = FunctionTool(func=git_checkout_back)

# Pliki (odczyt pełnych plików + zapis)
tool_read_file = FunctionTool(func=read_project_file)
tool_write_file = FunctionTool(func=write_project_file)
tool_list_files = FunctionTool(func=list_project_files)

# Build & test
tool_run_build = FunctionTool(func=run_build)
tool_run_tests = FunctionTool(func=run_tests)

_all_tools = [
    # RAG
    tool_search_code, tool_index_project, tool_get_stats,
    # Git
    tool_git_status, tool_git_create_branch, tool_git_commit,
    tool_git_diff, tool_git_log, tool_git_checkout_back,
    # Pliki
    tool_read_file, tool_write_file, tool_list_files,
    # Build
    tool_run_build, tool_run_tests,
]
_mcp_instruction_parts = []
_active_integrations = []

# =============================================================================
# GITHUB MCP (opcjonalny — wymaga GITHUB_PERSONAL_ACCESS_TOKEN)
# =============================================================================


def _try_github_mcp():
    """Inicjalizuje GitHub MCP jeśli token jest ustawiony w .env."""
    token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN", "").strip()
    if not token:
        return None
    try:
        from google.adk.tools.mcp_tool.mcp_toolset import (
            McpToolset,
            StdioConnectionParams,
            StdioServerParameters,
        )

        toolset = McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=["-y", "@modelcontextprotocol/server-github"],
                    env={"GITHUB_PERSONAL_ACCESS_TOKEN": token},
                ),
                timeout=30.0,
            ),
        )
        print("[Code Analyst] GitHub MCP aktywne")
        return toolset
    except Exception as e:
        print(f"[Code Analyst] GitHub MCP niedostępne: {e}")
        return None


# =============================================================================
# COMARCH MCP (opcjonalny — wymaga VPN + tokeny Jira/GitLab/Wiki)
# =============================================================================


def _try_comarch_mcp():
    """Inicjalizuje Comarch MCP jeśli tokeny + sieć dostępne."""
    if not os.environ.get("JIRA_BEARER_TOKEN", "").strip():
        return None

    # Szybki test sieci (2s timeout) — nie blokuje startu jeśli VPN wyłączony
    import socket
    from urllib.parse import urlparse
    from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

    jira_url = os.environ.get("JIRA_BASE_URL", "")
    if not jira_url:
        return None

    def _check_host():
        parsed = urlparse(jira_url)
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

    try:
        with ThreadPoolExecutor(max_workers=1) as pool:
            if not pool.submit(_check_host).result(timeout=3):
                print("[Code Analyst] Sieć Comarch niedostępna — MCP pominięte")
                return None
    except (FuturesTimeout, Exception):
        print("[Code Analyst] Timeout sieci Comarch — MCP pominięte")
        return None

    try:
        from google.adk.tools.mcp_tool.mcp_toolset import (
            McpToolset,
            StdioConnectionParams,
            StdioServerParameters,
        )

        ca_cert = os.environ.get(
            "NODE_EXTRA_CA_CERTS",
            os.path.expanduser(r"~\Documents\cert\GK_COMARCH_ROOT_CA.crt"),
        )
        toolset = McpToolset(
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
        print("[Code Analyst] Comarch MCP aktywne (Jira/GitLab/Wiki)")
        return toolset
    except Exception as e:
        print(f"[Code Analyst] Comarch MCP niedostępne: {e}")
        return None


# --- Wykryj i zarejestruj dostępne MCP ---

_github_mcp = _try_github_mcp()
if _github_mcp:
    _all_tools.append(_github_mcp)
    _active_integrations.append("GitHub")
    _mcp_instruction_parts.append(
        "- **GitHub MCP** — repozytoria, issues, pull requests, code search na GitHub"
    )

_comarch_mcp = _try_comarch_mcp()
if _comarch_mcp:
    _all_tools.append(_comarch_mcp)
    _active_integrations.append("Comarch (Jira/GitLab/Wiki)")
    _mcp_instruction_parts.append(
        "- **Comarch MCP** — tickety Jira, projekty GitLab, dokumentacja Wiki/Confluence"
    )

# =============================================================================
# INSTRUKCJA AGENTA
# =============================================================================

_mcp_block = ""
if _mcp_instruction_parts:
    _mcp_block = "\n### Integracje zewnętrzne\n" + "\n".join(_mcp_instruction_parts)

_integrations_info = (
    ", ".join(_active_integrations) if _active_integrations else "brak (tylko RAG)"
)

INSTRUCTION = f"""Jesteś zaawansowanym inżynierem oprogramowania. Łączysz role analityka kodu,
architekta i senior developera. Pomagasz zespołowi analizować, naprawiać i rozwijać bazę kodu.

## Narzędzia

### Kod — RAG (semantyczne przeszukiwanie)
- **search_code(query, top_k)** — szukaj fragmentów kodu po opisie funkcjonalności
- **index_project(extensions, incremental)** — zaindeksuj/odśwież kod
- **get_index_stats()** — statystyki indeksu

### Pliki — odczyt i zapis
- **read_project_file(repo_path, file_path)** — pełna zawartość pliku (nie fragment RAG)
- **write_project_file(repo_path, file_path, content)** — utwórz/nadpisz plik
- **list_project_files(repo_path, directory, extensions)** — lista plików w katalogu

### Git — lokalne operacje (NIGDY push/merge)
- **git_status(repo_path)** — aktualny branch i zmiany
- **git_create_branch(repo_path, branch_name)** — utwórz feature branch
- **git_commit(repo_path, message, files)** — commit (Conventional Commits)
- **git_diff(repo_path, file_path)** — pokaż zmiany
- **git_log(repo_path, count)** — historia commitów
- **git_checkout_back(repo_path, branch_name)** — wróć na branch

### Build & Test
- **run_build(repo_path)** — kompilacja (auto-detect Maven/Gradle/Python)
- **run_tests(repo_path, test_filter)** — uruchom testy
{_mcp_block}

## Przepływy pracy

### ANALIZA (readonly — bez zmian w kodzie):
1. Sprawdź indeks, zaindeksuj jeśli pusty.
2. Szukaj wielokrotnie (różne zapytania).
3. Odpowiedź z dokładnymi ścieżkami i numerami linii.

### BUG FIX (branch + commit):
1. **Analiza** — search_code, znajdź root cause, przeczytaj pełne pliki (read_project_file).
2. **Branch** — git_create_branch(repo, "fix/TICKET-opis").
3. **Fix** — write_project_file z poprawionym kodem.
4. **Test regresji** — write_project_file z nowym testem pokrywającym buga.
5. **Weryfikacja** — run_build, run_tests. Jeśli FAILED → popraw i powtórz.
6. **Commit** — git_commit z "fix: opis naprawy".
7. **Podsumowanie** — co naprawione, jakie pliki, jaki test, diff.

### CR / FEATURE (branch + commit):
1. **Analiza** — search_code, zrozum obecny stan, przeczytaj pliki.
2. **Projekt** — zaplanuj zmiany, diagram Mermaid.
3. **Branch** — git_create_branch(repo, "feature/TICKET-opis").
4. **Implementacja** — write_project_file (kolejno: model → serwis → test).
5. **Weryfikacja** — run_build, run_tests. Jeśli FAILED → popraw.
6. **Commit** — git_commit z "feat: opis".
7. **Podsumowanie** — co zaimplementowane, diagram, pliki, testy.

### GENEROWANIE TESTÓW (branch + commit):
1. **Analiza** — search_code, przeczytaj klasy do pokrycia.
2. **Branch** — git_create_branch(repo, "test/opis").
3. **Testy** — write_project_file z testami.
4. **Weryfikacja** — run_tests. Jeśli FAILED → popraw.
5. **Commit** — git_commit z "test: opis".

## Domyślne konwencje (Java / Quarkus / JUnit 5)
- Testy: JUnit 5 + Mockito, nazewnictwo should_X_when_Y
- Struktura: src/main/java, src/test/java
- Build: Maven (mvn compile, mvn test)
- Commit: Conventional Commits (fix:, feat:, test:, refactor:)
- Jeśli projekt jest inny (Python, TS, itp.) — dostosuj konwencje automatycznie

## Zasady jakości (Senior Developer)
- ZAWSZE przeczytaj pełny plik przed modyfikacją (read_project_file)
- ZAWSZE uruchom build po zmianie kodu
- ZAWSZE napisz test regresji przy bug fixie
- ZAWSZE cytuj ścieżki z RAG — nie wymyślaj
- NIGDY nie commituj na main/master/develop
- NIGDY nie pushuj ani nie merguj
- Kod musi się kompilować i testy muszą przechodzić PRZED commitem
- Odpowiadaj po polsku, diagramy w Mermaid
- Aktywne integracje: {_integrations_info}
"""

# =============================================================================
# AGENT
# =============================================================================

AGENT_APP_NAME = "code_analyst_agent"

root_agent = LlmAgent(
    name=AGENT_APP_NAME,
    model="gemini-2.0-flash",
    instruction=INSTRUCTION,
    tools=_all_tools,
    description="Analizuje, naprawia i rozwija kod — RAG + Git + Build + opcjonalnie GitHub/Jira/GitLab",
)

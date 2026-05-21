"""
Konfiguracja testow E2E.

Kluczowe decyzje:
  - ENV ustawiamy PRZED importem `web.app` (Settings jest cache'owane).
  - Patchujemy `_run_agent_pipeline` / `_get_indexer` / `_get_runner`, aby
    NIGDY nie wywolac realnego LLM ani embeddingu.
  - Data-dir = tmp_path (izolacja per-sesja).
  - API key = staly testowy sekret; require_auth wlaczony.
  - Rate-limity podkrecone (tak zeby testy nie dostawaly 429).
"""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path
from typing import Any, Iterator

import pytest

# --- 1) ENV przed importem aplikacji ---------------------------------------

_TEST_API_KEY = "test-secret-abc123"


def _prepare_env(data_dir: Path) -> None:
    os.environ["CODE_ANALYST_API_KEY"] = _TEST_API_KEY
    os.environ["CODE_ANALYST_REQUIRE_AUTH"] = "true"
    os.environ["CODE_ANALYST_DATA"] = str(data_dir)
    # Rate limiting bardzo wysokie - zeby testy szly szybko
    os.environ["CODE_ANALYST_RATE_INDEX"] = "1000/minute"
    os.environ["CODE_ANALYST_RATE_SEARCH"] = "1000/minute"
    os.environ["CODE_ANALYST_RATE_WORKFLOW"] = "1000/minute"
    # Wylacz JSON logging (czytelniejsze bledy w testach)
    os.environ["CODE_ANALYST_LOG_JSON"] = "false"
    os.environ["CODE_ANALYST_LOG_LEVEL"] = "WARNING"
    # Nie dotykamy GOOGLE_CLOUD_PROJECT - /ready zwroci false; OK.


# --- 2) PYTHONPATH: modul rodzic (tak zeby `import config` dzialalo) -------

_MODULE_DIR = Path(__file__).resolve().parents[2]  # .../module_13_code_analyst
_WEB_DIR = _MODULE_DIR / "web"
for _p in (_MODULE_DIR, _WEB_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))


# --- 3) Fixtury ------------------------------------------------------------


@pytest.fixture(scope="session")
def data_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    d = tmp_path_factory.mktemp("e2e_data")
    return d


@pytest.fixture()
def sample_repo(tmp_path: Path) -> Path:
    """Minimalne, legalne repo na dysku — nowe dla kazdego testu (brak duplikatow)."""
    repo = tmp_path / "sample_repo"
    repo.mkdir()
    (repo / "main.py").write_text("print('hello')\n", encoding="utf-8")
    (repo / "README.md").write_text("# sample\n", encoding="utf-8")
    return repo


@pytest.fixture(scope="session")
def _app_module(data_dir: Path):
    """Import aplikacji z ustawionymi ENV + wstrzyknietymi mockami."""
    _prepare_env(data_dir)

    # Wyczysc ewentualne wczesniejsze importy (jesli pytest juz zaladowal)
    for name in list(sys.modules):
        if name in {"config", "web.app"} or name.startswith("web.app"):
            del sys.modules[name]

    # Wyczysc cache Settings()
    try:
        from config import get_settings  # noqa: WPS433
        get_settings.cache_clear()
    except Exception:  # noqa: BLE001
        pass

    # Import aplikacji
    from web import app as app_module  # noqa: WPS433

    # --- MOCKI: nie wolywac LLM ani embeddingu ---
    async def _fake_pipeline(runner, session_id, user_message, system_hint=None):
        return {
            "steps": [
                {"agent": "code_analyst", "action": "tool_call", "detail": "search_code(q)"},
                {"agent": "code_analyst", "action": "tool_result", "detail": "search_code -> OK"},
            ],
            "final_response": f"FAKE odpowiedz dla: {user_message[:80]}",
            "had_error": False,
        }

    async def _fake_get_runner(repo, mode):
        # Prawdziwy runner wymaga LLM - zwracamy placeholdery
        return object(), f"session-{repo.id}-{mode}"

    class _FakeIndexer:
        def __init__(self) -> None:
            self.queries: list[str] = []

        def query(self, q: str, top_k: int = 5) -> list[dict]:
            self.queries.append(q)
            return [
                {
                    "file": "main.py",
                    "score": 0.91,
                    "snippet": f"print('{q}')",
                    "start_line": 1,
                    "end_line": 1,
                },
            ]

        def index_project(self, *_a, **_kw) -> dict:
            return {
                "indexed": 2,
                "skipped": 0,
                "total_chunks": 2,
                "time_seconds": 0.01,
            }

    _fake_idx = _FakeIndexer()

    async def _fake_get_indexer(repo):
        return _fake_idx

    app_module._run_agent_pipeline = _fake_pipeline  # type: ignore[attr-defined]
    app_module._get_runner = _fake_get_runner  # type: ignore[attr-defined]
    app_module._get_indexer = _fake_get_indexer  # type: ignore[attr-defined]
    app_module._fake_indexer = _fake_idx  # pomocnicze do asercji

    return app_module


@pytest.fixture()
def app(_app_module):
    return _app_module.app


@pytest.fixture()
def client(app) -> Iterator[Any]:
    from fastapi.testclient import TestClient

    with TestClient(app) as c:
        yield c


@pytest.fixture()
def auth_headers() -> dict[str, str]:
    return {"x-api-key": _TEST_API_KEY}


@pytest.fixture()
def api_key() -> str:
    return _TEST_API_KEY


@pytest.fixture()
def added_repo(client, sample_repo, auth_headers) -> dict[str, str]:
    """Dodaje repo przez endpoint i zwraca {'id': ..., 'path': ...}."""
    # list przed
    before = _list_repos(client, auth_headers)

    resp = client.post(
        "/repos",
        data={"path": str(sample_repo), "name": "sample"},
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text

    # Odczytaj id z registry przez RepoManager (bezposrednio)
    after = _list_repos(client, auth_headers)
    new_ids = [r for r in after if r not in before]
    assert len(new_ids) == 1, f"Oczekiwano 1 nowego repo, jest {new_ids}"
    return {"id": new_ids[0], "path": str(sample_repo)}


def _list_repos(client, auth_headers) -> list[str]:
    """Zwroc ID-ki repo z dashboardu (parsujac HTML: szuka /repos/{id})."""
    import re

    r = client.get("/", headers=auth_headers)
    assert r.status_code == 200
    return list(set(re.findall(r"/repos/([a-f0-9]{8})", r.text)))

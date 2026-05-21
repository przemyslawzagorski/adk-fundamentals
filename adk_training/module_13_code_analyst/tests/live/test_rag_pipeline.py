"""
Live test: RAG end-to-end z CodeIndexer + code_retrieval_tool.

Weryfikuje:
  - CodeIndexer.index_project() buduje realny indeks na sample_project
  - Agent wywoluje search_code i dostaje trafienia semantyczne
  - Finalna odpowiedz Gemini wykorzystuje kontekst z RAG

UWAGA: koszty API Vertex AI (embeddingi + inferencja) + czas ~60s.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from code_indexer import CodeIndexer
from code_retrieval_tool import make_retrieval_tools


pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        os.environ.get("RUN_LIVE_TESTS") != "1",
        reason="Live tests wylaczone (RUN_LIVE_TESTS != 1).",
    ),
    pytest.mark.skipif(
        not os.environ.get("GOOGLE_CLOUD_PROJECT"),
        reason="Brak GOOGLE_CLOUD_PROJECT.",
    ),
]


APP_NAME = "rag_live"
USER_ID = "tester"
MODEL = os.environ.get("CODE_ANALYST_LLM_MODEL", "gemini-2.0-flash")


@pytest.fixture()
def rag_repo(tmp_path: Path) -> Path:
    """Mini repo z rozpoznawalna semantyka do testow RAG."""
    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / "auth.py").write_text(
        '"""JWT authentication module."""\n'
        "import jwt\n\n"
        "SECRET = 'not-real'\n\n"
        "def issue_token(user_id: str) -> str:\n"
        "    '''Wygeneruj token JWT dla podanego uzytkownika.'''\n"
        "    return jwt.encode({'sub': user_id}, SECRET, algorithm='HS256')\n\n"
        "def verify_token(token: str) -> dict:\n"
        "    '''Zweryfikuj JWT i zwroc payload.'''\n"
        "    return jwt.decode(token, SECRET, algorithms=['HS256'])\n",
        encoding="utf-8",
    )
    (repo / "database.py").write_text(
        '"""Warstwa dostepu do bazy danych - PostgreSQL."""\n'
        "class UserRepo:\n"
        "    '''Repozytorium uzytkownikow - CRUD na tabeli users.'''\n"
        "    def find_by_email(self, email: str): ...\n"
        "    def save(self, user): ...\n",
        encoding="utf-8",
    )
    (repo / "pricing.py").write_text(
        '"""Kalkulator cen - rabaty, VAT, promocje."""\n'
        "def calc_discount(price: float, coupon: str) -> float:\n"
        "    '''Zastosuj kod rabatowy do ceny podstawowej.'''\n"
        "    return price * 0.9 if coupon == 'SALE10' else price\n",
        encoding="utf-8",
    )
    return repo


async def test_live_rag_agent_finds_auth_module(rag_repo: Path, tmp_path: Path):
    """Pytanie o JWT powinno zwrocic fragmenty z auth.py, nie z pricing.py."""
    index_dir = tmp_path / "index"
    indexer = CodeIndexer(
        project_dir=str(rag_repo),
        persist_dir=str(index_dir),
    )
    stats = indexer.index_project()
    assert stats["indexed_files"] >= 3, f"Indexer nie wczytal plikow: {stats}"

    tools = make_retrieval_tools(indexer)
    agent = LlmAgent(
        name="rag_analyst",
        model=MODEL,
        instruction=(
            "Jestes analitykiem kodu. Aby odpowiedziec o modulach projektu, "
            "ZAWSZE najpierw uzyj narzedzia search_code. Nie zgaduj."
        ),
        tools=tools,
    )
    runner = Runner(
        agent=agent, app_name=APP_NAME,
        session_service=InMemorySessionService(),
    )
    session = await runner.session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID,
    )

    final_text = ""
    tool_calls: list[str] = []
    content = types.Content(
        role="user",
        parts=[types.Part(text="Gdzie w tym projekcie jest autoryzacja JWT? "
                              "Podaj nazwe pliku i funkcji.")],
    )
    async for ev in runner.run_async(
        user_id=USER_ID, session_id=session.id, new_message=content,
    ):
        if ev.content and ev.content.parts:
            for p in ev.content.parts:
                fc = getattr(p, "function_call", None)
                if fc is not None:
                    tool_calls.append(fc.name)
        if ev.is_final_response() and ev.content and ev.content.parts:
            final_text = "".join(
                (p.text or "") for p in ev.content.parts if hasattr(p, "text")
            ).strip()

    assert "search_code" in tool_calls, f"Agent nie uzyl RAG: {tool_calls}"
    low = final_text.lower()
    assert "auth.py" in low or "issue_token" in low or "verify_token" in low, \
        f"Agent nie znalazl autoryzacji: {final_text!r}"

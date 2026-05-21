"""
Test agentowy - prawdziwy ADK Runner + SequentialAgent + realne tooli.

LLM jest skryptowany (FakeLlm), ale:
  - Runner = prawdziwy `google.adk.runners.Runner`
  - Agent = prawdziwy `google.adk.agents.SequentialAgent`
  - Tools = prawdziwe FunctionTool-e owinietymi wokol file_tools.py
  - Pipeline = pelny: user -> LLM#1 -> tool_call -> tool_response -> LLM#1
    finalize -> LLM#2 -> tool_call -> ... -> final

Sprawdzamy:
  - agent poprawnie wywoluje tool i dostaje prawdziwy rezultat z dysku
  - SequentialAgent faktycznie przekazuje kontrole miedzy agentami
  - function_call / function_response sa rozpoznawane (zdarzenia w Runnerze)
  - zapis pliku przez agenta realnie modyfikuje dysk
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool
from google.genai import types

from file_tools import list_project_files, read_project_file, write_project_file

from tests.agent.fake_llm import FakeLlm, call, say


APP_NAME = "agent_test"
USER_ID = "tester"


# --- Pomoc: zbuduj tooli owijajac realne funkcje (repo_path = closure) ---

def _make_tools(repo_path: str) -> list[FunctionTool]:
    def read_file(file_path: str) -> dict:
        """Odczytaj plik z repo."""
        return read_project_file(repo_path, file_path)

    def list_files(pattern: str = "") -> dict:
        """Lista plikow w repo."""
        return list_project_files(repo_path, pattern or None)

    def write_file(file_path: str, content: str) -> dict:
        """Zapisz plik w repo."""
        return write_project_file(repo_path, file_path, content)

    return [
        FunctionTool(func=read_file),
        FunctionTool(func=list_files),
        FunctionTool(func=write_file),
    ]


async def _run(runner: Runner, user_text: str) -> list:
    session = await runner.session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID
    )
    events = []
    content = types.Content(role="user", parts=[types.Part(text=user_text)])
    async for event in runner.run_async(
        user_id=USER_ID, session_id=session.id, new_message=content
    ):
        events.append(event)
    return events


def _extract(events: list) -> dict:
    """Wyciagnij tool_calls, tool_responses, final_text z eventow."""
    tool_calls: list[tuple[str, str, dict]] = []   # (agent, tool, args)
    tool_responses: list[tuple[str, str, dict]] = []
    final_text = ""
    for ev in events:
        author = getattr(ev, "author", "?") or "?"
        if getattr(ev, "content", None) and ev.content.parts:
            for p in ev.content.parts:
                fc = getattr(p, "function_call", None)
                if fc is not None:
                    tool_calls.append((author, fc.name, dict(fc.args or {})))
                fr = getattr(p, "function_response", None)
                if fr is not None:
                    tool_responses.append((author, fr.name, dict(fr.response or {})))
        if ev.is_final_response() and ev.content and ev.content.parts:
            txt = "".join((p.text or "") for p in ev.content.parts if hasattr(p, "text"))
            if txt.strip():
                final_text = txt.strip()
    return {
        "tool_calls": tool_calls,
        "tool_responses": tool_responses,
        "final_text": final_text,
    }


# =============================================================================
# TESTY
# =============================================================================


@pytest.mark.asyncio
async def test_agent_should_call_real_tool_and_return_response(sample_repo: Path):
    """LLM #1 woła read_file -> realny tool czyta plik z dysku -> LLM #1 odpowiada."""
    analyst_llm = FakeLlm(
        model="fake-analyst",
        name="analyst",
        script=[
            call("read_file", file_path="main.py"),
            say("Plik main.py definiuje funkcje greet."),
        ],
    )
    architect_llm = FakeLlm(
        model="fake-architect",
        name="architect",
        script=[
            say("Rekomenduje dodac testy dla greet()."),
        ],
    )

    tools = _make_tools(str(sample_repo))
    analyst = LlmAgent(
        name="code_analyst", model=analyst_llm,
        instruction="Analityk kodu.", tools=tools,
    )
    architect = LlmAgent(
        name="solution_architect", model=architect_llm,
        instruction="Architekt.", tools=tools,
    )
    pipeline = SequentialAgent(name="pipe", sub_agents=[analyst, architect])

    runner = Runner(
        agent=pipeline, app_name=APP_NAME,
        session_service=InMemorySessionService(),
    )
    events = await _run(runner, "Przeanalizuj main.py")
    result = _extract(events)

    # --- Asercje ---
    assert ("code_analyst", "read_file", {"file_path": "main.py"}) in result["tool_calls"]
    # Realny tool zwrocil zawartosc pliku (nie mock)
    read_responses = [r for r in result["tool_responses"] if r[1] == "read_file"]
    assert read_responses, "Brak function_response dla read_file"
    payload = read_responses[0][2]
    assert payload.get("ok") is True
    assert "greet" in payload.get("content", "")
    # Oba agenty wypowiedzialy sie
    assert "Rekomenduje" in result["final_text"]


@pytest.mark.asyncio
async def test_agent_should_list_files_from_real_repo(sample_repo: Path):
    """Agent woła list_files, dostaje realna liste z dysku."""
    llm = FakeLlm(
        model="fake-analyst", name="analyst",
        script=[call("list_files"), say("Znalazlem pliki projektu.")],
    )
    agent = LlmAgent(
        name="code_analyst", model=llm,
        instruction="Analityk.", tools=_make_tools(str(sample_repo)),
    )
    runner = Runner(
        agent=agent, app_name=APP_NAME,
        session_service=InMemorySessionService(),
    )
    events = await _run(runner, "Co jest w repo?")
    result = _extract(events)

    list_responses = [r for r in result["tool_responses"] if r[1] == "list_files"]
    assert list_responses
    files = list_responses[0][2].get("files", [])
    # Lista zawiera stringi (sciezki wzgledne) lub dict-y {path: ...}
    names = {f if isinstance(f, str) else f.get("path") for f in files}
    # Znajduje realne pliki z sample_repo
    assert "main.py" in names
    assert "utils.py" in names
    assert "README.md" in names


@pytest.mark.asyncio
async def test_agent_should_write_file_to_real_disk(sample_repo: Path):
    """Agent woła write_file - plik faktycznie pojawia sie na dysku."""
    llm = FakeLlm(
        model="fake-dev", name="dev",
        script=[
            call(
                "write_file",
                file_path="new_module.py",
                content="# napisane przez agenta\nX = 42\n",
            ),
            say("Utworzylem new_module.py"),
        ],
    )
    agent = LlmAgent(
        name="senior_developer", model=llm,
        instruction="Developer.", tools=_make_tools(str(sample_repo)),
    )
    runner = Runner(
        agent=agent, app_name=APP_NAME,
        session_service=InMemorySessionService(),
    )
    events = await _run(runner, "Dodaj nowy modul.")
    result = _extract(events)

    # Tool response OK
    write_resp = [r for r in result["tool_responses"] if r[1] == "write_file"]
    assert write_resp and write_resp[0][2].get("ok") is True
    # Plik REALNIE na dysku
    new_file = sample_repo / "new_module.py"
    assert new_file.exists()
    assert "X = 42" in new_file.read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_agent_should_block_path_traversal_via_real_security(sample_repo: Path):
    """Agent probuje wyjsc poza repo - realny `safe_resolve` blokuje."""
    llm = FakeLlm(
        model="fake-analyst", name="analyst",
        script=[
            call("read_file", file_path="../../../etc/passwd"),
            say("Koniec."),
        ],
    )
    agent = LlmAgent(
        name="code_analyst", model=llm,
        instruction="Analityk.", tools=_make_tools(str(sample_repo)),
    )
    runner = Runner(
        agent=agent, app_name=APP_NAME,
        session_service=InMemorySessionService(),
    )
    events = await _run(runner, "Przeczytaj passwd")
    result = _extract(events)

    read_resp = [r for r in result["tool_responses"] if r[1] == "read_file"]
    assert read_resp, "Brak odpowiedzi toola"
    payload = read_resp[0][2]
    # Security zablokowalo - ok: False
    assert payload.get("ok") is False
    assert "content" not in payload or not payload.get("content")


@pytest.mark.asyncio
async def test_sequential_agent_should_run_sub_agents_in_order(sample_repo: Path):
    """SequentialAgent: analyst konczy tura, dopiero wtedy architect startuje."""
    analyst = FakeLlm(
        model="fake-analyst", name="analyst",
        script=[say("Analiza zrobiona.")],
    )
    architect = FakeLlm(
        model="fake-architect", name="architect",
        script=[say("Rekomendacja.")],
    )
    a1 = LlmAgent(name="code_analyst", model=analyst, instruction="A")
    a2 = LlmAgent(name="solution_architect", model=architect, instruction="B")
    pipeline = SequentialAgent(name="pipe", sub_agents=[a1, a2])

    runner = Runner(
        agent=pipeline, app_name=APP_NAME,
        session_service=InMemorySessionService(),
    )
    events = await _run(runner, "Start")

    # Kolejnosc autorow finalnych wypowiedzi
    authors_order: list[str] = []
    for ev in events:
        if ev.is_final_response() and ev.content and ev.content.parts:
            if any((p.text or "").strip() for p in ev.content.parts if hasattr(p, "text")):
                authors_order.append(getattr(ev, "author", "?"))
    # Analyst przed architect
    assert authors_order == ["code_analyst", "solution_architect"], authors_order


@pytest.mark.asyncio
async def test_agent_multi_turn_tool_then_final_answer(sample_repo: Path):
    """LLM robi dwa kroki: najpierw list, potem read, potem finalny tekst.

    Weryfikuje ze Runner prawidlowo wywoluje LLM wielokrotnie w obrebie jednej
    tury agenta (pomiedzy function_call i function_response).
    """
    llm = FakeLlm(
        model="fake-analyst", name="analyst",
        script=[
            call("list_files"),
            call("read_file", file_path="utils.py"),
            say("utils.py zawiera funkcje add()."),
        ],
    )
    agent = LlmAgent(
        name="code_analyst", model=llm,
        instruction="Analityk.", tools=_make_tools(str(sample_repo)),
    )
    runner = Runner(
        agent=agent, app_name=APP_NAME,
        session_service=InMemorySessionService(),
    )
    events = await _run(runner, "Co robi utils?")
    result = _extract(events)

    tool_names = [t[1] for t in result["tool_calls"]]
    assert tool_names == ["list_files", "read_file"], tool_names
    assert "add()" in result["final_text"]
    # Trzy wywolania LLM (list -> read -> final) + initial prompt
    assert len(llm.calls_log) >= 3

"""Agent-level test E2E dla spec_generator (bez prawdziwego Gemini).

Uzywamy FakeLlm (z module_13) jako modelu dla kazdego sub-agenta. Skryptujemy
kompletna sciezke:

  ticket_fetcher   -> say(ticket summary)
  noop_context     -> say("BRAK ZEWNETRZNEGO KONTEKSTU")
  hld_writer       -> say(pierwsza wersja HLD)
  critique_loop iter 1:
    critic         -> say("ZMIANY WYMAGANE: dodaj NFR")
    escalation     -> no escalate
    reviser        -> say(poprawione HLD)
  critique_loop iter 2:
    critic         -> say("LGTM")
    escalation     -> escalate=True -> loop stop
  epic_decomposer  -> say(JSON z 2 epikami)

Asercje:
  - state.ticket, state.wiki_context, state.current_hld, state.epics_json sa zapisane
  - finalne state.epics_json parsuje sie jako JSON z >=1 epikiem
  - loop wyszedl po LGTM (reviser wywolany tylko raz)
  - calkowita liczba "say" zgadza sie ze skryptem
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

# Dolacz oba module paths: 22 (konfig) + 13 (FakeLlm)
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT.parent / "module_13_code_analyst" / "tests"))

# Upewniamy sie ze settings dzialaja bez MCP/NotebookLM
for k in ["COMARCH_MCP_JIRA_URL", "COMARCH_MCP_JIRA_TOKEN", "NOTEBOOKLM_ENABLED"]:
    os.environ.pop(k, None)

from google.adk.runners import Runner  # noqa: E402
from google.adk.sessions import InMemorySessionService  # noqa: E402
from google.genai import types  # noqa: E402

from agent.fake_llm import FakeLlm, say  # noqa: E402  (z module_13)
from agents.spec_generator import build_spec_generator  # noqa: E402


FAKE_TICKET = (
    "Ticket: SWOK-7777 (High)\nTytul: Dodaj endpoint raportu rocznego\n"
    "Opis: Nowy endpoint POST /api/reports/yearly generujacy PDF z danymi za rok.\n"
)

FAKE_HLD_V1 = (
    "# HLD: SWOK-7777\n\n## 1. Cel biznesowy\nEndpoint raportu rocznego.\n"
    "## 2. Scope\n### In scope\n- POST /api/reports/yearly\n## 3. Architektura rozwiazania\n"
    "## 8. Security & Compliance\nBrak zmian.\n## 10. Ryzyka\nBrak.\n"
)

FAKE_HLD_V2 = (
    FAKE_HLD_V1
    + "\n## 9. Niefunkcjonalne\n- Wydajnosc: p95 < 2s\n- Skalowanie: horizontal\n"
)

FAKE_EPICS_JSON = json.dumps({
    "epics": [
        {
            "title": "Model danych raportu rocznego",
            "summary": "Schema + migracja.",
            "acceptance_criteria": [
                "Given brak tabeli, when migracja, then tabela yearly_reports powstaje.",
            ],
            "priority": "High",
            "labels": ["backend", "data"],
            "estimated_story_points": 5,
            "dependencies": [],
        },
        {
            "title": "Endpoint POST /api/reports/yearly",
            "summary": "Generowanie PDF.",
            "acceptance_criteria": [
                "Given user z rola REPORTER, when POST /api/reports/yearly, then zwraca 200 + PDF.",
            ],
            "priority": "High",
            "labels": ["backend", "api"],
            "estimated_story_points": 8,
            "dependencies": ["Model danych raportu rocznego"],
        },
    ]
})


async def test_spec_generator_e2e_with_fake_llm():
    overrides = {
        "ticket_fetcher": FakeLlm(model="fake-ticket-fetcher", name="fake-ticket-fetcher", script=[say(FAKE_TICKET)]),
        "context":        FakeLlm(model="fake-context",        name="fake-context",        script=[say("BRAK ZEWNETRZNEGO KONTEKSTU")]),
        "hld_writer":     FakeLlm(model="fake-hld-writer",     name="fake-hld-writer",     script=[say(FAKE_HLD_V1)]),
        "critic":         FakeLlm(model="fake-critic",         name="fake-critic",         script=[
            say("ZMIANY WYMAGANE:\n1. brak sekcji NFR (9)"),
            say("LGTM"),
        ]),
        "reviser":        FakeLlm(model="fake-reviser",        name="fake-reviser",        script=[say(FAKE_HLD_V2)]),
        "epic_decomposer":FakeLlm(model="fake-epic-decomposer",name="fake-epic-decomposer",script=[say(FAKE_EPICS_JSON)]),
    }

    agent = build_spec_generator(
        max_critique_iterations=5,
        model_overrides=overrides,
    )

    session_service = InMemorySessionService()
    runner = Runner(
        agent=agent, app_name="spec_gen_test",
        session_service=session_service,
    )
    session = await session_service.create_session(
        app_name="spec_gen_test", user_id="tester",
    )

    events = []
    content = types.Content(
        role="user",
        parts=[types.Part(text="Wygeneruj HLD i epiki dla SWOK-7777")],
    )
    async for ev in runner.run_async(
        user_id="tester", session_id=session.id, new_message=content,
    ):
        events.append(ev)

    final_session = await session_service.get_session(
        app_name="spec_gen_test", user_id="tester", session_id=session.id,
    )
    state = final_session.state

    # Kluczowe pola stanu
    assert state.get("ticket"), "ticket_fetcher nie zapisal state.ticket"
    assert "SWOK-7777" in state["ticket"]
    # context_parallel z noop_context zapisuje wiki_context
    assert state.get("wiki_context") == "BRAK ZEWNETRZNEGO KONTEKSTU"
    # HLD po krytyce powinien byc v2 (po reviserze)
    assert state.get("current_hld", "").strip()
    assert "Niefunkcjonalne" in state["current_hld"], \
        f"Reviser nie zaaktualizowal HLD: {state.get('current_hld')!r}"
    # critic ostatni feedback to LGTM
    assert state.get("critic_feedback", "").strip().upper().startswith("LGTM")
    # Epiki
    epics_raw = state.get("epics_json")
    assert epics_raw, "Brak epics_json w state"
    epics_data = json.loads(epics_raw)
    assert "epics" in epics_data and len(epics_data["epics"]) == 2
    assert epics_data["epics"][0]["priority"] == "High"

    # Sanity: FakeLlm reviser wywolany DOKLADNIE 1 raz (iter 2 nie dojdzie
    # bo escalation stopnie loop po LGTM od critica)
    reviser_llm: FakeLlm = overrides["reviser"]
    assert len(reviser_llm.calls_log) == 1, \
        f"Reviser wywolany nieoczekiwana liczbe razy: {len(reviser_llm.calls_log)}"

    # Critic wywolany 2 razy (ZMIANY + LGTM)
    critic_llm: FakeLlm = overrides["critic"]
    assert len(critic_llm.calls_log) == 2, \
        f"Critic wywolany nieoczekiwana liczbe razy: {len(critic_llm.calls_log)}"

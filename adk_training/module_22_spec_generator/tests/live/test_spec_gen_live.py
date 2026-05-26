"""Live test Spec Generator - realne Gemini, BEZ MCP.

Weryfikuje:
  - Pelny SequentialAgent (ticket_fetcher -> context -> hld_writer -> critique_loop -> epic_decomposer)
    uruchamia sie przez Runner z realnym modelem.
  - Stan sesji zawiera `current_hld` (HLD markdown) i `epics_json` (JSON string).
  - HLD zawiera kluczowe sekcje (Cel biznesowy, Security, Ryzyka).
  - epics_json parsuje sie do listy z min. 1 epikiem majacym `title` + `acceptance_criteria`.

GATING:
  RUN_LIVE_TESTS=1 + GOOGLE_CLOUD_PROJECT ustawione. Bez ADC / projektu - skip.
  MCP nie jest wymagany - ticket_fetcher uzyje fallbacku (no-op z instrukcja promptu).

UWAGA: koszt API (3-6 wywolan Gemini). Domyslnie wylaczone.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.spec_generator import build_spec_generator, parse_epics_json  # noqa: E402


pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        os.environ.get("RUN_LIVE_TESTS") != "1",
        reason="Live tests wylaczone (ustaw RUN_LIVE_TESTS=1).",
    ),
    pytest.mark.skipif(
        not os.environ.get("GOOGLE_CLOUD_PROJECT"),
        reason="Brak GOOGLE_CLOUD_PROJECT.",
    ),
]


@pytest.mark.asyncio
async def test_spec_generator_live_produces_hld_and_epics():
    """E2E: realny Gemini generuje HLD + epiki dla syntetycznego ticketu."""
    agent = build_spec_generator(
        enable_notebooklm=False,
        max_critique_iterations=2,  # ograniczamy koszty
    )
    runner = Runner(
        agent=agent,
        app_name="spec_gen_live",
        session_service=InMemorySessionService(),
    )
    session = await runner.session_service.create_session(
        app_name="spec_gen_live", user_id="tester",
    )

    # Prosty issue_key - bez MCP ticket_fetcher zwroci komunikat o niedostepnosci,
    # ale HLD writer i tak wygeneruje szkic na podstawie instrukcji (test elastycznosci).
    content = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text="SWOK-LIVE-1: Dodaj endpoint /api/v1/report zwracajacy raport JSON.")],
    )
    async for _ev in runner.run_async(
        user_id="tester", session_id=session.id, new_message=content,
    ):
        pass

    final = await runner.session_service.get_session(
        app_name="spec_gen_live", user_id="tester", session_id=session.id,
    )
    assert final is not None
    state = final.state

    # 1. HLD powinien istniec i miec kluczowe sekcje
    hld = str(state.get("current_hld") or "").lower()
    assert hld, f"Brak current_hld w state: keys={list(state.keys())}"
    assert "cel biznesowy" in hld, f"HLD bez sekcji 'Cel biznesowy':\n{hld[:500]}"
    # Ryzyka / Security - jedna z nich powinna sie pojawic
    assert ("security" in hld) or ("ryzyka" in hld), \
        f"HLD bez sekcji Security/Ryzyka:\n{hld[:500]}"

    # 2. Krytyk powinien zakonczyc petle (feedback == LGTM lub zaczyna sie od LGTM)
    feedback = str(state.get("critic_feedback") or "").strip()
    # Nie twardo LGTM - po 2 iteracjach moze byc dalej ZMIANY WYMAGANE; logujemy tylko
    assert feedback, "Brak critic_feedback - petla krytyki nie wystartowala"

    # 3. Epics JSON powinien sie sparsowac do niepustej listy
    epics_raw = state.get("epics_json")
    assert epics_raw, "Brak epics_json w state"
    epics = parse_epics_json(epics_raw)
    assert isinstance(epics, list) and len(epics) >= 1, \
        f"Oczekiwano listy epikow, dostano raw={epics_raw[:300]!r} parsed={epics!r}"

    first = epics[0]
    assert "title" in first, f"Epik bez title: {first}"
    assert "acceptance_criteria" in first, f"Epik bez acceptance_criteria: {first}"
    assert isinstance(first["acceptance_criteria"], list), "acceptance_criteria musi byc lista"

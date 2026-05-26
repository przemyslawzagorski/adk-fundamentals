"""
Module 28 — ADK v2: Human Input (Human-in-the-Loop z RequestInput)
===================================================================

PRAWDZIWE ADK v2 API — HITL przez RequestInput:
  Nie ma już BaseAgent z _run_async_impl dla HITL.
  HITL = prosta funkcja yielding RequestInput(message="...")

  WZORZEC:
    from google.adk.events import RequestInput

    def request_approval(draft: str):
        yield RequestInput(
            message=f"Zatwierdź plan lub podaj uwagi:\\n\\n{draft}"
        )
        # ← ADK runner ZATRZYMUJE się tutaj
        # ← Użytkownik widzi pytanie w Web UI
        # ← Po odpowiedzi użytkownika runner wraca z node_input = odpowiedź

    def handle_approval(node_input: str):
        if node_input.lower() == "approve":
            yield Event(route="approved")
        elif node_input.lower() == "reject":
            yield Event(route="rejected")
        else:
            # Dowolna inna odpowiedź = feedback → pętla
            yield Event(route="revise", state={"feedback": node_input})

  PĘTLA REWIZJI (approve/reject/revise):
    edges=[
        ("START", init, draft_agent, request_approval, handle_approval),
        (handle_approval, {
            "revise":    draft_agent,   # ← PĘTLA: wróć do draftu z feedbackiem
            "approved":  execute_agent,
            "rejected":  abort_agent,
        }),
    ]

  DLACZEGO TO LEPSZE niż BaseAgent HITL:
    ✅ Nie wymaga klasy — zwykła funkcja
    ✅ ADK runner zarządza stanem wstrzymania (suspend/resume)
    ✅ Testowalne: wywołaj funkcję, sprawdź yielded events
    ✅ Natywna integracja z ADK Web UI (wyświetla input box)

PRZYKŁAD PRODUKCYJNY (Module 24 AuditOps — DisclaimerAck):
  Pentest pipeline: plan → human review → approve/revise/reject → execute/abort

TODO dla dewelopera:
  [ ] Zamień runtime_guard() z Module 24 safety.py na request_approval() + handle_approval()
  [ ] Dodaj RequestInput z choices=["approve", "reject"] dla prostszego UX
  [ ] Przetestuj pętlę: wyślij "dodaj test SQL injection" jako feedback
  [ ] Dodaj timeout (ADK API): RequestInput(message="...", timeout_seconds=300)
  [ ] Zintegruj z Slack przez webhook: RequestInput emituje notyfikację
  [ ] Dodaj audit log: każda odpowiedź persystowana do zewnętrznego systemu
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from google.adk import Agent, Event, Workflow
from google.adk.events import RequestInput

load_dotenv()
MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")


# =============================================================================
# WĘZEŁ 1 (FUNKCJA): Inicjalizacja state
# =============================================================================

def init_pentest(node_input: str):
    """Inicjuje state: cel pentestów i pusty feedback."""
    yield Event(state={"pentest_request": node_input, "feedback": ""})


# =============================================================================
# WĘZEŁ 2 (AGENT): Planning — generuje plan wymagający akceptacji
# =============================================================================

pentest_planner = Agent(
    name="pentest_planner",
    model=MODEL,
    instruction="""Planujesz pentest dla celu opisanego w żądaniu.

Żądanie: "{pentest_request}"
Feedback z poprzedniej iteracji (uwzględnij!): "{feedback?}"

Wygeneruj plan testów JSON:
{{
  "target": "...",
  "scan_type": "auto|guided",
  "estimated_duration_minutes": 15,
  "risk_impact": "HIGH|MEDIUM|LOW",
  "scenarios": [{{"id": "...", "name": "...", "owasp": "Axx:2021"}}],
  "destructive_tests": true/false
}}

TYLKO JSON.""",
    output_key="pentest_plan",
)


# =============================================================================
# WĘZEŁ 3 (FUNKCJA): RequestInput — PRAWDZIWY HITL CHECKPOINT
# =============================================================================

def request_human_review(pentest_plan: str):
    """
    HITL: zatrzymuje pipeline i czeka na decyzję człowieka.

    ADK runner WSTRZYMUJE się przy yield RequestInput(...)
    Użytkownik widzi message w Web UI i wpisuje odpowiedź.
    Po odpowiedzi runner wraca z node_input = tekst odpowiedzi.

    Akceptowane odpowiedzi:
    - "approve" → uruchom pentest
    - "reject"  → anuluj
    - cokolwiek innego → feedback do rewizji planu
    """
    yield RequestInput(
        message=(
            "📋 **Pentest Plan wymaga Twojej akceptacji:**\n\n"
            f"{pentest_plan}\n\n"
            "---\n"
            "Odpowiedz:\n"
            "• `approve` — zatwierdź i uruchom\n"
            "• `reject` — anuluj\n"
            "• Dowolny tekst — feedback do rewizji planu"
        ),
    )


# =============================================================================
# WĘZEŁ 4 (FUNKCJA): Router po decyzji człowieka
# =============================================================================

def handle_human_decision(node_input: str):
    """
    Routuje na podstawie odpowiedzi człowieka (czysty Python — testowalny!).
    node_input = dokładnie to co wpisał użytkownik po RequestInput.
    """
    decision = node_input.strip().lower()
    if decision == "approve":
        yield Event(route="approved", state={"human_decision": "APPROVED"})
    elif decision == "reject":
        yield Event(route="rejected", state={"human_decision": "REJECTED"})
    else:
        # Feedback → wróć do planera z uwagami (PĘTLA)
        yield Event(
            route="revise",
            state={"feedback": node_input, "human_decision": "REVISE"},
        )


# =============================================================================
# GAŁĄŹ APPROVED: Wykonanie pentestów
# =============================================================================

execution_agent = Agent(
    name="pentest_executor",
    model=MODEL,
    instruction="""Wykonujesz zatwierdzony plan pentestów.

Plan: "{pentest_plan}"
Zatwierdzono: {human_decision}

Symuluj wykonanie i zwróć wyniki JSON:
{{
  "executed_scenarios": ["..."],
  "findings": [{{"severity": "...", "description": "..."}}],
  "execution_time_minutes": 15,
  "status": "completed"
}}""",
    output_key="execution_result",
)


# =============================================================================
# GAŁĄŹ REJECTED: Dokumentacja odrzucenia
# =============================================================================

def handle_rejection():
    """Dokumentuje odrzucenie — prosta funkcja zamiast LlmAgent."""
    yield Event(
        message="❌ Pentest odrzucony przez operatora. Plan zarchiwizowany.",
        state={"execution_result": {"status": "REJECTED", "archived": True}},
    )


# =============================================================================
# WĘZEŁ KOŃCOWY: Finalny raport (wspólny dla approved + rejected)
# =============================================================================

final_reporter = Agent(
    name="hitl_reporter",
    model=MODEL,
    instruction="""Generujesz finalny raport HITL pentestów.

Plan: "{pentest_plan}"
Decyzja: "{human_decision}"
Wynik: "{execution_result?}"

## HITL Pentest Report
**Decision**: {human_decision}
**Outcome**: (sukces/odrzucenie/błąd)
**Key Findings**: (jeśli wykonano)
**Next Steps**: (konkretne działania)
**Compliance Note**: Pentest przeszedł przez HITL checkpoint — zgodność zapewniona.""",
)


# =============================================================================
# ROOT AGENT — Workflow z HITL + pętlą rewizji
# =============================================================================
# Graf (z pętlą!):
#                               ┌──────────────────────┐
#                               ↓                      │ route="revise"
#   START → init → plan → request_review → handle ────┤
#                                                      │ route="approved" → execute → report
#                                                      └ route="rejected" → abort   → report

root_agent = Workflow(
    name="root_agent",
    edges=[
        # Sekwencja do HITL checkpoint:
        (
            "START",
            init_pentest,
            pentest_planner,
            request_human_review,   # ← ZATRZYMUJE się tu i czeka na input
            handle_human_decision,  # ← routuje na podstawie odpowiedzi
        ),
        # Rozgałęzienie po decyzji HITL:
        (handle_human_decision, {
            "revise":   pentest_planner,    # ← PĘTLA z feedbackiem
            "approved": execution_agent,
            "rejected": handle_rejection,
        }),
        # Obie gałęzie finalizują się w raporcie:
        (execution_agent,  final_reporter),
        (handle_rejection, final_reporter),
    ],
)

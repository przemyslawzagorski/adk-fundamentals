"""
Module 24 — AuditOps: Autonomous Web Pentest (ADK v2)
======================================================

MODERNIZACJA ADK v2: linear async functions → Workflow + RequestInput HITL.

PRZED (ADK1):
  auto_pentest() — liniowa funkcja async: recon → plan → execute → report
  runtime_guard() — guard clause (nie czeka na input, rzuca wyjątek)

PO (ADK v2):
  Workflow(edges=[...]) z HITL przez RequestInput i routing po severity:

  START → init → recon_agent → planning_agent
       → HITL (RequestInput: "Czy zatwierdzasz pentest?")
       → approval_route:
         ├── "approve" → execute_agent
         │              → severity_route:
         │                ├── "critical" → escalation_agent
         │                └── "normal"   → report_agent
         └── "reject"  → abort_agent

KLUCZOWE KORZYŚCI:
  - HITL: każda decyzja o teście jest logowana z timestamp + user_id
  - Severity routing: CRITICAL findings → natychmiastowa eskalacja (Slack/PagerDuty)
  - Każda faza w session.state → pełna observability w ADK Web UI
  - pentest_agent.py i playwright_runner.py BEZ ZMIAN — wrapper jako FunctionTool

TODO dla dewelopera:
  [ ] Podłącz prawdziwy Playwright: zamień mock_recon/mock_execute na import z recon.py
  [ ] Dodaj Slack webhook w escalation_agent (gdy CRITICAL)
  [ ] Zintegruj audit log: zapisuj każdą decyzję HITL do ack_store.py
  [ ] Przetestuj ścieżkę REJECT (ack nie jest potrzebne — HITL ją zastępuje)
  [ ] Dodaj timeout na HITL: jeśli brak odpowiedzi w 5 min → auto-reject
"""

from __future__ import annotations

import json
import os
from typing import Literal

from dotenv import load_dotenv
from google.adk import Agent, Event, Workflow
from google.adk.events import RequestInput
from pydantic import BaseModel, Field

load_dotenv()
MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")


# =============================================================================
# PYDANTIC SCHEMAS
# =============================================================================

class ReconResult(BaseModel):
    """Wynik rekonesansu — wejście dla planisty."""
    target_url: str
    technologies: list[str] = Field(default_factory=list)
    interesting_paths: list[str] = Field(default_factory=list)
    forms_count: int = 0
    summary: str = ""


class PentestPlan(BaseModel):
    """Plan testu — wynik planisty, wejście dla executora."""
    target_url: str
    scenarios: list[dict] = Field(default_factory=list)
    scenario_count: int = 0
    risk_estimate: Literal["low", "medium", "high", "critical"] = "medium"


class ExecutionResult(BaseModel):
    """Wyniki wykonania scenariuszy testowych."""
    run_id: str
    target_url: str
    findings: list[dict] = Field(default_factory=list)
    findings_count: int = 0
    max_severity: Literal["none", "low", "medium", "high", "critical"] = "none"
    duration_s: float = 0.0
    scenarios_run: int = 0


# =============================================================================
# MOCK TOOLS — zastąp prawdziwymi importami z recon.py / playwright_runner.py
# =============================================================================

def run_passive_recon(target_url: str) -> str:
    """
    Wykonuje pasywny rekonesans celu.
    TODO: Zastąp: from .recon import passive_recon; asyncio.run(passive_recon(target_url, cfg))

    Args:
        target_url: URL celu (musi być HTTP/HTTPS)
    Returns:
        JSON z wynikami rekonesansu (ReconResult)
    """
    result = ReconResult(
        target_url=target_url,
        technologies=["nginx", "React", "PostgreSQL"],
        interesting_paths=["/admin", "/api/", "/login", "/.env"],
        forms_count=3,
        summary=(
            f"Cel {target_url}: wykryto React SPA z backendem Python/nginx. "
            "Znaleziono panel administracyjny (/admin) i 3 formularze. "
            "Brak nagłówka X-Frame-Options. RISK: MEDIUM."
        ),
    )
    return result.model_dump_json()


def build_pentest_scenarios(target_url: str, recon_json: str, max_scenarios: int = 5) -> str:
    """
    Buduje listę scenariuszy testowych na podstawie rekonesansu.
    TODO: Zastąp: from .attack_library import build_default_pack; pack = build_default_pack(url, recon, max_count)

    Args:
        target_url: URL celu
        recon_json: Wynik run_passive_recon() jako JSON
        max_scenarios: Maksymalna liczba scenariuszy
    Returns:
        JSON z PentestPlan
    """
    plan = PentestPlan(
        target_url=target_url,
        scenarios=[
            {"id": "sql-login", "name": "SQL Injection na formularzu login", "severity": "high"},
            {"id": "xss-search", "name": "XSS w polu wyszukiwania", "severity": "medium"},
            {"id": "admin-bypass", "name": "Bypass panelu admin (IDOR)", "severity": "critical"},
        ][:max_scenarios],
        scenario_count=3,
        risk_estimate="high",
    )
    return plan.model_dump_json()


def execute_pentest_scenarios(target_url: str, plan_json: str) -> str:
    """
    Uruchamia scenariusze testowe przez Playwright.
    TODO: Zastąp: from .pentest_agent import auto_pentest; asyncio.run(auto_pentest(target_url, cfg, ack))

    Args:
        target_url: URL celu
        plan_json: Wynik build_pentest_scenarios() jako JSON
    Returns:
        JSON z ExecutionResult (findings, severity, duration)
    """
    result = ExecutionResult(
        run_id=f"run_{os.urandom(4).hex()}",
        target_url=target_url,
        findings=[
            {"title": "SQL Injection w /login", "severity": "high", "owasp": "A03:2021"},
            {"title": "XSS reflected w ?q=", "severity": "medium", "owasp": "A03:2021"},
        ],
        findings_count=2,
        max_severity="high",
        duration_s=45.3,
        scenarios_run=3,
    )
    return result.model_dump_json()


# =============================================================================
# WĘZŁY GRAFU
# =============================================================================

def init_audit(node_input: str):
    """Parsuje żądanie użytkownika i inicjuje state audytu."""
    # Prosta heurystyka: szukaj URL w tekście
    import re
    urls = re.findall(r'https?://[^\s"\']+', node_input)
    target_url = urls[0] if urls else node_input.strip()
    yield Event(state={
        "target_url": target_url,
        "audit_mode": "auto",
        "user_request": node_input,
    })


recon_agent = Agent(
    name="recon_agent",
    model=MODEL,
    instruction="""Wykonujesz pasywny rekonesans celu bezpieczeństwa.

URL celu: "{target_url}"

Wywołaj run_passive_recon(target_url="{target_url}") i przeanalizuj wyniki:
1. Jakie technologie wykryto?
2. Które ścieżki są interesujące z punktu widzenia security?
3. Jakie formularze znaleziono?

Zapisz wynik jako JSON.""",
    tools=[run_passive_recon],
    output_key="recon_result",
)

planning_agent = Agent(
    name="planning_agent",
    model=MODEL,
    instruction="""Budujesz plan testów penetracyjnych na podstawie rekonesansu.

WYNIKI REKON: "{recon_result}"
CEL: "{target_url}"

Wywołaj build_pentest_scenarios(target_url="{target_url}", recon_json="{recon_result}")
i przeanalizuj scenariusze:
1. Które scenariusze mają najwyższy priorytet?
2. Jaki jest szacowany poziom ryzyka?
3. Które OWASP kategorie są objęte?

Podsumuj plan w 3-5 zdaniach.""",
    tools=[build_pentest_scenarios],
    output_key="pentest_plan",
)


def request_human_approval(node_input: str):
    """
    HITL — czeka na decyzję człowieka przed uruchomieniem aktywnych testów.

    To jest kluczowy węzeł ADK v2 zastępujący runtime_guard():
    - ADK1: runtime_guard() rzucał wyjątek jeśli brak ack → brak audit logu
    - ADK2: RequestInput → zatrzymuje workflow, czeka na input, loguje decyzję
    """
    plan_summary = node_input or "Plan testów gotowy"
    yield RequestInput(
        message=(
            f"⚠️  PENTEST APPROVAL REQUIRED\n\n"
            f"Plan testu: {plan_summary[:300]}\n\n"
            f"Potwierdzam, że:\n"
            f"1. Mam pisemną autoryzację właściciela systemu\n"
            f"2. Akceptuję pełną odpowiedzialność prawną za ten test\n"
            f"3. URL docelowy jest w autoryzowanym zakresie\n\n"
            f"Wpisz 'APPROVE' aby uruchomić test, lub 'REJECT' aby anulować:"
        )
    )


def route_approval(node_input: str):
    """Router: kieruje do wykonania (approve) lub anulowania (reject)."""
    decision = (node_input or "").strip().upper()
    if decision.startswith("APPROVE"):
        yield Event(
            route="approve",
            state={"approval_decision": "approved", "approved_by": "human"},
        )
    else:
        yield Event(
            route="reject",
            state={"approval_decision": "rejected", "rejection_reason": node_input},
        )


execute_agent = Agent(
    name="execute_agent",
    model=MODEL,
    instruction="""Uruchamiasz zatwierdzone scenariusze testów penetracyjnych.

PLAN: "{pentest_plan}"
CEL: "{target_url}"

Wywołaj execute_pentest_scenarios(target_url="{target_url}", plan_json="{pentest_plan}")
i przeanalizuj wyniki:
1. Ile findings zostało znalezionych?
2. Jaki jest maksymalny severity?
3. Które scenariusze przeszły, a które nie?""",
    tools=[execute_pentest_scenarios],
    output_key="execution_result",
)


def route_severity(node_input: str):
    """Router po severity: CRITICAL → eskalacja, pozostałe → raport."""
    try:
        data = json.loads(node_input) if node_input else {}
        max_sev = data.get("max_severity", "none")
    except (json.JSONDecodeError, AttributeError):
        max_sev = "none"

    if max_sev == "critical":
        yield Event(route="critical", state={"severity_route": "critical"})
    else:
        yield Event(route="normal", state={"severity_route": "normal"})


def abort_pentest():
    """Węzeł końcowy dla odrzuconego audytu."""
    yield Event(message=(
        "❌ Pentest odrzucony.\n\n"
        "Test bezpieczeństwa został anulowany na etapie zatwierdzania. "
        "Decyzja i powód zostały zalogowane. "
        "Skontaktuj się z właścicielem systemu aby uzyskać autoryzację."
    ))


escalation_agent = Agent(
    name="escalation_agent",
    model=MODEL,
    instruction="""Generujesz raport KRYTYCZNY wymagający natychmiastowej eskalacji.

WYNIKI WYKONANIA: "{execution_result}"
CEL: "{target_url}"

‼️ CRITICAL SEVERITY FINDINGS DETECTED ‼️

Wygeneruj raport eskalacyjny:

## 🚨 CRITICAL SECURITY ALERT

**System**: {target_url}
**Severity**: CRITICAL
**Wymaga natychmiastowego działania**: TAK

### Krytyczne podatności
(lista findings z severity=critical)

### Natychmiastowe działania (następne 2h)
1. ...

### Osoby do powiadomienia
- Security team
- CTO/CISO
- System owner

### Tymczasowe mitigacje
(co zrobić TERAZ zanim podatność zostanie naprawiona)

TODO: Podłącz Slack webhook / PagerDuty dla automatycznej eskalacji.""",
)

report_agent = Agent(
    name="report_agent",
    model=MODEL,
    instruction="""Generujesz końcowy raport z testu penetracyjnego.

REKONESANS: "{recon_result}"
PLAN: "{pentest_plan}"
WYNIKI: "{execution_result}"
CEL: "{target_url}"

## Security Audit Report

**System**: {target_url}
**Status**: Completed
**Decyzja zatwierdzenia**: {approval_decision}

### Executive Summary
(2-3 zdania dla zarządu)

### Findings by Severity
| Severity | Count | Examples |
|----------|-------|---------|
| Critical | ...   | ...     |
| High     | ...   | ...     |
| Medium   | ...   | ...     |

### OWASP Coverage
(które kategorie zostały przetestowane)

### Recommendations
(priorytetyzowane akcje naprawcze)

### Next Steps
(co i kiedy naprawić)""",
)


# =============================================================================
# ROOT AGENT — Workflow z HITL i severity routing
# =============================================================================
#
# Graf:
#   START → init → recon → planning → HITL → approval_route
#           ↓ approve: execute → severity_route
#                              ↓ critical: escalation
#                              ↓ normal: report
#           ↓ reject: abort
#

root_agent = Workflow(
    name="root_agent",
    edges=[
        # Faza 1: przygotowanie (deterministyczna sekwencja)
        ("START", init_audit, recon_agent, planning_agent),

        # Faza 2: HITL — workflow zatrzymuje się i czeka na input człowieka
        (planning_agent, request_human_approval),

        # Faza 3: routing po decyzji człowieka
        (request_human_approval, route_approval),
        (route_approval, {"approve": execute_agent, "reject": abort_pentest}),

        # Faza 4: severity routing (tylko po approve)
        (execute_agent, route_severity),
        (route_severity, {"critical": escalation_agent, "normal": report_agent}),
    ],
)

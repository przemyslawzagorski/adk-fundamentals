"""
Module 26 — ADK v2: Graph Routes (Warunkowe Rozgałęzienia Grafu)
================================================================

PRAWDZIWE ADK v2 API — Graph Routes:
  Nie ma już BaseAgent z _run_async_impl dla routingu.
  Routing = zwykła funkcja Pythona yielding Event(route="nazwa_gałęzi")

  WZORZEC ROUTINGU:
    def my_router(node_input: MySchema):  # input = wynik poprzedniego węzła
        if node_input.risk == "high":
            yield Event(route="deep")
        else:
            yield Event(route="fast")

    root_agent = Workflow(
        name="...",
        edges=[
            ("START", assess_risk, my_router),
            (my_router, {
                "deep":  deep_scan_agent,   # ← gałąź HIGH
                "fast":  fast_scan_agent,   # ← gałąź LOW/MEDIUM
                "error": error_handler,     # ← gałąź awarii
            }),
            # Obie gałęzie zbiegają się w audit_reporter:
            (deep_scan_agent, audit_reporter),
            (fast_scan_agent, audit_reporter),
            (error_handler,   audit_reporter),
        ],
    )

  STRUCTURED OUTPUT (output_schema):
    Agent zwracający pydantic model → router może go typowo odbierać
    jako argument. Eliminuje parsowanie JSON ze stringa.

  KLUCZOWA LEKCJA:
    Router to FUNKCJA PYTHONA — testowalny bez mockowania LLM:
    assert list(my_router(RiskLevel(risk="high")))[0].route == "deep"

PRZYKŁAD PRODUKCYJNY (Module 24 — AuditOps):
  auto_pentest vs guided_pentest jako dwie gałęzie grafu.
  Decyzja przez risk_level z output_schema agenta recon.

TODO dla dewelopera:
  [ ] Dodaj gałąź "critical" → natychmiastowy alert + eskalacja do eksperta
  [ ] Napisz pytest dla route_by_risk — test bez LLM (czysta funkcja)
  [ ] Zintegruj playwright_runner z Module 24 jako tool w deep_scan_agent
  [ ] Dodaj Event(state={"scan_mode": "deep"}) w router dla observability
  [ ] Przetestuj co się dzieje gdy scanner wyrzuci wyjątek (error path)
"""

from __future__ import annotations

import os
from typing import Literal

from dotenv import load_dotenv
from google.adk import Agent, Event, Workflow
from pydantic import BaseModel, Field

load_dotenv()
MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")


# =============================================================================
# STRUCTURED OUTPUT — pydantic model dla deterministycznego routingu
# =============================================================================

class RiskLevel(BaseModel):
    """Wynik oceny ryzyka — wyjście assess_risk, wejście route_by_risk."""
    risk: Literal["low", "medium", "high", "error"] = Field(
        description="Poziom ryzyka celu lub 'error' jeśli cel niedostępny."
    )
    target: str = Field(description="URL lub opis celu audytu.")
    reason: str = Field(description="Uzasadnienie oceny ryzyka (1-2 zdania).")


# =============================================================================
# WĘZEŁ 1: Assessment — zwraca pydantic model (nie string!)
# =============================================================================

def init_audit(node_input: str):
    """Inicjuje state z opisem celu."""
    yield Event(state={"audit_request": node_input})


assess_risk = Agent(
    name="assess_risk",
    model=MODEL,
    instruction="""Oceniasz ryzyko celu audytu bezpieczeństwa.

Żądanie: "{audit_request}"

Określ poziom ryzyka:
- "high":   produkcja, dane finansowe/medyczne, payment gateway, dane użytkowników
- "medium": staging, wewnętrzne systemy biznesowe, umiarkowane dane
- "low":    sandbox, dev environment, brak wrażliwych danych
- "error":  cel niedostępny, brak odpowiedzi, nieprawidłowy URL

Odpowiedz zgodnie ze schematem JSON (risk, target, reason).""",
    output_schema=RiskLevel,   # ← wymusza strukturalny output
    output_key="risk_assessment",
)


# =============================================================================
# ROUTER — czysta funkcja Pythona, testowalny bez LLM
# =============================================================================

def route_by_risk(node_input: RiskLevel):
    """
    Deterministyczny router na podstawie pydantic modelu.
    TESTOWALNY: assert list(route_by_risk(RiskLevel(risk="high", ...)))[0].route == "deep"
    """
    # Zapisz tryb skanu w state dla observability
    yield Event(
        route=node_input.risk if node_input.risk in ("high", "error") else "fast",
        state={"target": node_input.target, "scan_mode": node_input.risk},
    )


# =============================================================================
# GAŁĘZIE — jeden agent per ścieżka
# =============================================================================

fast_scan_agent = Agent(
    name="fast_scan",
    model=MODEL,
    instruction="""Wykonujesz szybki skan bezpieczeństwa (LOW/MEDIUM risk).

Cel: "{target}"
Tryb: FAST — podstawowe OWASP checks

Sprawdź:
1. Security headers (X-Frame-Options, CSP, HSTS)
2. Otwarte endpointy administracyjne (/admin, /debug, /.env)
3. Podstawowe SQL Injection markers
4. Brak rate limiting na /login

Raport JSON: {"scan_type": "fast", "findings": [...], "duration_estimate": "2-3min"}""",
    output_key="scan_result",
)

deep_scan_agent = Agent(
    name="deep_scan",
    model=MODEL,
    instruction="""Wykonujesz pełny pentest (HIGH risk).

Cel: "{target}"
Tryb: DEEP — pełne OWASP Top 10

Sprawdź:
1. A01: Broken Access Control (IDOR, privilege escalation)
2. A02: Cryptographic Failures (TLS, weak ciphers, exposed keys)
3. A03: Injection (SQL, NoSQL, Command, LDAP, XSS)
4. A05: Security Misconfiguration (verbose errors, default creds)
5. A07: Identification & Auth Failures

Raport JSON: {"scan_type": "deep", "findings": [...], "owasp_coverage": [...]}""",
    output_key="scan_result",
)

error_handler = Agent(
    name="error_handler",
    model=MODEL,
    instruction="""Cel audytu jest NIEDOSTĘPNY.

Żądanie: "{audit_request}"

Wygeneruj raport diagnostyczny:
1. Możliwe przyczyny niedostępności
2. Kroki diagnostyczne dla Ops
3. Sugerowany czas retry (minuty)
4. Czy wymagana eskalacja (TAK/NIE + powód)

Raport JSON: {"cause": "...", "steps": [...], "retry_minutes": 30, "escalate": false}""",
    output_key="scan_result",
)


# =============================================================================
# WĘZEŁ KOŃCOWY — agreguje wyniki ze wszystkich gałęzi
# =============================================================================

audit_reporter = Agent(
    name="audit_reporter",
    model=MODEL,
    instruction="""Generujesz finalny raport audytowy.

Wynik skanu: "{scan_result}"
Tryb skanu: "{scan_mode}"
Cel: "{target}"

## Audit Report
**Target**: {target}
**Scan Type**: {scan_mode}
**Risk Summary**: CRITICAL/HIGH/MEDIUM/LOW
**Key Findings**: (top 3)
**Required Actions**: (priorytety z timeline)
**OWASP Compliance**: (coverage)""",
)


# =============================================================================
# ROOT AGENT — Workflow z warunkowym rozgałęzieniem
# =============================================================================
# Graf:
#   START → init → assess_risk → route_by_risk ─┬─ "high"  → deep_scan  ─┐
#                                                ├─ "fast"  → fast_scan  ─┼─→ audit_reporter
#                                                └─ "error" → error_handler─┘

root_agent = Workflow(
    name="root_agent",
    edges=[
        # Sekwencja do routera:
        ("START", init_audit, assess_risk, route_by_risk),
        # Rozgałęzienie (dict = conditional edges):
        (route_by_risk, {
            "high":  deep_scan_agent,
            "fast":  fast_scan_agent,
            "error": error_handler,
        }),
        # Wszystkie gałęzie zbiegają się w audit_reporter:
        (deep_scan_agent,  audit_reporter),
        (fast_scan_agent,  audit_reporter),
        (error_handler,    audit_reporter),
    ],
)

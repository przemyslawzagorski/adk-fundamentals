"""
Module 32 — A2A Protocol: REMOTE CODE ANALYST AGENT
=====================================================

Ten plik eksponuje agenta jako usługę A2A za pomocą to_a2a().
Uruchamiany przez uvicorn na porcie 8001.

URUCHOMIENIE:
    # Z katalogu głównego projektu:
    uvicorn adk_training.module_32_a2a.remote_a2a.code_analyst.agent:a2a_app \
        --host localhost --port 8001

WERYFIKACJA:
    curl http://localhost:8001/.well-known/agent-card.json

CO ROBI to_a2a():
    1. Tworzy A2aAgentExecutor jako mostek między A2A ↔ ADK
    2. Auto-generuje agent-card z metadanych agenta
    3. Rejestruje endpointy A2A w aplikacji Starlette
    4. Zarządza sesjami i stanem w pamięci (InMemoryTaskStore)
"""
from __future__ import annotations

import os
import re
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.adk.a2a.utils.agent_to_a2a import to_a2a

load_dotenv()
MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")


# =============================================================================
# NARZĘDZIA — deterministyczne, specjalistyczne dla code_analyst
# =============================================================================

def scan_for_hardcoded_secrets(code_snippet: str) -> dict:
    """
    Skanuje kod w poszukiwaniu hardkodowanych sekretów.

    Args:
        code_snippet: Kod źródłowy do analizy

    Returns:
        dict z: found_secrets (lista), risk_level, recommendation
    """
    patterns = {
        "password_literal": r'(?i)(password|passwd|pwd)\s*=\s*["\'][^"\']{3,}["\']',
        "api_key_literal": r'(?i)(api_key|apikey|secret_key)\s*=\s*["\'][^"\']{8,}["\']',
        "token_literal": r'(?i)(token|bearer)\s*=\s*["\'][^"\']{10,}["\']',
        "aws_key": r'AKIA[0-9A-Z]{16}',
    }
    found = []
    for name, pattern in patterns.items():
        matches = re.findall(pattern, code_snippet)
        if matches:
            found.append({"type": name, "occurrences": len(matches)})

    risk = "high" if found else "low"
    return {
        "found_secrets": found,
        "secrets_count": len(found),
        "risk_level": risk,
        "recommendation": (
            "Przenieś sekrety do zmiennych środowiskowych lub secret managera."
            if found else "Brak hardkodowanych sekretów. OK."
        ),
    }


def scan_for_sql_injection(code_snippet: str) -> dict:
    """
    Wykrywa potencjalne podatności SQL Injection.

    Args:
        code_snippet: Kod źródłowy do analizy

    Returns:
        dict z: vulnerable_patterns, risk_level, safe_alternatives
    """
    # Wzorce niebezpiecznej konkatenacji SQL
    dangerous_patterns = [
        r'(?i)execute\s*\(\s*["\'].*\+',       # "SELECT " + user_input
        r'(?i)cursor\.execute\([^,)]*%\s*[^(]', # cursor.execute("..." % val)
        r'(?i)f["\'].*SELECT.*\{',               # f"SELECT {user}"
        r'(?i)query\s*=.*\+.*input',             # query = "..." + input
    ]
    safe_patterns = [
        r'(?i)cursor\.execute\(.*,\s*\(',        # cursor.execute("...", (val,))
        r'(?i)\.filter\(',                        # ORM filter
        r'(?i)parameterized',                     # parametrized mention
    ]

    found_unsafe = [p for p in dangerous_patterns if re.search(p, code_snippet)]
    found_safe = [p for p in safe_patterns if re.search(p, code_snippet)]

    risk = "critical" if found_unsafe and not found_safe else (
        "medium" if found_unsafe else "low"
    )
    return {
        "vulnerable_patterns_found": len(found_unsafe),
        "safe_patterns_found": len(found_safe),
        "risk_level": risk,
        "safe_alternatives": [
            "Użyj zapytań parametryzowanych: cursor.execute(sql, (val,))",
            "Użyj ORM (SQLAlchemy, Django ORM)",
            "Waliduj i sanityzuj input przed użyciem w query",
        ] if found_unsafe else [],
    }


# =============================================================================
# ROOT AGENT — wystawiany przez A2A
# =============================================================================

root_agent = LlmAgent(
    name="code_analyst_agent",
    model=MODEL,
    description=(
        "Specjalistyczny agent do bezpieczeństwa kodu. "
        "Wykrywa hardkodowane sekrety i podatności SQL Injection. "
        "Zwraca strukturalny raport JSON z oceną ryzyka."
    ),
    instruction="""Jesteś ekspertem od bezpieczeństwa kodu.

ZAWSZE wykonaj OBIE analizy na dostarczonym kodzie:
1. Wywołaj scan_for_hardcoded_secrets() — sprawdza hasła/klucze/tokeny
2. Wywołaj scan_for_sql_injection() — sprawdza podatności SQL

Po analizie zwróć TYLKO JSON (bez markdown):
{
  "security_score": <0-10, gdzie 10 = bezpieczny>,
  "critical_issues": [{"type": "...", "description": "...", "line_hint": "..."}],
  "hardcoded_secrets": <wynik z scan_for_hardcoded_secrets>,
  "sql_injection": <wynik z scan_for_sql_injection>,
  "overall_risk": "low|medium|high|critical",
  "action_required": true|false
}

Zasady:
- security_score = 10 - (3 * critical) - (1 * medium)
- overall_risk=critical jeśli którykolwiek skan zwróci critical lub high
- action_required=true jeśli overall_risk in ["high", "critical"]
""",
    tools=[
        FunctionTool(func=scan_for_hardcoded_secrets),
        FunctionTool(func=scan_for_sql_injection),
    ],
)

# =============================================================================
# A2A APP — eksponuje root_agent jako usługę A2A przez uvicorn
# Auto-generuje agent-card z metadanych LlmAgent.
# =============================================================================

a2a_app = to_a2a(root_agent, port=8001)

"""
6 produkcyjnych narzędzi ADK + 3 narzędzia diagnostyczne.
==========================================================

Każde delegujące do Auggie używa `auggie_run()` z pełnym stackiem:
cache → circuit breaker → retry → telemetry → cost.

Tools:
  Production (6):
    1. code_review_pr           — success_criteria + dataclass return
    2. analyze_codebase         — typed return List[Finding]
    3. generate_implementation  — success_criteria + iteracyjna weryfikacja
    4. refactor_workflow        — multi-step session() (kontekst między krokami)
    5. security_audit           — function calling
    6. ask_specialist           — generic delegation z cachem

  Diagnostics (3):
    7. auggie_telemetry         — statystyki wywołań
    8. auggie_cost_report       — szacunkowe koszty
    9. auggie_health            — system health check
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from typing import List

from auggie_factory import (
    AuggieUnavailable, TELEMETRY, auggie_call, auggie_run,
)
from caching import CACHE
from cost_tracker import COST
from resilience import BREAKER, CircuitBreakerOpen

logger = logging.getLogger(__name__)


# =============================================================================
# DATACLASSY
# =============================================================================
@dataclass
class ReviewIssue:
    severity: str
    file: str
    line: int
    category: str
    description: str
    suggested_fix: str


@dataclass
class CodeReview:
    summary: str
    issues: List[ReviewIssue]
    approval: str


@dataclass
class CodebaseFinding:
    path: str
    kind: str
    purpose: str
    risks: List[str]


# =============================================================================
# Helper — uniwersalny error wrapper
# =============================================================================
def _safe(fn):
    """Decorator: każdy tool zwraca string (JSON lub komunikat błędu)."""
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except CircuitBreakerOpen as e:
            return json.dumps({"error": "circuit_breaker_open", "detail": str(e)}, ensure_ascii=False)
        except AuggieUnavailable as e:
            return json.dumps({"error": "sdk_unavailable", "detail": str(e)}, ensure_ascii=False)
        except Exception as e:  # noqa: BLE001
            return json.dumps({"error": type(e).__name__, "detail": str(e)}, ensure_ascii=False)
    wrapper.__name__ = fn.__name__
    wrapper.__doc__ = fn.__doc__
    return wrapper


# =============================================================================
# TOOL 1: code_review_pr
# =============================================================================
@_safe
def code_review_pr(diff: str, repo_context: str = "", max_retries: int = 3) -> str:
    """
    Wykonuje strukturalny code review diffa z weryfikacją kryteriów jakości.

    Args:
        diff: Zawartość unified diff (output `git diff`).
        repo_context: Krótki kontekst repo (1-3 zdania, opcjonalnie).
        max_retries: Maks. liczba retrów (domyślnie 3).

    Returns:
        JSON z polami: summary, approval, issues[].
    """
    if not diff.strip():
        return json.dumps({"error": "Pusty diff."}, ensure_ascii=False)

    prompt = f"""Wykonaj rzetelny code review tego diffa.
{f'Kontekst repo: {repo_context}' if repo_context else ''}

DIFF:
```
{diff[:8000]}
```

Zwróć obiekt CodeReview z listą issues (severity, file, line, category, description, suggested_fix).
Każdy issue MUSI mieć konkretną sugestię naprawy. Jeśli kod jest OK — pusta lista issues + approval='approve'.
"""
    review: CodeReview = auggie_run(
        tool_name="code_review_pr",
        prompt=prompt,
        return_type=CodeReview,
        success_criteria=[
            "Każdy issue ma niepustego suggested_fix",
            "severity in {critical, major, minor, nit}",
            "category in {bug, security, performance, style, test}",
            "approval in {approve, request_changes, comment}",
        ],
        max_verification_rounds=2,
        max_attempts=max_retries,
        extra_cli=["--quiet"],
    )
    return json.dumps(
        {
            "summary": review.summary,
            "approval": review.approval,
            "issues": [i.__dict__ for i in review.issues],
        },
        ensure_ascii=False, indent=2,
    )


# =============================================================================
# TOOL 2: analyze_codebase
# =============================================================================
@_safe
def analyze_codebase(target_path: str = "", max_files: int = 20) -> str:
    """
    Analizuje strukturę workspace i zwraca listę kluczowych modułów.

    Args:
        target_path: Ścieżka do katalogu do analizy (domyślnie: cały workspace).
        max_files: Maks. liczba plików w raporcie.

    Returns:
        JSON list of findings.
    """
    prompt = (
        f"Przeanalizuj strukturę tego workspace. "
        f"Zwróć listę MAX {max_files} kluczowych plików/modułów. "
        "Dla każdego: path, kind (module/service/model/config/test), purpose (1 zdanie), "
        "risks (lista lub pusta lista)."
    )
    findings: List[CodebaseFinding] = auggie_run(
        tool_name="analyze_codebase",
        prompt=prompt,
        return_type=List[CodebaseFinding],
        extra_cli=["--quiet"],
        workspace_override=target_path if target_path else None,
    )
    return json.dumps([f.__dict__ for f in findings], ensure_ascii=False, indent=2)


# =============================================================================
# TOOL 3: generate_implementation
# =============================================================================
@_safe
def generate_implementation(spec: str, language: str = "python", must_have_csv: str = "") -> str:
    """
    Generuje implementację kodu z iteracyjną weryfikacją kryteriów.

    Args:
        spec: Specyfikacja co ma zostać zaimplementowane.
        language: Język programowania (default 'python').
        must_have_csv: Dodatkowe wymagania (oddzielone ';').

    Returns:
        Wygenerowany kod.
    """
    base_criteria = [
        f"Kod jest w języku {language}",
        "Kod ma pełne type hints (gdy język to wspiera)",
        "Funkcje publiczne mają docstring",
        "Obsłużone są przypadki brzegowe (None, puste wejście, błędne dane)",
        "Brak literałów hasłowych/sekretów w kodzie",
    ]
    extra = [c.strip() for c in must_have_csv.split(";") if c.strip()]
    criteria = base_criteria + extra

    return auggie_run(
        tool_name="generate_implementation",
        prompt=f"Zaimplementuj zgodnie ze specyfikacją:\n\n{spec}\n\nZwróć TYLKO kod (gotowy do wklejenia).",
        return_type=str,
        success_criteria=criteria,
        max_verification_rounds=3,
        extra_cli=["--quiet"],
    )


# =============================================================================
# TOOL 4: refactor_workflow (session — bez auggie_run, sesja wymaga raw obiektu)
# =============================================================================
@_safe
def refactor_workflow(target_file: str, refactor_goal: str) -> str:
    """
    Wieloetapowy refactor (analiza → plan → kod → testy) w jednej sesji.

    Args:
        target_file: Ścieżka do pliku.
        refactor_goal: Cel refactoru.

    Returns:
        Połączony raport z 4 kroków.
    """
    steps = [
        f"Przeanalizuj plik {target_file}. Wymień: główne klasy/funkcje, zależności, code smells.",
        f"Zaproponuj plan refactoru pod kątem: {refactor_goal}. Lista 3-7 kroków.",
        "Wygeneruj zrefactorowaną wersję pliku zgodną z planem (sam kod, gotowy do podmiany).",
        "Wygeneruj testy pytest weryfikujące że zrefactorowana wersja zachowuje stare zachowanie.",
    ]
    with auggie_call("refactor_workflow", extra_cli=["--quiet"]) as auggie:
        outputs = []
        with auggie.session() as sess:
            for i, step in enumerate(steps, 1):
                out = sess.run(step, return_type=str)
                outputs.append(f"## Krok {i}\n{out}")
        return "\n\n".join(outputs)


# =============================================================================
# TOOL 5: security_audit
# =============================================================================
_SECRET_PATTERNS = [
    (r"sk-[A-Za-z0-9]{20,}", "OpenAI/Anthropic API key"),
    (r"ghp_[A-Za-z0-9]{36}", "GitHub PAT"),
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key"),
    (r"-----BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY-----", "Private key"),
    (r"(?i)password\s*=\s*['\"][^'\"]{6,}['\"]", "Hardcoded password"),
]


def scan_for_secrets(content: str) -> dict:
    """Skanuje treść pod kątem sekretów (API keys, hasła, klucze prywatne).

    Args:
        content: Tekst do przeskanowania.
    """
    findings = []
    for pattern, label in _SECRET_PATTERNS:
        for m in re.finditer(pattern, content):
            findings.append({"type": label, "preview": m.group()[:24] + "..."})
    return {"count": len(findings), "findings": findings[:20]}


def check_dependency_age(package: str, ecosystem: str = "pypi") -> dict:
    """Mock: sprawdza czy paczka jest aktualna.

    Args:
        package: Nazwa paczki.
        ecosystem: 'pypi' | 'npm' | 'maven'.
    """
    return {
        "package": package,
        "ecosystem": ecosystem,
        "outdated": package.lower() in {"requests", "django", "flask", "numpy"},
        "advisory": None,
    }


@_safe
def security_audit(target: str = ".") -> str:
    """
    Audit bezpieczeństwa (sekrety, zależności) z function calling.

    Args:
        target: Ścieżka do auditu (domyślnie '.').

    Returns:
        Raport audytu.
    """
    prompt = (
        f"Wykonaj audyt bezpieczeństwa katalogu '{target}' w workspace. "
        "1) Znajdź pliki które MOGĄ zawierać sekrety. "
        "2) Dla podejrzanych treści UŻYJ funkcji scan_for_secrets aby zweryfikować. "
        "3) Wymień zależności (requirements.txt/package.json) i UŻYJ check_dependency_age "
        "dla 3-5 kluczowych paczek. "
        "4) Zwróć krótki raport: znalezione sekrety, ryzykowne zależności, rekomendacje."
    )
    return auggie_run(
        tool_name="security_audit",
        prompt=prompt,
        return_type=str,
        functions=[scan_for_secrets, check_dependency_age],
    )


# =============================================================================
# TOOL 6: ask_specialist (generic) — z cachem
# =============================================================================
@_safe
def ask_specialist(question: str) -> str:
    """
    Generyczne zapytanie do Auggie (Claude Sonnet) — z włączonym cache.

    Powtórzone pytanie zwraca natychmiast z cache (oszczędność).

    Args:
        question: Pytanie/zadanie.

    Returns:
        Odpowiedź tekstowa.
    """
    return auggie_run(
        tool_name="ask_specialist",
        prompt=question,
        return_type=str,
        extra_cli=["--quiet"],
    )


# =============================================================================
# TOOL 7-9: DIAGNOSTICS
# =============================================================================
def auggie_telemetry() -> str:
    """Statystyki wywołań Auggie (liczba, czas, success, cached)."""
    summary = TELEMETRY.summary()
    last = TELEMETRY.calls[-5:]
    return json.dumps({
        "summary": summary,
        "cache": CACHE.stats.to_dict(),
        "circuit_breaker": BREAKER.status(),
        "last_calls": [
            {
                "tool": c.tool, "duration_s": round(c.duration_s, 2),
                "success": c.success, "cached": c.cached, "attempts": c.attempts,
                "tool_calls": c.tool_calls, "function_calls": c.function_calls,
                "error": c.error,
            } for c in last
        ],
    }, ensure_ascii=False, indent=2)


def auggie_cost_report() -> str:
    """Szacunkowe koszty wywołań Auggie (USD, by tool, by model)."""
    return json.dumps(COST.summary(), ensure_ascii=False, indent=2)


def auggie_health() -> str:
    """Health check infrastruktury (SDK, CLI, auth, workspace)."""
    from health_check import run_checks
    results, healthy = run_checks(ping=False)
    return json.dumps({"healthy": healthy, "checks": results}, ensure_ascii=False, indent=2)

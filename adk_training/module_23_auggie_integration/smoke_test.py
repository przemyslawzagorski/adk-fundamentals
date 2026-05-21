"""
Smoke test dla module_23 — testuje 9 narzędzi + cache + breaker.

Użycie:
    python smoke_test.py            # wszystkie testy
    python smoke_test.py 1 3 6      # tylko wybrane
    python smoke_test.py --quick    # tylko diagnostyka (bez Auggie calls)
"""

from __future__ import annotations

import logging
import pathlib
import sys
import time

from dotenv import load_dotenv

_HERE = pathlib.Path(__file__).parent
load_dotenv(_HERE / ".env")
load_dotenv(_HERE.parent / ".env", override=False)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

from tools import (  # noqa: E402
    analyze_codebase, ask_specialist, auggie_cost_report, auggie_health,
    auggie_telemetry, code_review_pr, generate_implementation,
    refactor_workflow, security_audit,
)


SAMPLE_DIFF = """diff --git a/calc.py b/calc.py
@@ -1,3 +1,7 @@
-def divide(a, b):
-    return a / b
+def divide(a: float, b: float) -> float:
+    if b == 0:
+        raise ValueError("division by zero")
+    return a / b
+
+def add(a, b):
+    return a + b
"""


def _section(name: str) -> None:
    print(f"\n{'='*60}\n=== {name}\n{'='*60}")


def t1_code_review() -> None:
    _section("TEST 1: code_review_pr")
    out = code_review_pr(diff=SAMPLE_DIFF, repo_context="Mały moduł kalkulatora.")
    print(out[:1500])


def t2_analyze() -> None:
    _section("TEST 2: analyze_codebase")
    out = analyze_codebase(focus_paths="", max_files=5)
    print(out[:1500])


def t3_generate() -> None:
    _section("TEST 3: generate_implementation")
    out = generate_implementation(
        spec="Funkcja `safe_divide(a, b)` zwraca a/b lub None przy b==0. Z testem.",
        language="python",
        must_have_csv="Type hints;Docstring;Test pytest",
    )
    print(out[:1500])


def t4_refactor() -> None:
    _section("TEST 4: refactor_workflow")
    out = refactor_workflow(
        target_file="tools.py",
        refactor_goal="wydziel sekcje z dataclassami do osobnego pliku models.py",
    )
    print(out[:2000])


def t5_security() -> None:
    _section("TEST 5: security_audit")
    out = security_audit(target=".")
    print(out[:1500])


def t6_ask_cache() -> None:
    """Test cache: 2x to samo pytanie — drugi raz powinien być natychmiastowy."""
    _section("TEST 6: ask_specialist + CACHE")
    q = "Wytłumacz w 2 zdaniach co to jest dependency injection."

    t = time.perf_counter()
    out1 = ask_specialist(question=q)
    d1 = time.perf_counter() - t
    print(f"[1st call] {d1:.2f}s")
    print(out1[:500])

    t = time.perf_counter()
    out2 = ask_specialist(question=q)
    d2 = time.perf_counter() - t
    print(f"\n[2nd call] {d2:.2f}s  (cache hit if << 1s)")
    print(out2[:500])

    if d2 < d1 / 5:
        print(f"\n✓ CACHE HIT confirmed (speedup {d1/max(d2,0.001):.0f}x)")
    else:
        print(f"\n? Cache may not be active — check AUGGIE_CACHE_ENABLED")


def t7_telemetry() -> None:
    _section("TEST 7: auggie_telemetry")
    print(auggie_telemetry())


def t8_cost() -> None:
    _section("TEST 8: auggie_cost_report")
    print(auggie_cost_report())


def t9_health() -> None:
    _section("TEST 9: auggie_health")
    print(auggie_health())


TESTS = {
    1: t1_code_review, 2: t2_analyze, 3: t3_generate,
    4: t4_refactor, 5: t5_security, 6: t6_ask_cache,
    7: t7_telemetry, 8: t8_cost, 9: t9_health,
}

QUICK_TESTS = [9, 7, 8]  # bez kosztownych calls


def main() -> None:
    args = sys.argv[1:]
    if "--quick" in args:
        chosen = QUICK_TESTS
    elif args:
        chosen = [int(a) for a in args if a.isdigit()]
    else:
        chosen = list(TESTS.keys())

    failed = []
    for n in chosen:
        if n not in TESTS:
            print(f"Brak testu {n}. Dostępne: {sorted(TESTS)}")
            continue
        try:
            TESTS[n]()
        except Exception as e:  # noqa: BLE001
            print(f"!!! TEST {n} FAILED: {type(e).__name__}: {e}")
            failed.append(n)

    print(f"\n{'='*60}\nDONE — {len(chosen)-len(failed)}/{len(chosen)} OK")
    if failed:
        print(f"FAILED: {failed}")
        sys.exit(1)


if __name__ == "__main__":
    main()

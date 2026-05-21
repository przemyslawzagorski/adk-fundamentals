"""
Entry-point dla LIVE testow - PRAWDZIWE Gemini przez Vertex AI.

UWAGA: ponosi koszty API. Uruchamiaj swiadomie.

Wymagane ENV:
    RUN_LIVE_TESTS=1
    GOOGLE_CLOUD_PROJECT=<twoj-projekt>
    GOOGLE_GENAI_USE_VERTEXAI=1
    GOOGLE_CLOUD_LOCATION=us-central1   (opcjonalnie)

Uzycie:
    python run_live_tests.py
    python run_live_tests.py -k tool
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    module_dir = Path(__file__).resolve().parent
    os.chdir(module_dir)
    if str(module_dir) not in sys.path:
        sys.path.insert(0, str(module_dir))

    # Sprawdzenie ENV
    if os.environ.get("RUN_LIVE_TESTS") != "1":
        print("=" * 70)
        print("LIVE TESTY POMINIETE.")
        print("Aby je uruchomic ustaw:")
        print("    $env:RUN_LIVE_TESTS='1'")
        print("    $env:GOOGLE_CLOUD_PROJECT='twoj-projekt'")
        print("    $env:GOOGLE_GENAI_USE_VERTEXAI='1'")
        print("=" * 70)
        return 0

    if not os.environ.get("GOOGLE_CLOUD_PROJECT"):
        print("BLAD: Brak GOOGLE_CLOUD_PROJECT.")
        return 2

    import pytest

    # -m live wlacza marker; nadpisujemy default addopts
    args = argv or ["tests/live", "-v", "-m", "live", "--tb=short"]
    return pytest.main(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

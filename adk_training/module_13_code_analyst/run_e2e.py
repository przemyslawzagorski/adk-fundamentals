"""
Entry-point do uruchomienia pakietu testow E2E z poziomu Pythona.

Uzycie:
    python run_e2e.py                      # wszystkie E2E
    python run_e2e.py tests/e2e/test_auth.py  # pojedynczy plik
    python run_e2e.py -k auth              # po nazwie
    python run_e2e.py -v                   # verbose

Skrypt nie wymaga aktywnego srodowiska Vertex AI — mockuje LLM i indexer.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    module_dir = Path(__file__).resolve().parent
    os.chdir(module_dir)

    # Upewnij sie, ze sciezka do modulu jest w PYTHONPATH
    if str(module_dir) not in sys.path:
        sys.path.insert(0, str(module_dir))

    import pytest  # lazy import

    # Domyslnie: caly katalog tests/e2e
    args = argv or ["tests/e2e", "-v", "--tb=short"]
    return pytest.main(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

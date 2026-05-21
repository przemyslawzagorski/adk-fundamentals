"""
Entry-point do uruchomienia PRAWDZIWYCH testow agentowych z Pythona.

Uruchamia prawdziwy ADK Runner + SequentialAgent + realne tooli file_tools.
LLM jest skryptowany (FakeLlm) - zero polaczen do Vertex/Gemini.

Uzycie:
    python run_agent_tests.py
    python run_agent_tests.py -k path_traversal
    python run_agent_tests.py -v
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

    import pytest

    args = argv or ["tests/agent", "-v", "--tb=short"]
    return pytest.main(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

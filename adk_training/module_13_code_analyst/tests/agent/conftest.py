"""
Konfiguracja testow agentowych. Bez mockow Runnera/Indexera - to jest
integracyjna warstwa agenta ADK.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

_MODULE_DIR = Path(__file__).resolve().parents[2]
_WEB_DIR = _MODULE_DIR / "web"
for _p in (_MODULE_DIR, _WEB_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

# Testy agentowe nie wymagaja GCP - ale kazemy ADK NIE probowac konfigurowac
# Vertex (jesli ktos ma ustawione w .env, nie szkodzi - FakeLlm i tak nie
# wywola zadnego zewnetrznego API).
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "0")
os.environ.setdefault("GOOGLE_API_KEY", "not-used-fakellm")


@pytest.fixture()
def sample_repo(tmp_path: Path) -> Path:
    """Minimalne repo z paroma plikami - realne tooli beda na nim operowac."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "main.py").write_text(
        "def greet(name):\n    return f'hello, {name}'\n\nprint(greet('world'))\n",
        encoding="utf-8",
    )
    (repo / "README.md").write_text(
        "# Sample\nPrzykladowy projekt dla testow agentowych.\n",
        encoding="utf-8",
    )
    (repo / "utils.py").write_text(
        "def add(a, b):\n    return a + b\n",
        encoding="utf-8",
    )
    return repo

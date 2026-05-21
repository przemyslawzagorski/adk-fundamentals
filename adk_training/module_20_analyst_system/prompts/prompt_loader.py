"""Loader promptów markdown z `module_20/prompts/markdown/`.

Zachowuje pattern z zagi-analyst-assistant — prompty w plikach .md zamiast string literals,
żeby łatwo edytować je bez ruszania kodu Pythona.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

_PROMPTS_DIR = Path(__file__).resolve().parent / "markdown"


@lru_cache(maxsize=64)
def load_prompt(name: str) -> str:
    """Załaduj prompt z `markdown/{name}.md`. Cache w pamięci.

    Args:
        name: Nazwa bez rozszerzenia, np. 'hld_writer_pl'.

    Raises:
        FileNotFoundError: gdy plik nie istnieje (typowy błąd konfiguracyjny).
    """
    path = _PROMPTS_DIR / f"{name}.md"
    if not path.is_file():
        raise FileNotFoundError(f"Prompt not found: {path}")
    return path.read_text(encoding="utf-8")

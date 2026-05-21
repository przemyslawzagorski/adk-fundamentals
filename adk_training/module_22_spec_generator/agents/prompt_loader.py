"""Helper do ladowania promptow z plikow .md.

ADK interpretuje `{KEY}` (rownież zagniezdzone `{{KEY}}`) w instrukcji agenta jako
placeholder ze state (`InstructionUtils._populate_values`). W naszych promptach
placeholdy-szablony oznaczamy przez `<KEY>` aby uniknac kolizji. Jesli chcesz
realnie podstawiac wartosc z `session.state`, uzyj `{KEY}` explicite - wtedy
ADK ja podmieni.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


@lru_cache(maxsize=16)
def load_prompt(name: str) -> str:
    """Zaladuj prompt z prompts/<name>.md (z cache).

    Args:
        name: Nazwa pliku bez rozszerzenia (np. "hld_pl").
    """
    path = PROMPTS_DIR / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Prompt not found: {path}")
    return path.read_text(encoding="utf-8")

"""Pre-commit guard: blokuje commit zawierajacy ewidentnie zywe tokeny.

Wywolanie: python tools/check_no_live_tokens.py <plik1> <plik2> ...

Wzorce (heurystyki):
  - ghp_XXXXXXXX (GitHub PAT)
  - glpat-XXXXXXXX (GitLab PAT)
  - Bearer <base64ish>
  - Jira/Confluence-style: base64:base64  (np. NzAxNjA4MDgwODYyOg...:...)

False positive-y da sie wyciszyc przez `# pragma: allowlist secret`.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


PATTERNS = [
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"glpat-[A-Za-z0-9_\-]{20,}"),
    re.compile(r"gho_[A-Za-z0-9]{20,}"),
    re.compile(r"xoxb-[A-Za-z0-9\-]{20,}"),
    re.compile(r"AIza[0-9A-Za-z_\-]{30,}"),
    # Jira/Confluence tokeny Comarch (base64 : base64, >20 znakow kazdy)
    re.compile(r"\b[A-Za-z0-9+/=]{30,}:[A-Za-z0-9+/=_\-]{20,}\b"),
    re.compile(r"Bearer\s+[A-Za-z0-9+/=_\-\.]{30,}"),
]

ALLOW_TAG = "pragma: allowlist secret"


def check_file(path: Path) -> list[str]:
    problems: list[str] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:  # pragma: no cover
        return [f"{path}: cannot read: {exc}"]

    for i, line in enumerate(text.splitlines(), 1):
        if ALLOW_TAG in line:
            continue
        for pat in PATTERNS:
            if pat.search(line):
                problems.append(f"{path}:{i}: potencjalny sekret '{pat.pattern}'")
                break
    return problems


def main(argv: list[str]) -> int:
    if not argv:
        return 0
    all_problems: list[str] = []
    for arg in argv:
        p = Path(arg)
        if not p.exists() or not p.is_file():
            continue
        # Pomijamy pliki binarne
        try:
            with open(p, "rb") as f:
                chunk = f.read(4096)
            if b"\x00" in chunk:
                continue
        except Exception:
            continue
        all_problems.extend(check_file(p))

    if all_problems:
        print("BLAD: wykryto potencjalne sekrety w plikach do commita:", file=sys.stderr)
        for pr in all_problems:
            print("  " + pr, file=sys.stderr)
        print(file=sys.stderr)
        print("Jesli to false-positive, dodaj '# pragma: allowlist secret' na tej samej linii.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

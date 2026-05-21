"""
Eksport rozmowy VS Code Copilot Chat -> markdown.

Tryby:
  1) Z eksportu natywnego ("Chat: Export..." w VS Code -> plik JSON):
       python tools/export_chat.py --input chat.json --output reports/chat.md
  2) Z aktualnego workspace'a (auto-wykrycie najnowszej sesji):
       python tools/export_chat.py --auto --output reports/chat.md

Uwaga: plik wynikowy moze zawierac wrazliwe fragmenty (tokeny, sekrety).
Zawsze weryfikuj przed commitem / udostepnieniem.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


SENSITIVE_PATTERNS = [
    (re.compile(r"(ghp_[A-Za-z0-9]{20,})"), "ghp_***REDACTED***"),
    (re.compile(r"(Bearer\s+[A-Za-z0-9+/=_\-\.]{20,})"), "Bearer ***REDACTED***"),
    (re.compile(r"([A-Za-z0-9+/=]{30,}:[A-Za-z0-9+/=_\-]{20,})"), "***REDACTED_BEARER***"),
    # PAT-y typu GitLab
    (re.compile(r"(glpat-[A-Za-z0-9_\-]{20,})"), "glpat-***REDACTED***"),
]


def redact(text: str) -> str:
    out = text
    for pat, repl in SENSITIVE_PATTERNS:
        out = pat.sub(repl, out)
    return out


# ------------------------------------------------------------------------
# Parser eksportu natywnego VS Code ("Chat: Export...")
# ------------------------------------------------------------------------

def _extract_text(part: Any) -> str:
    if isinstance(part, str):
        return part
    if isinstance(part, dict):
        if "value" in part and isinstance(part["value"], str):
            return part["value"]
        if "text" in part and isinstance(part["text"], str):
            return part["text"]
        if "content" in part:
            return _extract_text(part["content"])
        if "parts" in part and isinstance(part["parts"], list):
            return "\n".join(_extract_text(p) for p in part["parts"])
    if isinstance(part, list):
        return "\n".join(_extract_text(p) for p in part)
    return ""


def parse_native_export(data: Any) -> list[dict]:
    """Zwraca liste turn'ow: {role: user|assistant, text: str}."""
    turns: list[dict] = []

    # format 1: {"requests": [{"message": {...}, "response": [...]}]}
    if isinstance(data, dict) and "requests" in data:
        for req in data["requests"]:
            user_text = _extract_text(req.get("message", {}))
            if user_text.strip():
                turns.append({"role": "user", "text": user_text})
            resp = req.get("response") or req.get("responseModel") or []
            asst_text = _extract_text(resp)
            if asst_text.strip():
                turns.append({"role": "assistant", "text": asst_text})
        return turns

    # format 2: {"exchanges": [...]}
    if isinstance(data, dict) and "exchanges" in data:
        for ex in data["exchanges"]:
            for k in ("prompt", "request", "user"):
                if k in ex:
                    turns.append({"role": "user", "text": _extract_text(ex[k])})
                    break
            for k in ("response", "answer", "assistant"):
                if k in ex:
                    turns.append({"role": "assistant", "text": _extract_text(ex[k])})
                    break
        return turns

    # format 3: surowa lista wiadomosci
    if isinstance(data, list):
        for item in data:
            role = item.get("role") or item.get("type") or "assistant"
            role = "user" if "user" in role.lower() else "assistant"
            turns.append({"role": role, "text": _extract_text(item)})
        return turns

    raise ValueError("Nierozpoznany format eksportu.")


def render_markdown(turns: list[dict], title: str = "Rozmowa") -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"# {title}", "", f"_Wyeksportowano: {now}_", "", "---", ""]
    for i, t in enumerate(turns, 1):
        role = "USER" if t["role"] == "user" else "ASSISTANT"
        text = redact(t["text"].rstrip())
        lines.append(f"## [{i:03d}] {role}")
        lines.append("")
        lines.append(text)
        lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines)


# ------------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------------

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", "-i", type=Path, help="Plik JSON wyeksportowany z VS Code.")
    ap.add_argument("--output", "-o", type=Path, required=True, help="Plik wyjsciowy .md")
    ap.add_argument("--title", default="Rozmowa Copilot")
    args = ap.parse_args(argv)

    if not args.input or not args.input.exists():
        print("BLAD: Podaj istniejacy plik --input.", file=sys.stderr)
        print()
        print("Jak wyeksportowac z VS Code:")
        print("  1. Otworz panel Chat.")
        print("  2. Ctrl+Shift+P -> 'Chat: Export...'")
        print("  3. Zapisz JSON i przekaz sciezke przez --input.")
        return 2

    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"BLAD: nie mozna sparsowac JSON: {e}", file=sys.stderr)
        return 3

    turns = parse_native_export(data)
    if not turns:
        print("OSTRZEZENIE: brak wiadomosci w eksporcie.", file=sys.stderr)
        return 4

    md = render_markdown(turns, title=args.title)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(md, encoding="utf-8")
    print(f"OK: {len(turns)} wiadomosci -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

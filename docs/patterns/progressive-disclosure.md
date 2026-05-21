# Progressive disclosure (skills L1/L2/L3)

> Inspirowane Anthropic's *skills as folders* + ADK `SkillToolset` (module_14).
> Implementacja referencyjna: `adk_training/module_24_audit_ops/skills_loader.py`.

## Idea

LLM dostaje **manifest** wszystkich skilli (cheap), ale **pełne instrukcje**
ładuje tylko dla tych, które faktycznie są potrzebne (deterministyczny trigger
albo decyzja modelu).

| Poziom | Co | Token cost |
|---|---|---|
| **L1 — manifest** | `[{name, description}, ...]` | ~50 tok / skill |
| **L2 — instructions** | body `SKILL.md` (system-prompt fragment) | 200–800 tok / skill |
| **L3 — references** | pliki w `references/`, ładowane *na żądanie* z body | dowolne |

## Layout skilla

```text
skills/
  owasp-a01-access-control/
    SKILL.md                    # YAML front-matter + body (instructions)
    references/
      idor-templates.md         # L3 — model woła load_resource() gdy potrzebuje
```

`SKILL.md`:

```markdown
---
name: owasp-a01-access-control
description: Broken access control — IDOR, missing auth, session fixation. Triggers when forms with passwords or auth headers exist.
triggers: [forms, auth, access-control]
---
You are auditing OWASP A01. Focus on...
```

## Co skopiować do swojego modułu

```python
# w nowym module, np. module_13_code_analyst/
from adk_training.module_24_audit_ops.skills_loader import (
    SkillRegistry, load_skill_from_dir,
)
import pathlib

def code_analyst_registry() -> SkillRegistry:
    reg = SkillRegistry()
    base = pathlib.Path(__file__).parent / "skills"
    for d in sorted(base.iterdir()):
        if (d / "SKILL.md").is_file():
            reg.register(load_skill_from_dir(d))
    return reg
```

To jedyny kod jaki musisz napisać — reszta (parser, recursion safety, manifest)
jest reużywalna *as-is*.

## Wywołanie L2 dla wybranych skilli

```python
reg = code_analyst_registry()
manifest = reg.manifest()              # L1 → idzie do system-promptu
chosen   = reg.by_triggers(["forms"])  # deterministyczny wybór
prompt   = "\n\n".join(s.instructions for s in chosen)  # L2 → on-demand
```

## Anti-patterns

- ❌ **Wkładanie L2 wszystkich skilli na start** — to zabija sens disclosure (i kosztuje).
- ❌ **LLM pisze do `SKILL.md`** — instrukcje muszą być deterministyczne, wersjonowane w git.
- ❌ **Triggery jako fuzzy matching** — używamy zwykłego intersect zbiorów (test-friendly).
- ❌ **Brak `references/` guard** — patrz `load_resource()` w module_24, blokuje path traversal.

## Test snippets

```python
def test_skill_loads_minimal(tmp_path):
    d = tmp_path / "demo"
    d.mkdir()
    (d / "SKILL.md").write_text(
        "---\nname: demo\ndescription: demo skill\n---\nDo X.", encoding="utf-8"
    )
    s = load_skill_from_dir(d)
    assert s.name == "demo"
    assert "Do X" in s.instructions
```

## Gdzie już używamy

- `module_24_audit_ops/skills/` — 5 skilli OWASP + recon-helpers (eagerly registered).
- *(planowane)* `module_13_code_analyst/skills/` — komplexity, security, perf.
- *(planowane)* `module_22_spec_generator/skills/` — user-story, acceptance, edge-cases.

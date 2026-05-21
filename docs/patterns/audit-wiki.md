# Per-target wiki

> Karpathy's *LLM-Wiki* pattern, zaimplementowany deterministycznie w Pythonie:
> `adk_training/module_24_audit_ops/wiki.py`. Funkcje są **agnostyczne** —
> przyjmują `artifacts_dir: Path` jako parametr, więc działają poza AuditOps.

## Layout

```text
artifacts/wiki/<target_slug>/
  index.md                       # always-current TOC, hot-cache dla planera
  log.md                         # append-only chronological log
  findings/F-<slug>.md           # entity page per (severity, normalized_title)
  runs/<run_id>.md               # immutable stub linking to actual report
  synthesis/                     # LLM-authored, HITL-gated
```

## Niezłomne reguły

1. **Python pisze wiki**, LLM tylko czyta. Eliminuje read-your-own-prose corruption.
2. **`runs/<id>.md` immutable** — append-only do log + update index.
3. **Findings atomic** (Zettelkasten — stable ID per `severity-normalized_title`).
4. **`lint_wiki()`** flaguje broken links + orphans → uruchamiaj w CI.

## Drop-in do innego modułu

```python
from pathlib import Path
from adk_training.module_24_audit_ops.wiki import record_run, lint_wiki

# np. module_09_database_postgres — wiki per-schema
ARTIFACTS = Path(__file__).parent / "artifacts"

def after_db_audit(audit: dict) -> None:
    paths = record_run(ARTIFACTS, audit)
    issues = lint_wiki(ARTIFACTS, audit["target_url"])
    if issues:
        raise RuntimeError(f"wiki lint failed: {issues}")
```

`audit` musi mieć `target_url` (dowolny stable identifier) i listę `findings:[{severity, title, ...}]`.
Reszta (pliki, linki, daty) wygenerowana po stronie wiki writer.

## API w pigułce

```python
wiki_paths(artifacts_dir, target_url) -> WikiPaths
record_run(artifacts_dir, audit)      -> WikiPaths              # main entry
history_skill_text(artifacts_dir, target_url, max_findings=25)  # L3 → "audit-history" skill
lint_wiki(artifacts_dir, target_url)  -> List[LintIssue]
lint_all(artifacts_dir)               -> Dict[slug, List[issue]]
```

## Anti-patterns

- ❌ **LLM edytuje `index.md`** — wiki dryfuje, nie da się zlintować.
- ❌ **Mutable run files** — tracimy audit trail.
- ❌ **Findings bez normalizacji tytułu** — duplikaty per re-run.
- ❌ **Wiki jako primary storage** — to projekcja artefaktów do read-only docs, nie DB.

## Integracja z mkdocs

`artifacts/wiki/` możesz wystawić jako sekcję mkdocs (statyczne md):

```yaml
nav:
  - Audit history: '!include adk_training/module_24_audit_ops/artifacts/wiki/index.md'
```

…albo zamontować przez monorepo plugin jeśli każdy moduł ma swoje wiki.

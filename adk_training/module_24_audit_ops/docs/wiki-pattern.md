# V2 — Audit Wiki Pattern

> **Inspiration**: Andrej Karpathy's
> *[The Art of the LLM-Wiki](https://karpathy.bearblog.dev/the-art-of-the-llm-wiki/)*,
> sharpened by the gist comment debate (gnusupport / SEO-Warlord / yogirk).
> The bottom line: **at moderate scale, an index file is enough — no
> embedding-based RAG infrastructure needed.**

## What it is

A per-target, on-disk markdown wiki that captures every audit run as
*atomic, immutable, deterministic* artefacts. The LLM never writes here.
Python is the only writer.

## Why we do not use a vector store

| Vector RAG | Markdown wiki |
|------------|---------------|
| Requires Pinecone / Chroma / pgvector | A directory of `.md` files |
| Re-indexing on every run | `record_run()` writes 1–2 files |
| Hard to diff in git | `git diff wiki/` Just Works™ |
| Embedding drift across model versions | n/a |
| Expensive at our scale | $0 |
| Nice for >100k docs | Overkill for ≤10k findings |

We have at most a few hundred runs and a few hundred distinct findings per
target. Linear scan + grep wins.

## File layout

```text
wiki/<host_slug>/
├── index.md         ← TOC, rebuilt from disk every call (cheap, accurate)
├── log.md           ← append-only chronological event log
├── findings/
│   └── F-<sev>-<normalized-title>.md
├── runs/
│   └── <run_id>.md  ← immutable stub linking to artifacts/<id>/report.md
└── synthesis/       ← optional, LLM-authored, HITL-gated
```

## Hard rules (and the bugs they prevent)

### Rule 1 — Python writes, never the LLM

> **Bug prevented**: "the LLM rewrites the index and accidentally drops the
> first 30 entries because it can't count past 50".

`wiki.record_run`, `_rebuild_index`, `_append_log`, `_render_finding_page`
are all pure deterministic functions. The LLM is allowed *one* writer
endpoint: `POST /api/audit/wiki/synthesize`, and even there the output is
saved as a brand-new file under `synthesis/`, never overwriting prior
content, and only after the operator passes `accept=true`.

### Rule 2 — Run stubs are immutable

> **Bug prevented**: "rerunning the report generator changes the timestamps
> on old runs, breaking external links".

`record_run` checks `if not run_stub.is_file()` before writing. Once a run
is recorded, its stub never changes.

### Rule 3 — Findings have stable IDs

> **Bug prevented**: "the same vuln has 12 wiki entries because the LLM
> phrased the title differently each time".

`finding_slug(severity, title)` collapses cosmetic differences:

```python
finding_slug("high", "Missing CSP")
finding_slug("HIGH", "missing CSP")
finding_slug("high", "Missing  CSP   ")
# all equal: "high-missing-csp"
```

It also normalizes numbers — `"Form 12 leaks password"` and
`"Form 99 leaks password"` collapse to the same slug. Counting matters
across runs, not which form happened to be enumerated first.

### Rule 4 — Idempotent merging

> **Bug prevented**: "we recorded the same run three times and now the
> finding shows 'Occurrences: 3'".

When merging a finding, `record_run` skips occurrences whose `run_id` is
already on the page. Replaying the same audit produces the exact same
files (modulo `log.md`, which is intentionally append-only as an audit
trail).

### Rule 5 — Index rebuilt from disk every call

> **Bug prevented**: "deleting a finding manually leaves a dangling entry
> in index.md until the next bulk regenerate".

`_rebuild_index` walks `findings/`, `runs/`, `synthesis/` and emits a fresh
TOC. The cost is a directory listing — well below 1 ms for thousands of
files on a modern disk.

## What the LLM is allowed to do

Exactly two LLM-authored artefacts can land in the wiki:

1. **Run stub findings list** — but only because the run stub copies what
   the *audit* (Python-validated) produced; the LLM does not free-write the
   stub.
2. **Synthesis pages** under `synthesis/<timestamp>.md`, written by
   `POST /api/audit/wiki/synthesize` after the operator opts in. These are
   never read back into the planner — they are for human consumption.

The audit-history skill (V3) reads the wiki and surfaces it back into the
planner prompt — but that summarization happens in `wiki.history_skill_text`
which is also pure Python, just `re` over markdown. The LLM never gets to
edit anything it later reads.

## Lint contract

`lint_wiki(artifacts_dir, target_url)` reports:

- `broken_link` — relative link target does not exist on disk;
- `missing_run_stub` — a finding page references a run id that has no stub.

Run it in CI:

```powershell
.venv312\Scripts\python.exe -m adk_training.module_24_audit_ops.cli `
    wiki-lint --report-dir .\artifacts --json
```

Exit code is `1` if any issues, `0` otherwise.

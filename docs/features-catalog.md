# Features catalog

Pełna lista funkcji platformy. Każda ma plik + przykład wywołania.

## Singletons

| Komponent | Plik | Po co |
|---|---|---|
| ACP pool | `module_23/acp_pool.py` | reuse połączenia Auggie, eliminuje cold-start subprocess |
| Skill registry | `module_24/skills_loader.py` | manifest L1 cache, leniwe L2/L3 |
| Cache | `module_23/caching.py` | LRU+TTL key=SHA256(prompt+model+opts) |
| Cost tracker | `module_23/cost_tracker.py` | rolling USD per tool/model |
| Circuit breaker | `module_23/resilience.py` | 5 fails / 60 s → open 120 s |

## 🟣 Concierge Web

`adk_training/module_23_auggie_integration/web/` — FastAPI + React/Vite.

```bash
python -m uvicorn adk_training.module_23_auggie_integration.web.app:app --port 8770 --reload
cd adk_training/module_23_auggie_integration/web/frontend && npm run dev
```

Routery: `/api/health`, `/api/tools`, `/api/tools/run` (SSE), `/api/cost`,
`/api/telemetry`, `/api/cache/clear`, `/api/index/start` (SSE), `/api/audit/*`
(mountowany z module_24).

## 🟢 MCP Server

`adk_training/module_23_auggie_integration/mcp_server.py` — 9 tools jako MCP server
do Claude Desktop / Cursor.

```bash
python -m adk_training.module_23_auggie_integration.mcp_server
```

## 🔵 ACP pool (opt-in)

`AUGGIE_USE_ACP=true` — reuse subprocess. Latency -200..400 ms na call.

```python
from adk_training.module_23_auggie_integration.acp_pool import get_acp
client = get_acp()           # singleton
result = client.run(prompt, opts)
```

## 🟡 LRU cache

`module_23/caching.py` — TTL 1 h domyślnie, klucz = SHA256(prompt+model+opts).
Skip rules: prompt zawiera `success_criteria` lub `functions` (nie cache'ujemy
randomized agentic loops).

```python
from adk_training.module_23_auggie_integration.caching import get_cache
get_cache().clear()                                          # /api/cache/clear
```

## 🟠 Resilience

`module_23/resilience.py` — retry z exponential backoff 1/2/4/8 s + circuit breaker
5 fails / 60 s → open 120 s. Decorator-friendly:

```python
from adk_training.module_23_auggie_integration.resilience import resilient

@resilient(max_retries=4, breaker_key="auggie")
def call_auggie(prompt: str) -> str: ...
```

## 🟣 Cost tracker

`module_23/cost_tracker.py` — `RATES_USD_PER_SEC` per model. Per-tool aggregation.

```python
from adk_training.module_23_auggie_integration.cost_tracker import tracker
tracker.snapshot()    # GET /api/cost
```

| Model | USD / sek |
|---|---|
| `gemini-2.5-flash` | ~0.000007 |
| `claude-sonnet-4.5` | ~0.000150 |

(Stawki w `cost_tracker.py` — aktualizuj per pricing change.)

## 🔴 Telemetry / health

`module_23/health_check.py` — standalone CLI (`--ping`, `--full`) + `/api/health`
endpoint zwraca CLI/session/breaker snapshot.

## 🟢 AuditOps planner + skills (module_24)

5 skilli OWASP + recon-helpers. Endpoint `/api/audit/skills` (L1),
`/api/audit/skills/{name}` (L2 + L3 listing). Patrz [AuditOps deep-dive](AuditOps/skills-pack.md).

## 🔵 Audit wiki + lint

`/api/audit/wiki` (lista per-target), `/api/audit/wiki/{slug}` (detail), CI:
`module_24/cli.py wiki-lint`.

## 🟡 Audit-History skill (V3)

Per-target dynamic skill — wstrzykuje historię wcześniejszych findings jako L2.
Kod: `wiki.history_skill_text()`.

## 🟢 CI mode (CLI + GitHub Action)

```bash
python -m adk_training.module_24_audit_ops.cli audit --target https://staging --ci
```

Plus `module_23/.github/workflows/ai-code-review.yml` — AI review każdego PR.

## 🟣 Cross-module hookups (planned / partial)

- `module_13_code_analyst` — skille progressive disclosure dla complexity/security/perf.
- `module_22_spec_generator` — skille user-story/acceptance/edge-cases.
- `module_09_database_*` — wiki per-schema (audit changes).
- `module_15_gmail_integration` — wiki per-thread (decyzje + akcje).

[Patterns →](patterns/index.md) tłumaczy *jak* je dodać.

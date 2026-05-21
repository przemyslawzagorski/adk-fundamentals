# ARCHITECTURE — Module 23: AI Code Concierge

> Production-grade integracja Google ADK (Gemini) + Augment Auggie SDK (Claude Sonnet 4.5)
> z pełnym stackiem niezawodności: cache, circuit breaker, retry, telemetry, cost tracking.

## Wysokopoziomowy obraz

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          USER / CLIENT                                   │
│   (ADK web UI │ MCP client │ GitHub Action │ CLI │ external API)         │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                ┌───────────────▼────────────────┐
                │   ai_code_concierge (LlmAgent) │  ◄── gemini-2.5-flash
                │   ROUTER / DISPATCHER          │      (tani orchestrator)
                └───────────────┬────────────────┘
                                │ tool calls
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
┌───────▼────────┐  ┌───────────▼──────────┐  ┌─────────▼────────┐
│ Production (6) │  │ Diagnostics (3)      │  │ MCP Server       │
│ code_review_pr │  │ auggie_telemetry     │  │ (stdio)          │
│ analyze_codebase│ │ auggie_cost_report   │  │ wrapper          │
│ generate_impl  │  │ auggie_health        │  └──────────────────┘
│ refactor_workfl│  └──────────────────────┘
│ security_audit │
│ ask_specialist │
└───────┬────────┘
        │ auggie_run() / auggie_call()
┌───────▼─────────────────────────────────────────────────────────────────┐
│                    AUGGIE FACTORY (single point of integration)          │
│  ┌──────────┐   ┌──────────────┐   ┌────────┐   ┌──────────┐   ┌─────┐ │
│  │  CACHE   │ → │ CIRCUIT BREAK│ → │ RETRY  │ → │ EXECUTE  │ → │ COST│ │
│  │ (LRU+TTL)│   │ (3 fail/60s) │   │(3x exp)│   │ (Auggie) │   │ + ML│ │
│  └──────────┘   └──────────────┘   └────────┘   └──────────┘   └─────┘ │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │
                  ┌─────────────────▼───────────────┐
                  │      AUGGIE SDK (Python)         │
                  │   ↓                              │
                  │   subprocess: auggie CLI (Node)  │
                  │   ↓                              │
                  │   Claude Sonnet 4.5 / Haiku /…   │
                  └──────────────────────────────────┘
```

## Komponenty

### 1. Router (Gemini 2.5 Flash) — `agent.py`
- Tani model decyzyjny (~$0.075/1M tok input).
- Wybiera narzędzie na podstawie intencji użytkownika.
- 9 narzędzi w `tools=[...]`.

### 2. Auggie Factory — `auggie_factory.py`
**Single point of integration.** Każde wywołanie Auggie idzie przez:
- `auggie_call(tool, extra_cli)` — context manager dla zaawansowanych przypadków (sesje).
- `auggie_run(tool, prompt, return_type, …)` — full-stack helper z cache/breaker/retry/cost.

Kluczowe klasy:
- `AuggieConfig.from_env()` — auto-detect CLI (`auggie.cmd`/`auggie.exe`), env config.
- `TelemetryStore` — globalny `TELEMETRY` z listą `CallStats`.
- `_build_listener()` — przechwytuje `on_tool_call`, `on_function_call`, `on_agent_message` z Auggie.

### 3. Cache — `caching.py`
- `AuggieCache` (LRU + TTL, thread-safe).
- Klucz: `SHA256(prompt | model | return_type | extra_cli)`.
- TTL domyślnie 1h, max 200 wpisów.
- **Bypass automatyczny** gdy `success_criteria` lub `functions` (wynik niedeterministyczny).
- Env: `AUGGIE_CACHE_ENABLED`, `AUGGIE_CACHE_TTL`, `AUGGIE_CACHE_MAX`.

```
                   ┌──────────────────┐
   prompt+model →  │  make_key (sha)  │ → "abc123…"
                   └────────┬─────────┘
                            │
            ┌───────────────▼─────────────┐
            │  if key in cache and !TTL: │ → HIT (saved_seconds += last_dur)
            │  else: MISS, run Auggie,   │
            │        put(key, value)     │
            └─────────────────────────────┘
```

### 4. Circuit Breaker — `resilience.py`
**Stany:** `closed → open → half-open → closed`.

```
   closed ──[3 failures w 60s]──► open
     ▲                              │
     │                              │ [60s reset timer]
     │                              ▼
     └──[1 success]──── half-open ◄─┘
                          │
                          └──[1 failure]──► open
```

- Chroni przed kaskadowymi błędami (np. Augment API down).
- W trybie `open` natychmiast rzuca `CircuitBreakerOpen` (nie marnuje czasu/pieniędzy).
- Env: `AUGGIE_BREAKER_THRESHOLD=3`, `AUGGIE_BREAKER_RESET_S=60`.

### 5. Retry — `resilience.py`
- Exponential backoff: 1s → 2s → 4s → 8s (cap), z jitter ±25%.
- Filter `is_retriable(exc)` — pomija auth/config errors (401, 403, AUGMENT_SESSION_AUTH).
- Default `max_attempts=3`.

### 6. Cost Tracker — `cost_tracker.py`
- Stawki domyślne (USD/sekunda CLI):
  - sonnet4.5: $0.012, sonnet4: $0.010, haiku4.5: $0.003, opus4.7: $0.060, gpt5: $0.020.
- Override: `AUGGIE_RATE_<model>` (np. `AUGGIE_RATE_sonnet4.5=0.015`).
- Cached wywołania = $0.

### 7. ACP Pool (opt-in) — `acp_pool.py`
- Singleton `AuggieACPClient` gdy `AUGGIE_USE_ACP=true`.
- Eliminuje cold start subprocess (~1-3s/call).
- Auto-restart przy crashy, `atexit.register(shutdown_acp)`.

### 8. Health Check — `health_check.py`
Walidacja: SDK import, CLI obecność, auth (`session.json` scopes ['read','write'] / `AUGMENT_SESSION_AUTH` / API key), workspace, model, google.adk.

```bash
python health_check.py        # static checks
python health_check.py --ping # + faktyczne wywołanie Auggie
```

### 9. MCP Server — `mcp_server.py`
Wystawia 9 narzędzi przez stdio dla **dowolnego MCP clienta** (Claude Desktop, Cursor, Cline).
Konfiguracja w `~/.config/Claude/claude_desktop_config.json`.

### 10. CI/CD — `ci_review.py` + `.github/workflows/ai-code-review.yml`
- Wywołane na każdym PR.
- Generuje diff `git diff origin/main...HEAD`.
- Wywołuje `code_review_pr` → komentarz na PR + fail build jeśli `severity >= --fail-on`.

## Decyzje architektoniczne

| Decyzja | Powód |
|---------|-------|
| Gemini Flash jako router, Claude jako worker | Flash = $0.075/1M input, Sonnet ~$3/1M. Router dla 80% zadań nie potrzebuje SOTA. |
| `auggie_run()` z wbudowanym cache/breaker/retry | Single point of failure → single point of resilience. |
| Cache bypass gdy `success_criteria`/`functions` | Auggie wtedy iteruje weryfikacją → wynik nie powinien być cache'owany. |
| Circuit breaker per-process (nie distributed) | Każdy proces = osobny worker; dystrybucję zostawiamy infra (np. Redis) na przyszłość. |
| MCP jako 2. interfejs | Re-use 9 narzędzi w Claude Desktop/Cursor bez kopiowania kodu. |
| ACP opt-in | Domyślnie subprocess (proste); ACP dla produkcji wysokorzutowej. |
| Brak full OpenTelemetry | YAGNI dla MVP; CallStats + JSON logs wystarczą. Łatwo dodać `OTEL_EXPORTER_OTLP_ENDPOINT` później. |

## Macierz "co kiedy używać"

| Scenariusz                           | Tool                       |
|--------------------------------------|----------------------------|
| Review PR diffa                      | `code_review_pr`           |
| Mapowanie nieznanego repo            | `analyze_codebase`         |
| Generacja kodu z testem akceptacyjnym| `generate_implementation`  |
| Wieloetapowy refactor                | `refactor_workflow`        |
| Audit security                       | `security_audit`           |
| Generic Q&A do Sonnet                | `ask_specialist` (cached!) |
| Diagnostyka produkcji                | `auggie_telemetry/cost/health` |

## Operations runbook

**Cold start zbyt wolny?** → włącz `AUGGIE_USE_ACP=true`.
**Wysokie koszty?** → przełącz `AUGGIE_MODEL=haiku4.5` dla `ask_specialist`.
**Augment API down?** → circuit breaker zatrzyma calls; sprawdź `auggie_telemetry()`.
**Cache hit rate niski?** → wydłuż `AUGGIE_CACHE_TTL`, zwiększ `AUGGIE_CACHE_MAX`.
**CI fałszywie failuje?** → zmień `--fail-on=critical` (zostaw major jako warning).

# Module 23 — Production-Ready ADK + Auggie SDK Integration

> **AI Code Concierge** — dwumodelowy system (Gemini jako tani dispatcher + Claude/Auggie jako drogi specjalista od kodu).
> Ten moduł **wykracza poza szkolenie** — to baza pod realne systemy.

---

## TL;DR

```
[User] → [ADK Gemini 2.5 Flash] →  decyzja: prosta odp. / delegacja
                                ↓
                       [Auggie SDK + Claude Sonnet 4.5]
                                ↓
                       (workspace, narzędzia, weryfikacja)
```

Gemini robi orchestrację (tanio, szybko). Claude robi ciężką robotę kodową (drogo, dokładnie).
**Płacisz za drogiego specjalistę tylko gdy faktycznie potrzebujesz.**

---

## Pliki

| Plik | Rola |
|---|---|
| `agent.py` | ADK agent (`root_agent`) — wystawia 9 tools, działa pod `adk web`. |
| `tools.py` | 6 tools produkcyjnych + 3 diagnostyczne (telemetria/koszty/health). |
| `auggie_factory.py` | Wspólna infrastruktura: config, telemetria, listener, `auggie_run()`. |
| `caching.py` | LRU+TTL cache dla powtarzalnych promptów (thread-safe). |
| `cost_tracker.py` | Real-time szacowanie kosztów USD per tool / per model. |
| `resilience.py` | Circuit breaker + retry z exponential backoff. |
| `acp_pool.py` | Singleton ACP client (opt-in, eliminuje cold-start subprocess). |
| `health_check.py` | Standalone healthcheck (`python health_check.py --ping`). |
| `mcp_server.py` | Wystawia 9 tools jako MCP server (Claude Desktop / Cursor). |
| `ci_review.py` + `.github/workflows/ai-code-review.yml` | GitHub Action: AI review na każdym PR. |
| `smoke_test.py` | E2E test 9 tools + cache + diagnostyka. |
| `ARCHITECTURE.md` | Pełna dokumentacja architektury z diagramami. |
| `BUSINESS_VALUE.md` | Pitch dla kierownictwa: ROI, KPI, use cases, risk. |
| `.env.template` | Wzorzec konfiguracji. |

---

## 9 narzędzi

### Produkcyjne (6)

| # | Tool | Funkcjonalność SDK | Realny use case |
|---|---|---|---|
| 1 | `code_review_pr` | `success_criteria` + dataclass return | Auto-review PR-ów w CI |
| 2 | `analyze_codebase` | `return_type=List[Finding]` (typed) | Onboarding dewelopera |
| 3 | `generate_implementation` | `success_criteria` + verification rounds | Scaffolding kodu spec→code |
| 4 | `refactor_workflow` | `auggie.session()` (kontekst między krokami) | Wieloetapowy refactor |
| 5 | `security_audit` | `functions=[...]` (Auggie woła nasze funkcje) | Audit z firmowymi skanerami |
| 6 | `ask_specialist` | Generic — z **cache** | Powtarzalne pytania Q&A |

### Diagnostyczne (3)

| # | Tool | Co pokazuje |
|---|---|---|
| 7 | `auggie_telemetry` | call stats, cache hits, breaker state, last 5 calls |
| 8 | `auggie_cost_report` | USD per tool / per model / total |
| 9 | `auggie_health` | SDK + CLI + auth + workspace + ADK |

---

## Stack niezawodności

Każde wywołanie Auggie idzie przez `auggie_run()`:

```
prompt → CACHE (LRU+TTL) → CIRCUIT BREAKER → RETRY (3x backoff) → AUGGIE → COST + TELEMETRY
           │                    │
        hit? skip               open? fail-fast (no waste $)
```

- **Cache** — domyślnie 1h TTL, max 200 wpisów. Bypass gdy `success_criteria`/`functions` (niedeterministyczne).
- **Circuit breaker** — 3 fail/60s → open → 60s reset → half-open → close.
- **Retry** — 1s/2s/4s/8s exp backoff + jitter; pomija auth/config errors.
- **Cost tracking** — env override per model: `AUGGIE_RATE_sonnet4.5=0.015`.

Szczegóły: [`ARCHITECTURE.md`](ARCHITECTURE.md).
Wartość biznesowa: [`BUSINESS_VALUE.md`](BUSINESS_VALUE.md).

---

## Setup

```powershell
# 1. Aktywuj venv (z pakietem auggie-sdk już zainstalowanym)
.\.venv312\Scripts\Activate.ps1

# 2. (opcjonalnie) Doinstaluj wymagania
pip install -r adk_training/module_23_auggie_integration/requirements.txt

# 3. Skonfiguruj .env (skopiuj z .env.template)
#    Najprostsze: ustaw AUGMENT_SESSION_AUTH (Service Account JSON).
#    Lub wypełnij ~/.augment/session.json — SDK go znajdzie automatycznie.
```

### Auth — opcje

**A. Service Account (zalecane dla enterprise)** — w `~/.augment/session.json`:
```json
{
  "accessToken": "eyJ...",
  "tenantURL": "https://e1-eu.api.augmentcode.com/",
  "scopes": ["read", "write"]
}
```

**B. Env var** w `.env`:
```env
AUGMENT_SESSION_AUTH={"accessToken":"...","tenantURL":"...","scopes":["read","write"]}
```

**C. API key** (jeśli Twoje konto pozwala na non-interactive CLI):
```env
AUGMENT_API_KEY=...
AUGMENT_API_URL=https://e1-eu.api.augmentcode.com/
```

---

## Uruchomienie

### Tryb interaktywny (ADK web UI)

```powershell
cd adk_training
adk web
# wybierz "module_23_auggie_integration" w UI
```

### Smoke test

```powershell
cd adk_training/module_23_auggie_integration
# Tryb diagnostyczny (bez Auggie API) — 3 testy: health/telemetry/cost.
python smoke_test.py --quick

# Real E2E (wymaga zalogowania `auggie auth login`).
# AUGGIE_USE_CLI=1 wymusza tryb subprocess `auggie --print` — szybki, niezawodny.
$env:AUGGIE_USE_CLI="1"; $env:AUGGIE_MODEL="sonnet4.5"
python smoke_test.py 6 7 8      # ask_specialist + cache + telemetry + cost
python smoke_test.py            # wszystkie 9 testów (cięższe)
```

> **Tryby wywołania Auggie**:
> - `AUGGIE_USE_CLI=1` (zalecane do produkcji prostych zapytań string-in/string-out):
>   subprocess `auggie --print --quiet --model X`. Działa dla `ask_specialist`,
>   nie obsługuje `success_criteria` / `functions` / dataclass returns.
> - Domyślnie (CLI=0): tryb ACP przez `auggie-sdk` — pełne return_type + functions
>   + success_criteria, ale long-running ACP server i większy narzut na cold start.

---

## Kluczowe decyzje projektowe

### 1. `auggie_factory.py` jako shared layer
- Jeden `AuggieConfig.from_env()` — wszystkie narzędzia czytają konfigurację identycznie.
- Context manager `auggie_call(tool_name)` — automatyczne zamykanie + telemetria.
- **Bez tego każdy tool 50 linii boilerplate.** Z tym — 5 linii.

### 2. Telemetria globalna
`TelemetryStore` zlicza wszystkie wywołania w procesie. W produkcji podmień na OpenTelemetry / Prometheus exporter — interfejs jest gotowy.

### 3. Listener jako klasa, nie callback
`TelemetryListener(AgentListener)` — można rozbudować o `on_agent_message`, `on_token_usage`, persist do DB.

### 4. Dataclass returns
`return_type=CodeReview` — SDK sam parsuje LLM output do strukturalnego obiektu. Nie ma JSON-parsing-roulette w naszym kodzie.

### 5. Error boundary
Każdy tool zwraca **string** (JSON lub tekst) z polem `error` przy fail. Agent nigdy nie crashuje.

---

## Pattern: function calling przez Auggie (`tool 5`)

Najciekawsza część — Auggie woła **nasze** funkcje (`scan_for_secrets`, `check_dependency_age`):

```python
def security_audit(target: str = ".") -> str:
    with auggie_call("security_audit") as auggie:
        return auggie.run(
            prompt,
            functions=[scan_for_secrets, check_dependency_age],  # ← tu
        )
```

To daje Auggie dostęp do **firmowych skanerów / API / baz danych** które tylko my mamy.
Pattern: agent ma swoje narzędzia (workspace, edit, run), MY dodajemy domain-specific.

---

## Production checklist

- [x] Telemetria (czas, success rate, cache hits, breaker state)
- [x] Real-time cost tracking (USD per tool/model, env override)
- [x] Circuit breaker (3 fail/60s → open → reset)
- [x] Retry z exponential backoff + jitter
- [x] LRU+TTL cache dla cacheable promptów
- [x] Health check standalone (`python health_check.py --ping`)
- [x] MCP server (Claude Desktop / Cursor / Cline)
- [x] GitHub Action CI (`ci_review.py`)
- [x] Persistent ACP client (opt-in: `AUGGIE_USE_ACP=true`)
- [x] Structured errors (każdy tool zwraca `error` field)
- [x] Auto-detect CLI (Windows `.cmd`, Linux/Mac `auggie`)
- [x] Multiple auth methods (session.json, env, api_key)
- [x] Workspace isolation (`AUGGIE_WORKSPACE` env var)
- [x] Timeout + max_turns (kontrola kosztów)
- [x] Architecture & business docs (`ARCHITECTURE.md`, `BUSINESS_VALUE.md`)

## Następne integracje

- OpenTelemetry exporter (interfejs `TelemetryStore` gotowy do wymiany)
- Distributed circuit breaker przez Redis (dla wielu workerów)
- JIRA/Linear context w `refactor_workflow` (ticket → cel refactoru)
- Self-service skill packs (zespoły dodają własne `success_criteria`)

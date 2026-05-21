# DEVELOPER GUIDE — Module 23 (Auggie Integration)

> **Cel:** uruchomić AI Code Concierge (Gemini router → Claude Sonnet 4.5 specialist via Auggie SDK)
> w 5 minut na lokalnej maszynie i wiedzieć, kiedy używać którego trybu.

---

## 1. TL;DR — który tryb wybrać

| Środowisko | Tryb | Komenda | Wsparcie funkcji |
|---|---|---|---|
| **Windows (lokalny dev)** | **`AUGGIE_USE_CLI=1`** (subprocess `--print --quiet`) | `..\..\.venv312\Scripts\python.exe smoke_test.py 6 7 8` | `return_type=str` only |
| **Linux / WSL / macOS** | **ACP (default)** — pełen SDK | `python smoke_test.py 6 7 8` (bez `AUGGIE_USE_CLI`) | `return_type=*`, `functions=[...]`, `success_criteria` |
| **CI/CD (GitHub Action)** | ACP na ubuntu-latest runner | `.github/workflows/ai-code-review.yml` | pełne |

**Reguła:** ACP daje najwięcej (typed returns, function-calling, success criteria, multi-turn verification),
ale na Windows wisi przez bug w spawnie `auggie.cmd` shimu npm. CLI fallback jest oficjalnie rekomendowany
w [auggie README](https://github.com/augmentcode/auggie) ("great for CI") i wystarcza dla 80% use-cases (string-in/string-out).

---

## 2. Wymagania

| Komponent | Wersja | Skąd |
|---|---|---|
| Python | 3.10+ (testowane: 3.12) | `uv venv --python 3.12` lub instalator z python.org |
| Node.js | 22+ | nodejs.org / NodeSource / `nvm` |
| `@augmentcode/auggie` (CLI) | 0.24+ | `npm install -g @augmentcode/auggie@latest` |
| `auggie-sdk` (Python) | 0.1.12+ | `pip install -r requirements.txt` |
| Service account session | enterprise-only | Augment Admin Console → Service Accounts → download `session.json` |
| Google Cloud SDK | dowolna | `gcloud auth application-default login` (dla Gemini routera) |

---

## 3. Setup w 4 krokach

### 3.1. Sklonuj i utwórz venv
```powershell
# Windows PowerShell
cd C:\path\to\adk-fundamentals
python -m venv .venv312
.\.venv312\Scripts\Activate.ps1
pip install -r adk_training\module_23_auggie_integration\requirements.txt
```

```bash
# Linux / macOS / WSL
cd ~/adk-fundamentals
uv venv --python 3.12 .venv         # lub: python3.12 -m venv .venv
source .venv/bin/activate
pip install -r adk_training/module_23_auggie_integration/requirements.txt
```

### 3.2. Zainstaluj Auggie CLI globalnie
```bash
npm install -g @augmentcode/auggie@latest
auggie --version    # powinno być >= 0.24.0
```

### 3.3. Skonfiguruj autentykację (service account — wymaganie produkcyjne)
1. **Admin Console** → [app.augmentcode.com/settings/service-accounts](https://app.augmentcode.com/settings/service-accounts)
2. **New Service Account** → wpisz nazwę (np. `adk-codeconcierge-prod`).
3. **Add API token** → pobierz `session.json` (jednorazowo).
4. Skopiuj do:
   - Windows: `C:\Users\<you>\.augment\session.json`
   - Linux/WSL: `~/.augment/session.json` (`chmod 600`)

Sanity check:
```bash
auggie --print "Reply: pong" --quiet --model sonnet4.5
# Oczekiwane: "pong\nRequest ID: <uuid>"
# Jeśli "❌ CLI non-interactive mode access has been disabled" — admin musi włączyć dla konta.
```

### 3.4. Skonfiguruj zmienne środowiskowe
`.env` w katalogu `module_23_auggie_integration/` (template w `.env.template`):
```bash
AUGGIE_MODEL=sonnet4.5
AUGGIE_TIMEOUT=180
AUGGIE_MAX_TURNS=3
AUGGIE_CACHE_ENABLED=1
AUGGIE_CACHE_TTL=3600
# Windows-only: aktywuje CLI fallback (workaround na bug ACP+.cmd shim)
AUGGIE_USE_CLI=1

# Opcjonalnie — Google Cloud dla Gemini routera (jeśli używasz `agent.py`)
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_CLOUD_PROJECT=your-project
GOOGLE_CLOUD_LOCATION=europe-central2
```

---

## 4. Uruchomienie

### 4.1. Smoke test (10 testów weryfikujących wszystkie warstwy)
```bash
cd adk_training/module_23_auggie_integration
python smoke_test.py              # wszystkie testy
python smoke_test.py 6 7 8        # wybrane: ask_specialist + telemetry + cost
python smoke_test.py --quick      # bez prawdziwych wywołań Auggie (CI lint)
```

Oczekiwany output dla `6 7 8` (po cache miss → cache hit):
```
[1st call] 11.30s
[2nd call] 0.00s   ✓ CACHE HIT confirmed (speedup 11937x)
DONE — 3/3 OK
```

### 4.2. Agent ADK (interaktywny)
```bash
adk web   # otworzy http://localhost:8080 → wybierz "module_23_auggie_integration"
```
Spróbuj prompty:
- "Wyjaśnij mi w 2 zdaniach co to dependency injection." → routuje do `ask_specialist`
- "Zrób review pliku ./tools.py pod kątem SOLID." → `review_code`
- "Wykryj sekrety w gałęzi `feature/xyz`." → `scan_secrets`
- "Wygeneruj plan refaktoryzacji dla tego modułu." → `plan_refactor`

### 4.3. CI — automatyczny review PR
Workflow w [`.github/workflows/ai-code-review.yml`](.github/workflows/ai-code-review.yml):
- trigger: `pull_request`
- runs `ci_review.py` → komentuje PR
- **secrets** GitHub: `AUGMENT_SESSION_AUTH` (cała zawartość `session.json` jako JSON string)

### 4.4. MCP server (IDE / inne LLM jako klient)
```bash
python mcp_server.py      # uruchamia stdio MCP exposing 9 tools
```
Konfiguracja w Claude Desktop / Cursor: `mcp.json` — patrz [README.md](README.md#mcp-integration).

---

## 5. Architektura w jednym diagramie

```
┌────────────────────────────────────────────────────────────────┐
│  ADK Agent (Gemini 2.5 Flash — tani router)                    │
│  ├─ ask_specialist          ┐                                  │
│  ├─ review_code             │                                  │
│  ├─ explain_concept         │  9 tools, każdy → auggie_run()  │
│  ├─ plan_refactor           │                                  │
│  ├─ scan_secrets            │                                  │
│  ├─ generate_tests          │                                  │
│  ├─ migrate_legacy          │                                  │
│  ├─ design_review           │                                  │
│  └─ auggie_telemetry        ┘                                  │
└────────────────────────────────────────────────────────────────┘
                  │
                  ▼
┌────────────────────────────────────────────────────────────────┐
│  auggie_factory.auggie_run()                                   │
│   1. Cache lookup (LRU + TTL + SHA256)         miss            │
│   2. Circuit breaker check (3 fail / 60s)      ok              │
│   3. Retry wrapper (3× exp backoff)                            │
│   4. ┌─────────────────┐    OR    ┌──────────────────────┐    │
│      │  ACP path       │          │  CLI path            │    │
│      │  (Linux/WSL)    │          │  (Windows fallback)  │    │
│      │  Auggie SDK     │          │  subprocess.run([    │    │
│      │  return_type=*  │          │   "auggie.cmd",      │    │
│      │  functions=[]   │          │   "--print",         │    │
│      │  success_crit=  │          │   "--quiet"])        │    │
│      └─────────────────┘          └──────────────────────┘    │
│   5. Telemetry + cost tracking + cache write                   │
└────────────────────────────────────────────────────────────────┘
                  │
                  ▼
┌────────────────────────────────────────────────────────────────┐
│  Auggie CLI (Node 22) → Augment Backend (e0-eu tenant)         │
│  → Claude Sonnet 4.5 (SOTA na coding tasks)                    │
└────────────────────────────────────────────────────────────────┘
```

---

## 6. Mapa plików

| Plik | Co robi |
|---|---|
| [`agent.py`](agent.py) | Definicja `LlmAgent` z 9 tools, instruction routera |
| [`tools.py`](tools.py) | 9 funkcji-narzędzi wywołujących `auggie_run()` |
| [`auggie_factory.py`](auggie_factory.py) | `AuggieConfig.from_env()` + `auggie_run()` (cache + breaker + retry + ACP/CLI switch) |
| [`caching.py`](caching.py) | LRU + TTL + SHA256-keyed cache |
| [`cost_tracker.py`](cost_tracker.py) | Per-model rates, agregacja USD |
| [`resilience.py`](resilience.py) | Circuit breaker + retry policy |
| [`acp_pool.py`](acp_pool.py) | Singleton pool `AuggieACPClient` (eksperymentalny) |
| [`health_check.py`](health_check.py) | Pre-flight: CLI present, session valid, model OK |
| [`mcp_server.py`](mcp_server.py) | MCP wrapper — eksponuje tools przez stdio JSON-RPC |
| [`ci_review.py`](ci_review.py) | Skrypt do GitHub Action (PR review) |
| [`smoke_test.py`](smoke_test.py) | 10 testów: cache, telemetry, cost, każde tool, --quick mode |

---

## 7. Konfiguracja w `auggie_factory.py`

```python
@dataclass
class AuggieConfig:
    model: str            # AUGGIE_MODEL (default sonnet4.5)
    timeout: int          # AUGGIE_TIMEOUT (default 180s)
    max_turns: int        # AUGGIE_MAX_TURNS (default 3 — niski koszt)
    workspace: Path       # AUGGIE_WORKSPACE (default = katalog modułu)
    api_key: str | None   # AUGMENT_API_KEY (fallback)
    api_url: str | None   # AUGMENT_API_URL (fallback)
    cli_path: str | None  # autodetected; override: AUGGIE_CLI_PATH
    has_session_auth: bool
```

**Lookup `cli_path` (od kwietnia 2026):**
- `AUGGIE_CLI_PATH` (explicit override) — najwyższy priorytet
- POSIX: `auggie` → `auggie.exe` → `auggie.cmd`
- Windows: `auggie.cmd` → `auggie.exe` → `auggie`
- WSL ostrzeżenie: jeśli `PATH` przecieka z Windowsa, `which auggie` może zwrócić `/mnt/c/.../auggie.cmd` co nie zadziała na Linuxie. Użyj `export AUGGIE_CLI_PATH=/usr/bin/auggie` lub `npm install -g @augmentcode/auggie` w WSL.

---

## 8. Troubleshooting

### 8.1. `OSError: [Errno 8] Exec format error: '.../auggie.cmd'` w WSL
**Przyczyna:** WSL dziedziczy Windows PATH; `which auggie` znajduje `.cmd` shim którego Linux nie wykona.
**Fix:** `sudo npm install -g @augmentcode/auggie@latest` w WSL, lub `export AUGGIE_CLI_PATH=/usr/bin/auggie`.

### 8.2. `TimeoutError` po 180s na Windows (ACP)
**Przyczyna:** Bug w `auggie-sdk` — spawn `auggie.cmd` w trybie persistent stdio (`--acp`) nie działa bez `shell=True`. Powiązane issues: [#88](https://github.com/augmentcode/auggie/issues/88), [#91](https://github.com/augmentcode/auggie/issues/91).
**Fix:** `set AUGGIE_USE_CLI=1` (PowerShell: `$env:AUGGIE_USE_CLI="1"`).

### 8.3. `403 Forbidden` / `Permission denied: HTTP error: 403`
**Przyczyna:** session token nieważny lub policy konta zablokowała non-interactive access.
**Fix:**
- Zweryfikuj `~/.augment/session.json` — `tenantURL` i `accessToken`.
- Jeśli to user account: zaloguj się ponownie `auggie login`.
- Jeśli to service account: skontaktuj się z adminem Augment, włącz "non-interactive CLI access".

### 8.4. `❌ CLI non-interactive mode access has been disabled for your account`
**Przyczyna:** policy administracyjna na tenancie.
**Fix:** Admin Console → Settings → Account Policies → enable "Non-interactive CLI". Wymaga Enterprise plan.

### 8.5. `RuntimeWarning: coroutine 'AuggieACPClient._async_stop' was never awaited`
**Przyczyna:** błąd zamykania ACP po wyjątku w `__init__`.
**Severity:** kosmetyczne (nie wpływa na wynik).
**Fix:** ignoruj lub upgrade `auggie-sdk`.

### 8.6. Cache nie hit'uje (`saved_seconds: 0.0`)
**Przyczyny:**
- `success_criteria` lub `functions` w wywołaniu — celowo pomijają cache (non-deterministic).
- `AUGGIE_CACHE_ENABLED=0` w env.
- Inny prompt (case-sensitive, whitespace, model).
**Fix:** sprawdź log `INFO: cache HIT for tool=...`.

---

## 9. Production checklist

- [ ] **Service account** (nie user account) w `~/.augment/session.json`
- [ ] **Token rotation policy** — co 90 dni nowy `session.json` przez Admin Console
- [ ] **Cost cap** — `AUGGIE_DAILY_USD_CAP` (TODO w `cost_tracker.py`)
- [ ] **Telemetria → observability** — pipe `auggie_telemetry()` do Prometheus / Datadog
- [ ] **Cache backend** — w prod replace in-memory na Redis (multi-instance)
- [ ] **Circuit breaker** monitoring — alert gdy `state=open` >5 min
- [ ] **Audit log** — każde wywołanie z `request_id` (z output Auggie) → log centralny
- [ ] **Rate limit** — per user/per repo (np. 100 calls/h)
- [ ] **PII scrubber** w `tools.py` — przed wysłaniem promptu do Augment

---

## 10. Linki

- Auggie SDK (PyPI): https://pypi.org/project/auggie-sdk/
- Auggie CLI (npm): https://www.npmjs.com/package/@augmentcode/auggie
- Service Accounts: https://docs.augmentcode.com/cli/automation/service-accounts
- ACP Protocol: https://agentclientprotocol.com/
- Issues GitHub: https://github.com/augmentcode/auggie/issues
- Reddit community: https://www.reddit.com/r/AugmentCodeAI/

---

> _Ostatnia aktualizacja: 2026-04-25. Empirycznie zweryfikowane: Windows 11 + Python 3.12 + auggie-sdk 0.1.12 + auggie CLI 0.24 (Windows) / 0.22 (WSL Ubuntu 20.04 + uv-managed Python 3.12)._

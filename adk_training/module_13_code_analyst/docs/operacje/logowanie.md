# Logowanie

Structured logging z `logging_config.py`. Dwa formaty: **JSON** (prod) i **plain** (dev).

## Konfiguracja

```env
CODE_ANALYST_LOG_FORMAT=json        # json | plain
CODE_ANALYST_LOG_LEVEL=INFO         # DEBUG | INFO | WARNING | ERROR
```

## Format JSON (prod)

Każda linia = jeden JSON, gotowy do Elastic/Loki/Stackdriver.

```json
{
  "timestamp": "2026-04-11T19:20:48.532Z",
  "level": "INFO",
  "logger": "web.app",
  "message": "Indexing completed",
  "request_id": "abc-def-123",
  "repo_id": "acme-xyz",
  "duration_ms": 34210,
  "indexed": 412,
  "skipped": 18
}
```

Pola stałe dodawane przez middleware:

- `request_id` — UUID v4 per-request.
- `path`, `method` — (w logach access).
- `status` — kod odpowiedzi.
- `duration_ms` — czas obsługi requestu.

## Format plain (dev)

```
2026-04-11 19:20:48 INFO     web.app: Indexing completed [req=abc-def-123 repo=acme-xyz indexed=412]
```

Czytelne dla człowieka, nie do scrapowania.

## Wyciszone biblioteki

W `logging_config.py`:

```python
for noisy in ("httpx", "httpcore", "urllib3", "google_genai",
              "llama_index", "llama_index.core.indices", "uvicorn.access"):
    logging.getLogger(noisy).setLevel(logging.WARNING)
```

Bez tego logi zalewa telemetria HTTP. `uvicorn.access` wyciszony, bo
dublujemy w own middleware.

## Request ID middleware

```python
@app.middleware("http")
async def request_id_middleware(request, call_next):
    rid = request.headers.get("x-request-id") or str(uuid.uuid4())
    request.state.request_id = rid
    with logging_contextvars.bind(request_id=rid):
        response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    return response
```

Implikacje:

- Klient może narzucić swój `X-Request-ID` (np. z ingress-a).
- Każdy log wewnątrz requestu ma `request_id` auto-dodany.
- ID wraca w odpowiedzi — klient może zalogować własną stronę.

## Co jest logowane

| Event | Level | Pola |
|-------|-------|------|
| Start requestu | INFO | path, method, ip |
| Koniec requestu | INFO | status, duration_ms |
| Index start | INFO | repo_id, incremental |
| Index done | INFO | indexed, skipped, duration_ms |
| Index error | ERROR | repo_id, exception |
| Agent step | DEBUG | agent_name, tool_name |
| Tool call | DEBUG | tool, args_summary |
| Tool error | WARNING | tool, reason |
| Auth fail | WARNING | endpoint, ip |
| Rate limit hit | WARNING | endpoint, ip, limit |
| Security violation | WARNING | type (path_traversal, secret_access, ...), ip |

## Co **NIE** jest logowane

- Treść prompts (prywatność + rozmiar).
- Zawartość odczytanych plików.
- API key (nigdy, w żadnym polu).
- ADC credentials.

!!! warning "Ścieżki absolutne w logach"
    Ścieżki do plików mogą zawierać nazwy użytkowników systemu (`/home/jan/...`).
    W strictniejszym środowisku dodaj redaction middleware — audyt: [M-8](../bezpieczenstwo/audyt.md).

## Korelacja logów i metryk

Rzeczywisty debug flow:

```
1. Grafana alert: p95 workflow > 60s
2. Grafana → klik → Loki/Elastic z filter: workflow_seconds > 60
3. Znajdź request_id konkretnego slow requestu
4. Grep logs: grep '"request_id":"xxx"' /var/log/analyst.log
5. Widzisz: jaki workflow, jakie toole, gdzie padł czas
```

Przykład slow request:

```json
{"ts":"...","level":"INFO","msg":"request start","request_id":"r1","path":"/repos/x/workflow"}
{"ts":"...","level":"DEBUG","msg":"tool call","request_id":"r1","tool":"search_code","query":"auth"}
{"ts":"...","level":"DEBUG","msg":"tool done","request_id":"r1","tool":"search_code","duration_ms":1800}
{"ts":"...","level":"DEBUG","msg":"tool call","request_id":"r1","tool":"read_project_file"}
{"ts":"...","level":"DEBUG","msg":"tool done","request_id":"r1","tool":"read_project_file","duration_ms":45000}
{"ts":"...","level":"INFO","msg":"request end","request_id":"r1","status":200,"duration_ms":48000}
```

Diagnoza: `read_project_file` zjadło 45s — pewnie zbyt duży plik + LLM czytanie.

## Log rotation

Aplikacja loguje do `stdout` / `stderr` — rotacja to rola platformy:

- Docker: `--log-driver json-file --log-opt max-size=100m --log-opt max-file=5`
- K8s: logi do Stackdriver/Loki przez DaemonSet.
- systemd: `journalctl`.

## Debugging konkretnego problemu

```powershell
# Uruchom lokalnie z pełnymi logami
$env:CODE_ANALYST_LOG_LEVEL = "DEBUG"
$env:CODE_ANALYST_LOG_FORMAT = "plain"
python -m uvicorn web.app:app --reload

# W drugim terminalu: test
curl -v http://localhost:8088/repos/xxx/search -d "query=abc" ...
# Header X-Request-ID: abc123

# Grep tylko tego requestu
Select-String "req=abc123" analyst.log
```

Następnie: [Rate limiting](rate-limiting.md).

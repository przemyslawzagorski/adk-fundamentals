# Troubleshooting

Katalog typowych problemów + diagnoza.

## Aplikacja nie wstaje

### `ValidationError: CODE_ANALYST_PORT`

```
pydantic.ValidationError: 1 validation error for Settings
port: ensure this value is less than or equal to 65535
```

**Fix:** Popraw `.env`, `CODE_ANALYST_PORT` musi być liczbą 1-65535.

### `ModuleNotFoundError: google.adk`

```
ModuleNotFoundError: No module named 'google.adk'
```

**Fix:** `pip install -r requirements.txt`. Sprawdź aktywny venv:

```powershell
Get-Command python
# powinien wskazywać .venv\Scripts\python.exe
```

### `OSError: [Errno 98] Address already in use`

Port zajęty.

**Fix:** zmień port lub zabij proces:

```powershell
# znajdź
Get-NetTCPConnection -LocalPort 8088 | Select-Object OwningProcess
Stop-Process -Id <pid>
```

## `/ready` zwraca 503

```json
{"ready":false,"project":null}
```

**Przyczyna:** brak konfiguracji LLM.

**Fix:**

=== "Gemini API"
    ```env
    GOOGLE_GENAI_USE_VERTEXAI=FALSE
    GOOGLE_API_KEY=twój-klucz
    ```

=== "Vertex AI"
    ```powershell
    gcloud auth application-default login
    ```
    ```env
    GOOGLE_GENAI_USE_VERTEXAI=TRUE
    GOOGLE_CLOUD_PROJECT=twój-projekt
    ```

## 401 Invalid API key

**Sprawdzenia:**

1. Czy `CODE_ANALYST_API_KEY` jest ustawione w `.env`?
2. Czy wysyłasz nagłówek `X-API-Key`?
3. Trailing whitespace w `.env` — usuń.
4. Nowa linia w headerze (`curl -H "X-API-Key: xxx "` — spacja!).

Test:

```powershell
curl -v -H "X-API-Key: $env:CODE_ANALYST_API_KEY" http://localhost:8088/health
# 401 == problem; 200 == OK
```

Szczegóły: [Autoryzacja — troubleshooting](../bezpieczenstwo/autoryzacja.md).

## Indeksacja "utyka"

**Objawy:** `/index/status` pokazuje "Indeksowanie w toku" > 5 min.

**Diagnoza:**

```powershell
# 1. CPU vs I/O
docker stats analyst
# wysokie CPU → LLM embed, normalne
# wysokie I/O → duże repo, normalne

# 2. Logi
docker logs analyst --tail 100
# szukaj "Skipped" / "OSError"
```

**Fixy:**

- Duże repo (>10k plików): skróć eksplorację przez `.gitignore`, zmniejsz `CODE_ANALYST_MAX_FILE_SIZE`.
- Za wolne embeddingi: rozważ zmianę `CODE_ANALYST_EMBED_MODEL` na lżejszy.
- Bardzo duże pliki (>1MB): domyślnie pomijane — sprawdź `skipped` w wyniku.

## Search zwraca pustkę

**Możliwe:**

1. **Indeks nie zbudowany** — po `/index` musi zakończyć się `state: done`.
2. **`similarity_cutoff` za wysoki** — obniż do `0.25`:
    ```env
    CODE_ANALYST_SIMILARITY_CUTOFF=0.25
    ```
3. **Nie pasująca query** — spróbuj po polsku i po angielsku (model embedding-owy jest multi-lingual, ale nie idealnie).
4. **Pliki pominięte** — sprawdź w stats `skipped` vs `indexed`.

## Agent "zmyśla"

**Objawy:** Odpowiedź nie zgadza się z kodem, ścieżki nieistniejące.

**Diagnoza:**

```powershell
# Włącz DEBUG — zobaczysz każdy tool call
$env:CODE_ANALYST_LOG_LEVEL="DEBUG"
python -m uvicorn web.app:app --reload
```

W logach szukaj:

- Czy agent wołał `search_code` i `read_project_file` przed odpowiedzią?
- Czy toole zwracały `ok: true`?
- Czy plik, o który pyta, **istnieje** w indeksie?

**Fixy:**

- Przeindeksuj pełnym indexem (`incremental=false`).
- Zwiększ `CODE_ANALYST_SIMILARITY_TOP_K` do 12 (więcej kontekstu).
- W UI podaj bardziej konkretne pytanie — "Gdzie jest klasa `UserService`?" > "Gdzie jest logowanie?".

## Workflow padł na `500`

```
{"error":"Blad agenta (zapisano w logach): ..."}
```

**Flow diagnostyczny:**

1. Zwróć uwagę na `X-Request-ID` w odpowiedzi.
2. `grep 'request_id":"<id>"' /var/log/analyst.log`.
3. Zobacz stacktrace — najczęstsze przyczyny:
    - **Rate limit Vertex/Gemini** (`ResourceExhausted`): poczekaj, rozważ quota increase.
    - **Auth LLM**: `DefaultCredentialsError` → `gcloud auth application-default login`.
    - **Tool error**: najczęściej `PathSecurityError` — legalne, agent źle prosił, ale błąd był łapany — sprawdź gdzie nie jest.

## 429 Too Many Requests

**Przyczyna:** przekroczony rate limit. Sprawdź `Retry-After`.

**Fix (deweloper):** poczekaj + nie spamuj `curl` w pętli.

**Fix (admin):** podnieś limity jeśli wielu użytkowników legitnie czeka — [Rate limiting](rate-limiting.md).

## Metryki — puste

**Objawy:** `/metrics` zwraca `# HELP ...` bez wartości.

**Przyczyna:** Nikt jeszcze nie użył endpointów. Histogramy mają wartości dopiero po pierwszym requeście.

**Fix:** Zrób jeden `/search` i odśwież.

## Docker compose: healthcheck failuje

```
Container code-analyst Health: unhealthy
```

**Diagnoza:**

```bash
docker inspect --format='{{json .State.Health}}' analyst | jq
```

Pokaże ostatnie 5 uruchomień healthcheck z exit kodami.

**Fixy:**

- App jeszcze się nie wstała → zwiększ `start_period` do 30s.
- Aplikacja wali 500 na `/health` → patrz logi.
- `curl` nie ma w obrazie — nasz healthcheck używa `python urllib`, nie curl, więc to nie dotyczy.

## Stale indeks po zmianach plików

**Objawy:** Po `write_project_file` agent dalej widzi stary kod.

**Fix:** `CodeIndexer` markuje plik dirty automatycznie w wrapperze zapisu, ale **musisz zrobić `/index` (incremental)** ponownie, żeby re-embed.

**Alternatywa:** auto-reindex po każdym zapisie — dodaj w wrapperze `write_file_wrapper` w `web/app.py` call `await _do_index(repo, incremental=True)`. Uwaga: to obciąża LLM.

## Pamięć rośnie

**Objawy:** Po kilku godzinach `code-analyst` zajmuje > 2GB.

**Możliwe:**

1. **Session leak** — sprawdź czy session cache się czyści (reset po jakimś czasie).
2. **LlamaIndex cache** — trzyma embeddings w RAM per-indexer. Dla wielu repo = suma.

**Fixy:**

- Ogranicz repliki do jednego repo albo zwiększ memory limit.
- Restart raz dziennie (systemd timer, K8s deployment restart).

## Diagnostic checklist

```powershell
# Health
curl http://localhost:8088/health
curl http://localhost:8088/ready

# Metrics
curl http://localhost:8088/metrics | Select-String "code_analyst"

# Logi ostatnie 1000 linii z pełnym levelem
docker logs --tail 1000 analyst

# CPU / memory
docker stats --no-stream analyst

# Process tree
docker exec analyst ps -ef
```

Jeśli żadne z powyższych nie pomaga — otwórz issue z:

- `X-Request-ID` problematicznego requestu,
- Fragment logów z tym ID,
- Wersja app (`/health` → `version`),
- ENV (wymaskuj klucze).

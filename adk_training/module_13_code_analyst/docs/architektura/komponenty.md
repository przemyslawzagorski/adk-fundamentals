# Komponenty

Cała logika domenowa żyje w ~10 plikach Pythona. Każdy ma jedną odpowiedzialność.

## Mapa modułów

| Moduł | Odpowiedzialność | Zależy od |
|-------|------------------|-----------|
| [`config.py`](#configpy) | walidacja + wczytywanie `.env` (Pydantic Settings) | — |
| [`logging_config.py`](#logging_configpy) | konfiguracja loggera JSON/plain, request-ID | — |
| [`security.py`](#securitypy) | `safe_resolve`, walidacja branchy, sanityzacja inputu | — |
| [`file_tools.py`](#file_toolspy) | read/write/list plików projektu (bezpiecznie) | security, logging_config |
| [`git_tools.py`](#git_toolspy) | `status`, `create_branch`, `commit`, `diff`, `log` | security, logging_config, config |
| [`build_tools.py`](#build_toolspy) | detekcja Maven/Gradle/Python/npm + `run_build` / `run_tests` | security, logging_config, config |
| [`code_indexer.py`](#code_indexerpy) | LlamaIndex: indeksacja, incremental, query | config, logging_config, security |
| [`code_retrieval_tool.py`](#code_retrieval_toolpy) | fabryka `FunctionTool` dla agenta | code_indexer |
| [`agent.py`](#agentpy) | `root_agent` dla trybu CLI (`adk web`) | wszystkie narzędzia |
| [`web/app.py`](#webapppy) | FastAPI app: routing, auth, cache, lifecycle | wszystko |

## `config.py`

**Pydantic Settings** z walidacją przy starcie. Wszystkie zmienne mają aliasy zgodne z konwencją `CODE_ANALYST_*` dla nowych oraz starsze nazwy (np. `GOOGLE_CLOUD_PROJECT`) dla kompatybilności.

Kluczowe pola (wybór):

```python
api_key: Optional[str] = Field(default=None, alias="CODE_ANALYST_API_KEY")
require_auth: bool = Field(default=False, alias="CODE_ANALYST_REQUIRE_AUTH")
port: int = Field(default=8088, alias="CODE_ANALYST_PORT")
chunk_size: int = Field(default=768, alias="CODE_ANALYST_CHUNK_SIZE")
similarity_cutoff: float = Field(default=0.35, ...)
rate_limit_index: str = Field(default="2/minute", ...)
```

Pełna lista: [Konfiguracja](../deweloper/konfiguracja.md).

`@lru_cache` daje singleton `get_settings()` — wczytujemy raz, wszędzie ta sama instancja.

## `logging_config.py`

- Format **JSON** (`CODE_ANALYST_LOG_JSON=true`) lub plain text do stdout.
- Idempotentna — można wołać wielokrotnie bez duplikacji handlerów.
- Wycisza hałaśliwe logi `httpx`, `urllib3`, `watchfiles` do `WARNING`.
- W `web/app.py` dopięte jest middleware dodające `X-Request-ID` do odpowiedzi.

Przykład logu JSON:

```json
{"time":"2026-04-17T10:54:14Z","level":"INFO","name":"code_analyst.web",
 "msg":"request","request_id":"a1b2","path":"/","method":"GET",
 "status":200,"duration_ms":12.3}
```

## `security.py`

### `safe_resolve(repo_path, relative_path)`

Rozwiązuje ścieżkę użytkownika do absolutnej, odrzucając wszystko co prowadzi poza repo. Kluczowe detale:

- `os.path.realpath` po **obu** stronach — rozpracowuje symlinki.
- Porównanie `candidate.startswith(repo_real + os.sep)` — zapobiega atakom typu `/repo` ⊂ `/repo-evil`.
- Odrzuca ścieżki absolutne, puste, z `\x00`.

### `validate_branch_name(name)`

Regex `^[A-Za-z0-9][A-Za-z0-9_./-]{1,99}$` + blacklist chronionych (`main`, `master`, `develop`, `release`, `production`, `prod`).

### `sanitize_user_input(text)`

Tnie do 2000 znaków, usuwa znaki kontrolne, escape'uje `{`/`}` (ochrona przed `.format()`).

### `is_secret_file(name)`

Lista plus reguła sufiksu — identyfikuje pliki typu `.env`, `*.pem`, `*.key`, `id_rsa` itp.

## `file_tools.py`

Trzy publiczne funkcje:

- `read_project_file(repo_path, file_path)` — odczyt (limit 50 000 znaków, obcięcie sygnalizowane).
- `write_project_file(repo_path, file_path, content)` — zapis (limit 2 MB, blokada sekretów, weryfikacja że katalog nie jest symlinkiem poza repo).
- `list_project_files(repo_path, directory, extensions)` — listing z filtrem, bez `_SKIP_DIRS` (`.git`, `node_modules`, `target`, …).

Każda zwraca `{"ok": bool, ...}` zamiast rzucać wyjątki — to kontrakt dla narzędzi ADK.

## `git_tools.py`

Wszystkie operacje używają `subprocess.run(..., shell=False, timeout=...)`:

| Funkcja | Co robi |
|---------|---------|
| `git_status(repo_path)` | `git status --porcelain`, lista zmian |
| `git_create_branch(repo_path, branch_name)` | walidacja → `git checkout -b` |
| `git_commit(repo_path, message)` | blokuje chronione branche, `git add -A && git commit -m` |
| `git_diff(repo_path, ...)` | diff workspace albo konkretnego pliku |
| `git_log(repo_path, limit)` | `git log --oneline -n <limit>` |
| `git_checkout_back(repo_path)` | powrót na poprzednią gałąź (`git checkout -` z fallback) |

Timeouty konfigurowalne w `config.py` (domyślnie 30 s).

## `build_tools.py`

Detektor build systemu: `pom.xml` → Maven, `build.gradle` → Gradle, `package.json` → npm, `setup.py`/`pyproject.toml` → Python.

`run_build`, `run_tests` — odpalają właściwą komendę z limitem timeoutu i cappingiem outputu (8 KB last).

`test_filter` (np. `-k testFoo`) jest **walidowany** pod kątem metaznaków powłoki — nie pozwalamy na wstrzykiwanie.

## `code_indexer.py`

Klasa `CodeIndexer` inkrementalna:

- pierwszy raz: chodzi po repo (z pominięciem sekretów), chunkuje przez `SentenceSplitter(chunk_size, chunk_overlap)`, wysyła do `GoogleGenAIEmbedding`, zapisuje `SimpleVectorStore` na dysku.
- kolejne razy: porównuje mtime plików z metadanymi → reindeksuje tylko zmienione.
- `mark_file_dirty(rel_path)` — usuwa metadane pliku, wymusza reindeks przy następnym `index_project`.
- `query(question, top_k)` — top-K z filtrem `similarity_cutoff` (domyślnie 0.35).
- `get_stats()` — pliki, chunki, katalog persist, cutoff.
- `reset_index()` — usuwa storage, zaczyna od zera.

## `code_retrieval_tool.py`

**Fabryka** `make_retrieval_tools(indexer) → list[FunctionTool]` — używana przez `web/app.py` (każde repo ma własny indeks).

Dodatkowo **cienkie wrappery CLI** (`search_code`, `index_project`, `get_index_stats`) — używa globalnego singletona skonfigurowanego przez `CODE_PROJECT_DIR` / `CODE_INDEX_DIR`. Tylko dla trybu `adk web`.

## `agent.py`

`root_agent` — pojedynczy `LlmAgent` z pełnym zestawem narzędzi dla `adk web` (tryb jednego promptu/odpowiedzi). W web UI używamy bardziej rozbudowanego pipeline (patrz `web/app.py`).

## `web/app.py`

Największy plik (~800 linii), ale o jasnej strukturze:

```
1.  Importy + path setup
2.  Settings + logger + Prometheus (idempotentna rejestracja)
3.  Definicja workflow'ów (WORKFLOWS dict)
4.  Fabryki: _get_indexer, _get_runner, _invalidate_runners
5.  _build_sequential_agent — definicja agentów i promptów
6.  _run_agent_pipeline — pętla po zdarzeniach Runnera
7.  Lifespan (startup/shutdown) — persist indeksów
8.  Middleware: request-ID, CORS, rate limiting, auth
9.  Publiczne endpointy: /health /ready /metrics
10. Endpointy HTML: / /repos /repos/{id}
11. Endpointy funkcjonalne: /index /search /chat /workflow
12. __main__: uvicorn.run
```

## Następny krok

- [Przepływ danych](przeplyw-danych.md) — sekwencja request/response.
- [Workflows](workflows.md) — definicja scenariuszy.

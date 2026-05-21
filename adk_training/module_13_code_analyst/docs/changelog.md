# Historia zmian

Wszystkie istotne zmiany aplikacji Code Analyst. Format: [Keep a Changelog](https://keepachangelog.com/pl/1.1.0/).

## [1.1.0] — Dokumentacja + timing-safe auth

### Security

- **C-9 (CRITICAL): Timing attack na porównaniu API key** — zastąpione `hmac.compare_digest` w `_require_api_key`. Odporność na enumeration przez pomiar czasu.

### Added — dokumentacja MkDocs

- Pełna dokumentacja dla 3 person (biznes / deweloper / ekspert) w `docs/`.
- 6 sekcji: Start, Dla biznesu, Architektura, Bezpieczeństwo, Dla dewelopera, Operacje, Dla eksperta, Historia.
- Mermaid diagrams, admonitions, code tabs, cards grid.
- `mkdocs.yml` z Material theme, polska lokalizacja.
- [Autoryzacja krok po kroku](bezpieczenstwo/autoryzacja.md) — 8 etapów z sequence diagram.
- [Pełny raport audytu](bezpieczenstwo/audyt.md) — 37 znalezisk z statusami.

## [1.0.0] — Production-readiness (4 sprinty)

Duża rekompozycja z modułu szkoleniowego na aplikację produkcyjną. Szczegóły w [audycie](bezpieczenstwo/audyt.md).

### Sprint 1 — Security foundation

#### Added

- `security.py` z `safe_resolve`, `sanitize_user_input`, `is_secret_file`, `validate_branch_name`.
- `tests/test_security.py` — 20+ testów bezpieczeństwa.
- `_file_metadata` w `CodeIndexer` do detekcji zmian (inkrementalna indeksacja).

#### Fixed

- **C-1**: Path traversal w file_tools (realpath + os.sep check).
- **C-5**: Subprocess injection w `run_tests` (shell=False hardcoded + regex walidacja filter-a).
- **C-6**: Sekrety (.env, *.pem, *.key, credentials) — blokada read/write/index/list.
- **C-7**: Prompt injection — separacja `system_hint` i `user_message` jako osobne Parts + sanityzacja.
- **C-8**: Stale indeks — `mark_file_dirty()` po write.

### Sprint 2 — ADK correctness + RAG tuning

#### Added

- Konfigurowalne `chunk_size`, `chunk_overlap`, `similarity_cutoff`, `similarity_top_k`, `max_file_size` przez ENV.
- `code_retrieval_tool.make_retrieval_tools(indexer)` — fabryka narzędzi per repo.
- `sequential_agent.SequentialAgent` używany w workflowach.
- 3-warstwowa instrukcja agenta (polska): CodeAnalyst, Architect, Developer.

#### Fixed

- **C-2**: Race condition na indeksach → `asyncio.Lock` per-repo.
- **H-2**: Agent nie improwizuje na `ok: false` — explicit instruction.
- **H-3**: Singleton CodeIndexer → fabryka per repo.
- **H-8**: Session leak — globalny `SessionService`, cache per (repo, mode).
- Rozdzielenie `user_message` i `system_hint` jako osobne `types.Part` zamiast concat/format.

### Sprint 3 — Operability

#### Added

- Endpointy `/health`, `/ready`, `/metrics` (Prometheus).
- Histogramy: `code_analyst_{index,search,workflow}_seconds`.
- Countery: `code_analyst_errors_total`, `code_analyst_rate_limited_total`.
- SlowAPI rate limiting per-IP per-endpoint (konfigurowalne).
- `logging_config.py` — JSON/plain format, request-ID middleware.
- `config.py` — Pydantic Settings z walidacją.
- `lifespan` — graceful shutdown z persist indeksu.

#### Fixed

- **C-3**: XSS w outputie agenta — DOMPurify 3.1.6, usunięcie `| safe`.
- **C-4**: Blocking I/O — `asyncio.to_thread` dla indeksacji.
- **H-5**: Structured logging (był `print()`).
- **H-7**: SIGTERM + persist na shutdown.

### Sprint 4 — Packaging + CI

#### Added

- `Dockerfile` multi-stage, non-root user, HEALTHCHECK wbudowany.
- `.dockerignore`.
- `docker-compose.yml` z volume na indeksy, ENV z `.env`, healthcheck.
- `.github/workflows/code-analyst.yml` — ruff + pytest + docker build.
- `requirements.txt` z pinami (`google-adk>=1.28.0,<2.0.0`).
- `.env.template`.

#### Fixed

- **M-2, M-4, M-7**: Docker/CI + healthcheck + `.dockerignore`.
- **L-2**: Pinowanie zależności.

## Status finalny (po rekompozycji)

- **Testy**: 50+ zielonych, 1 skipped (symlinki na Windows).
- **Coverage bezpieczeństwa**: security ~95%, file_tools ~90%.
- **Audyt**: 29 CRIT/HIGH fixed, 4 mitigated, 4 świadomy trade-off.
- **Docker obraz**: ~450 MB (python:3.11-slim base).
- **Start-up time**: ~3s lokalnie, ~8s w Docker (cold).
- **Memory baseline**: ~200MB + ~50MB/repo (zindeksowany 1000-plikowy projekt).

## Planowane — backlog

Zobacz [audyt → backlog](bezpieczenstwo/audyt.md).

- OAuth/OIDC jako alternatywa dla API key.
- Shared vector store (Qdrant/Weaviate) dla multi-node.
- Per-user audit trail.
- Budżet tokenów per repo/workflow.
- MCP integration (Jira, GitHub PR draft).
- GPG signing commit-ów agenta.

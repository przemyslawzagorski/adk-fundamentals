# Przegląd architektury

Code Analyst to **monolit w Pythonie** z trzema warstwami: **web (FastAPI)**, **agent runtime (ADK)** i **stan per-repo** (indeks RAG + pliki + git).

## Widok C4 — poziom kontekstu

```mermaid
flowchart TB
    U[Deweloper / PM] -->|HTTP + API key| CA[Code Analyst Web UI]
    CA -->|embeddings| GE{{Google GenAI<br/>text-embedding-005}}
    CA -->|LLM calls| GL{{Google GenAI<br/>Gemini}}
    CA -->|git, fs| R[(Repozytorium<br/>użytkownika)]
    CA -->|logi JSON + /metrics| O[(Observability<br/>Prometheus / stdout)]
```

## Widok C4 — poziom kontenerów

```mermaid
flowchart TB
    subgraph "Kontener: code-analyst"
      direction TB
      W[FastAPI<br/>web/app.py]
      S[Settings<br/>config.py]
      L[Logger<br/>logging_config.py]
      subgraph "Runtime ADK"
        RN[Runner]
        SA[SequentialAgent]
        A1[LlmAgent: Analyst]
        A2[LlmAgent: Reviewer/Impl]
      end
      subgraph "RAG"
        CI[CodeIndexer]
        LI[(LlamaIndex<br/>SimpleVectorStore)]
      end
      subgraph "Narzędzia"
        FT[file_tools]
        GT[git_tools]
        BT[build_tools]
        RT[code_retrieval_tool]
      end
      SEC[security.py]
    end
    W --> S
    W --> L
    W --> RN
    RN --> SA
    SA --> A1
    SA --> A2
    A1 --> RT
    A2 --> FT
    A2 --> GT
    A2 --> BT
    CI --> LI
    RT --> CI
    FT --> SEC
    GT --> SEC
    BT --> SEC
```

## Diagram sekwencji: od pytania do odpowiedzi

```mermaid
sequenceDiagram
    participant U as Użytkownik
    participant W as FastAPI
    participant MW as Auth + RateLimit
    participant AR as AsyncLock per repo
    participant R as Runner (ADK)
    participant A as SequentialAgent
    participant T as Tools (RAG/Git/Fs)
    participant M as Prometheus

    U->>W: POST /repos/{id}/workflow
    W->>MW: X-API-Key + rate check
    MW-->>W: OK
    W->>AR: asyncio.Lock(repo_id)
    AR-->>W: acquired
    W->>R: get_or_create Runner
    R->>A: run(system_hint + user_message)
    A->>T: search_code("...")
    T-->>A: wyniki
    A->>T: read_project_file("...")
    T-->>A: zawartość
    A-->>R: propozycja
    R-->>W: odpowiedź
    W->>M: observe(workflow_seconds)
    W-->>U: HTML/JSON + request-ID
    W->>AR: release
```

## Kluczowe decyzje architektoniczne (ADR-skrót)

### ADR-1: Multi-tenant per-repo z `asyncio.Lock`

**Decyzja**: Każde repo ma własny `CodeIndexer`, `Runner` i `asyncio.Lock`. Cache jest per-proces (in-memory).
**Powód**: Ten sam indeks nie może być modyfikowany równolegle (LlamaIndex nie jest thread-safe). Lock per-repo pozwala na równoległą pracę na różnych repo.
**Konsekwencja**: Jeden proces = jeden shard. Skalowanie horyzontalne wymaga load balancera z sticky session po `repo_id`.

### ADR-2: `SequentialAgent` zamiast jednego `LlmAgent`

**Decyzja**: Workflow'y w trybie implementacja używają `SequentialAgent([Analyst, Reviewer])`.
**Powód**: Rozdzielenie odpowiedzialności — jeden agent analizuje, drugi implementuje. Mniej halucynacji.
**Konsekwencja**: Podwójne koszty LLM za workflow, ale wyższa jakość.

### ADR-3: `user_message` jako osobny `types.Part`

**Decyzja**: Wejście użytkownika NIE jest wstrzykiwane do instrukcji agenta przez `.format()` — przekazujemy je jako osobną część wiadomości.
**Powód**: Ochrona przed prompt injection (użytkownik nie może „uciec" z nawiasu klamrowego).
**Konsekwencja**: Jeden layer promptu + jeden layer danych.

### ADR-4: Brak własnej bazy danych

**Decyzja**: Stan trzymamy w plikach na wolumenie (`web_data/indices/<repo_id>/`). Bez Postgres/Redis.
**Powód**: Prostota wdrożenia, brak zewnętrznych zależności. Indeksy RAG są deterministyczne (można przeliczyć).
**Konsekwencja**: Brak multi-node out-of-the-box. Dla kilku instancji: sticky session + wspólny NFS, lub migracja do zewnętrznego vector store.

### ADR-5: FastAPI + HTMX zamiast SPA

**Decyzja**: Jeden proces, serwerowy render HTML, aktualizacje częściowe przez HTMX.
**Powód**: Brak build pipeline, prostszy deployment, mniej powierzchni ataku (XSS).
**Konsekwencja**: Ograniczona interaktywność UI. Wystarczająca dla narzędzia wewnętrznego.

## Granice systemu

Co jest **wewnątrz** Code Analyst:

- Indeksacja kodu (LlamaIndex SimpleVectorStore, plik na dysku).
- Pipeline agentowy (ADK `Runner` + `SequentialAgent`).
- Interfejs web (FastAPI + szablony Jinja2).
- Metryki Prometheus, logi JSON, health checks.

Co jest **na zewnątrz**:

- Model embeddingów (Google GenAI albo Twój wybór).
- Model LLM (Gemini / inny skonfigurowany).
- Reverse proxy (nginx/Traefik) — zalecane w produkcji dla TLS.
- Prometheus, Grafana, Alertmanager — obserwowalność.
- Wolumen z repo źródłowymi (bind mount albo copy-in).

## Następny krok

- [Komponenty szczegółowo](komponenty.md) — co robi każdy moduł Pythonowy.
- [Przepływ danych](przeplyw-danych.md) — jak dokładnie płynie request.
- [Workflows](workflows.md) — jak zbudowane są scenariusze.

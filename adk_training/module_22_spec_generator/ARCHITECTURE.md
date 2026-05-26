# Architektura — Spec Generator (M22)

> Produkcyjny system "ticket Jira → HLD + Epiki" zbudowany na Google ADK.
> Ten dokument opisuje **jak** to dziala — od warstwy agentowej, przez API REST/SSE,
> az po frontend React i flow Human-in-the-Loop.

---

## 1. Mapa systemu

```
┌──────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Vite + React)                      │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────────────────┐  │
│  │ GenerateForm │ → │   Timeline   │ → │ HldView + EpicsList      │  │
│  └──────────────┘   └──────────────┘   │ (HITL inline edit)       │  │
│         │                  ▲           └──────────────────────────┘  │
│         │ POST              │ SSE events                  │          │
│         │ /api/generate     │ /api/generate/stream        │          │
│         ▼                  │                              ▼          │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │                  ActionsBar  (Save / Publish / Export)       │    │
│  └──────────────────────────────────────────────────────────────┘    │
└──────────────────────────────┬───────────────────────────────────────┘
                               │   REST + SSE
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                       BACKEND (FastAPI, port 8766)                   │
│  /health   /api/generate(stream)   /api/sessions/{id}                │
│  /api/sessions/{id}/export.{md,json}   /api/publish/{id}             │
│                              │                                       │
│                              ▼                                       │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                ADK Runner (per-session)                        │  │
│  │   InMemorySessionService + InMemoryArtifactService             │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────┬───────────────────────────────────────┘
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     ADK Pipeline (SequentialAgent)                   │
│                                                                      │
│   ticket_fetcher → context_parallel → hld_writer → critique_loop     │
│        │                │                │              │            │
│        ▼                ▼                ▼              ▼            │
│   Jira MCP        Wiki+GitLab+NLM   Gemini 2.5    Critic↔Reviser     │
│   (LLM agent)      (ParallelAgent)   (writer)      (LoopAgent)       │
│                                                          │            │
│                                                          ▼            │
│                                                   epic_decomposer     │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 2. Warstwa agentowa (ADK)

### 2.1 Top-level `SequentialAgent` — `spec_generator`

Definicja w [agents/spec_generator.py](agents/spec_generator.py).

Pipeline w stalej kolejnosci:

| # | Sub-agent           | Typ              | Wejscie (state)                  | Wyjscie (state key)        |
|---|---------------------|------------------|----------------------------------|----------------------------|
| 1 | `ticket_fetcher`    | `LlmAgent`       | `issue_key`                      | `ticket_payload` (JSON)    |
| 2 | `context_parallel`  | `ParallelAgent`  | `ticket_payload`                 | `wiki_ctx`, `code_ctx`, `nlm_ctx` |
| 3 | `hld_writer`        | `LlmAgent`       | `ticket_payload + *_ctx`         | `hld_markdown`             |
| 4 | `critique_loop`     | `LoopAgent`      | `hld_markdown`                   | `hld_markdown` (po N iter), `critique` |
| 5 | `epic_decomposer`   | `LlmAgent`       | `hld_markdown`                   | `epics` (list[dict])       |

### 2.2 `context_parallel` — `ParallelAgent`

Trzy rownolegle podagenty zbierajace kontekst:

- `wiki_searcher` (Confluence MCP) → `state["wiki_ctx"]`
- `code_searcher` (GitLab MCP)     → `state["code_ctx"]`
- `nlm_advisor`   (NotebookLM tool, opcjonalny) → `state["nlm_ctx"]`

ParallelAgent czeka az wszyscy skoncza i scala state przed `hld_writer`.

### 2.3 `critique_loop` — `LoopAgent`

```
   ┌────────────────────────────────────────┐
   │                                        ▼
critic_agent  →  reviser_agent  →  exit_check (gate)
   │  (output_key=critique)             │ (escalate=true → break)
   └────────────────────────────────────┘
   max_iterations = 2 (default; configurable via SPEC_GEN_MAX_CRITIQUE_ITER)
```

`critic_agent` ocenia `hld_markdown`, `reviser_agent` poprawia i nadpisuje
`state["hld_markdown"]`. Po `max_iterations` lub po decyzji `escalate=true`
loop konczy sie i wynik trafia do `epic_decomposer`.

### 2.4 HITL + `jira_publisher` (poza pipeline)

`jira_publisher` celowo NIE jest w `SequentialAgent`. Czlowiek:

1. Otrzymuje preview (HLD + epiki) w UI
2. Edytuje epiki (PUT /api/sessions/{id})
3. Klika **Approve & Publish** → osobny endpoint `POST /api/publish/{id}`
4. Backend wola `jira_publisher` (gdy MCP podlaczone) lub zwraca scaffold

Dzieki temu LLM **nigdy nie pisze do Jira bez akceptacji czlowieka**.

---

## 3. Warstwa API (FastAPI)

Plik: [web/app.py](web/app.py).

### 3.1 Endpointy

| Metoda | Path                                    | Cel                                         |
|--------|-----------------------------------------|---------------------------------------------|
| GET    | `/health`                                | Liveness + flagi (`real_pipeline`)          |
| POST   | `/api/generate`                          | Sync run (zwraca finalny JSON)              |
| POST   | `/api/generate/stream`                   | **SSE** — eventy live progress              |
| GET    | `/api/sessions/{id}`                     | Odczyt sesji (HLD + epiki + status)         |
| PUT    | `/api/sessions/{id}`                     | Zapis edycji HITL                           |
| GET    | `/api/sessions/{id}/export.md`           | Download Markdown                           |
| GET    | `/api/sessions/{id}/export.json`         | Download JSON                               |
| POST   | `/api/publish/{id}`                      | Approve & publish (zapisuje `edited_epics`) |

### 3.2 SSE — protokol eventow

Nazwa eventu w `event:` header, payload w `data:` (JSON).

```
event: session         { session_id, mode: "real" | "scaffold" }
event: stage_start     { stage, ts, iteration? }
event: stage_event     { stage, preview }
event: stage_end       { stage, ts }
event: done            { hld_markdown, epics, iterations }
event: end             {}
event: error           { message }
```

Stage keys odpowiadaja sub-agentom (`ticket_fetcher`, `context_parallel`,
`hld_writer`, `critique_loop`, `epic_decomposer`). W trybie scaffold wysylane
sa cztery sztuczne stage'y z `asyncio.sleep` do testowania UI.

### 3.3 Sesje w pamieci

`_SESSIONS: dict[str, dict]` trzyma:

```python
{
  "hld_markdown": str,
  "epics": list[dict],
  "approved": bool,
  "mode": "real" | "scaffold",
  "events_log": list[dict],   # historia SSE do replay
}
```

> **Uwaga produkcyjna:** w wersji production-ready trzeba zamienic
> `_SESSIONS` na Redis/Postgres + TTL. Obecnie sesje gina po restarcie.

### 3.4 CORS

`CORSMiddleware` zezwala na `http://localhost:5173` (Vite dev).
W produkcji UI serwowane jest z tej samej origin (`/dist`) — CORS niepotrzebne.

---

## 4. Warstwa frontend (React + Vite)

### 4.1 Stack

| Pakiet               | Wersja  | Cel                              |
|----------------------|---------|----------------------------------|
| Vite                 | 5.4     | dev server + bundler             |
| React                | 18.3    | UI                               |
| TypeScript           | 5.6 strict | typowanie                     |
| Tailwind CSS         | 3.4     | styling utility-first            |
| shadcn/ui (Radix)    | —       | komponenty (Button, Card, Input) |
| TanStack Query       | 5.59    | stan serwerowy (zaczatek)        |
| react-markdown       | 9.x     | render HLD                       |
| lucide-react         | 0.460   | ikony                            |

### 4.2 Struktura

```
web/frontend/src/
├── api/
│   ├── client.ts       # REST: generate, saveEdits, publish, exportUrl
│   └── stream.ts       # SSE parser (fetch + ReadableStream)
├── hooks/
│   └── use-generate-stream.ts   # state machine (reducer + AbortController)
├── components/
│   ├── ui/             # shadcn primitives
│   ├── app-header.tsx
│   ├── theme-provider.tsx + theme-toggle.tsx
│   ├── generate-form.tsx
│   ├── timeline.tsx    # live progress per stage
│   ├── hld-view.tsx    # markdown z prose-spec
│   ├── epics-list.tsx  # read + inline EpicEditor
│   ├── actions-bar.tsx # Save / Publish / Export
│   └── toast.tsx       # ToastProvider + useToast
├── pages/Dashboard.tsx
├── App.tsx             # QueryClient + Theme + Toast
└── main.tsx
```

### 4.3 Stan i flow danych

- **Streaming** zarzadza `useGenerateStream` (reducer): SSE → `applyEvent` →
  state z `stages[]`, `result`, `mode`, `iterations`, `error`.
- **HITL edit:** `Dashboard` trzyma lokalna kopie `editedEpics` + `savedSnapshot`.
  `dirty = JSON.stringify(editedEpics) !== savedSnapshot`. Po `saveEdits`
  snapshot jest aktualizowany.
- **Akcje** sa w `ActionsBar`: kazda async wola toast (success/error).
  Eksport MD/JSON dziala przez wirtualny `<a download>`.

### 4.4 Vite proxy (dev)

`vite.config.ts` proxuje `/api/*` i `/health` na `http://127.0.0.1:8766`,
zeby frontend (5173) gadal z backendem bez CORS preflight.

---

## 5. Tryby pracy

### 5.1 Scaffold mode (default w dev)

- Wlacza sie gdy brak `SPEC_GEN_USE_REAL_PIPELINE=1` lub brak `GOOGLE_CLOUD_PROJECT`
- Backend zwraca placeholdery + symuluje 4 stage'y SSE z `asyncio.sleep(0.5)`
- UI dziala identycznie — testy E2E nie wymagaja Vertex AI

### 5.2 Real mode

Wymaga zmiennych:

```
GOOGLE_CLOUD_PROJECT=<gcp-project>
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_LOCATION=europe-west1   # lub global; vide /memories/repo
SPEC_GEN_USE_REAL_PIPELINE=1
SPEC_GEN_MAX_CRITIQUE_ITER=2
```

Opcjonalne MCP (gdy podlaczone):

```
JIRA_MCP_URL=...
CONFLUENCE_MCP_URL=...
GITLAB_MCP_URL=...
NOTEBOOKLM_API_KEY=...
```

---

## 6. Decyzje techniczne (ADR-light)

| Decyzja                                        | Powod                                                                 |
|------------------------------------------------|-----------------------------------------------------------------------|
| `SequentialAgent` zamiast wlasnego orkiestratora | wbudowane state-passing przez `output_key`, mniej kodu              |
| `ParallelAgent` dla kontekstu                  | wiki+code+NLM sa niezalezne → 3x szybciej                              |
| `LoopAgent` z `escalate=true` exit             | pozwala critic-owi przerwac wczesniej gdy HLD jest OK                 |
| HITL **poza** pipeline                         | LLM nigdy nie publikuje bez akceptacji czlowieka                      |
| SSE zamiast WebSocket                          | one-way progress; prostsze (fetch + ReadableStream), zero zaleznosci  |
| In-memory sesje (`_SESSIONS`)                  | MVP — production: Redis + TTL                                          |
| Vite + Tailwind + shadcn                       | zero runtime CSS-in-JS, mala bundle, accessibility z Radix            |
| Frontend bez routera                           | jedna strona = jeden flow; rozszerzenie pojdzie z React Router        |

---

## 7. Roadmap produkcyjna

- [ ] Persistent sessions (Redis + TTL 24h)
- [ ] Auth (OAuth2 / IAP) + audit log publish'ow
- [ ] Real `jira_publisher` po podlaczeniu Comarch MCP (rotate tokens!)
- [ ] Diff view miedzy iteracjami critique
- [ ] Bulk export (zip wielu sesji)
- [ ] Metrics (Prometheus): generate_seconds, epics_count, publish_total
- [ ] Frontend tests (Vitest + Testing Library)
- [ ] Backend integration tests (pytest + httpx, real LLM stub)
- [ ] Deployment: Cloud Run (backend) + Cloud CDN (frontend dist)

---

## 8. Quick start

```bash
# 1. Backend
cd adk_training/module_22_spec_generator
python -m web.app                # port 8766

# 2. Frontend (osobny terminal)
cd web/frontend
npm install
npm run dev                       # port 5173

# 3. Otworz http://localhost:5173
```

Real mode: ustaw env (`SPEC_GEN_USE_REAL_PIPELINE=1` + GCP) przed `python -m web.app`.

---

*Ostatnia aktualizacja: Faza D refactor → produkcyjny stack (Vite + SSE + HITL).*

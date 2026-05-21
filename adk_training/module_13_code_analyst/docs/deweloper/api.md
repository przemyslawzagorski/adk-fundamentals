# API — referencja endpointów

Code Analyst wystawia **HTML fragments** (dla HTMX) oraz kilka endpointów JSON. Nie jest klasycznym REST API — to aplikacja hipermedialna. Jeśli potrzebujesz integracji programatycznej, skup się na endpointach zdrowia/metryk.

## Podstawowe informacje

- **Base URL**: `http://localhost:8088` (dev), `https://analyst.internal` (prod)
- **Auth**: `X-API-Key: <klucz>` lub `?api_key=<klucz>` (patrz [Autoryzacja](../bezpieczenstwo/autoryzacja.md))
- **Rate limit**: per-IP, konfigurowalny ([Rate limiting](../operacje/rate-limiting.md))
- **Request-ID**: każdy request ma `X-Request-ID` w logach (i w odpowiedzi, przy `HX-Request`)

## Zdrowie i monitoring (bez auth)

| Endpoint | Metoda | Opis | Odpowiedź |
|----------|--------|------|-----------|
| `/health` | GET | Liveness — proces żyje | `{"status":"ok","version":"1.0.0"}` |
| `/ready` | GET | Readiness — konfiguracja LLM OK | `{"ready":true,"project":"..."}` |
| `/metrics` | GET | Prometheus text format | `# HELP ... # TYPE ...` |

Używaj `/health` w liveness probe, `/ready` w readiness probe.

## UI / repozytoria

Wszystkie poniższe wymagają `X-API-Key` (gdy `CODE_ANALYST_API_KEY` ustawione).

### `GET /` — dashboard

Zwraca HTML z listą repo.

### `POST /repos` — dodaj repo

**Form**: `path` (wymagane, absolute path), `name` (opcjonalne).

**Odpowiedź**: HTML fragment z komunikatem + link do nowego repo.

```bash
curl -X POST http://localhost:8088/repos \
  -H "X-API-Key: $KEY" \
  -d "path=C:/repos/acme&name=ACME Backend"
```

### `DELETE /repos/{repo_id}` — usuń repo

Usuwa repo z listy + kasuje cached indexer + runner. Sam indeks na dysku zostaje (do ręcznego czyszczenia w `web_data/`).

### `GET /repos/{repo_id}` — widok szczegółowy

HTML strony z panelami: indeksacja, search, chat, workflow.

## Indeksacja (RAG)

### `POST /repos/{repo_id}/index`

**Form**: `incremental` = `true` | `false`.

- **Incremental** (domyślnie): indeksuje tylko zmienione pliki (po mtime).
- **Pełna**: czyści indeks i buduje od zera.

Rate limit: `CODE_ANALYST_RATE_LIMIT_INDEX` (domyślnie 2/min).

Odpowiedź: HTML fragment z liczbą indeksowanych / pominiętych / czasem.

### `GET /repos/{repo_id}/index/status`

Polling — UI odpytuje co sekundę. Zwraca:

- pusty HTML gdy idle,
- `Indeksowanie w toku...` gdy trwa,
- komunikat błędu gdy fail.

## Wyszukiwanie (RAG)

### `POST /repos/{repo_id}/search`

**Form**: `query` (do 500 znaków, sanityzacja), `top_k` (1..20).

Zwraca HTML z listą `top_k` fragmentów kodu + plikami źródłowymi.

Rate limit: `CODE_ANALYST_RATE_LIMIT_SEARCH`.

## Chat (workflow `analysis`)

### `POST /repos/{repo_id}/chat`

**Form**: `message` (sanityzowane).

Uruchamia sekwencyjny pipeline `analysis`:
`CodeAnalyst → (opcjonalnie) Architect → Summarizer` (patrz [Workflows](../architektura/workflows.md)).

Odpowiedź: HTML z kroków pipeline + finalna odpowiedź.

Rate limit: `CODE_ANALYST_RATE_LIMIT_WORKFLOW`.

### `POST /repos/{repo_id}/chat/reset`

Czyści session chat dla tego repo. Historia rozmowy znika.

## Workflows (scenariusze)

### `POST /repos/{repo_id}/workflow`

**Form**:

- `workflow_id` — jeden z: `analysis`, `onboarding`, `bugfix`, `code_review`, `testing`, `documentation`.
- `user_input` — dodatkowy kontekst (opcjonalnie).

Każdy workflow to osobny `SequentialAgent` z własną kombinacją sub-agentów. Szczegóły w [Workflows](../architektura/workflows.md).

```bash
curl -X POST http://localhost:8088/repos/acme-abc123/workflow \
  -H "X-API-Key: $KEY" \
  -d "workflow_id=code_review&user_input=Skup sie na bledach null-check"
```

## Kody statusu

| Status | Kiedy |
|--------|-------|
| 200 | OK |
| 400 | Walidacja nie przeszła (np. pusty input) |
| 401 | Brak lub zły `X-API-Key` |
| 404 | Repo/resource nie istnieje |
| 429 | Rate limit przekroczony |
| 500 | Błąd wewnętrzny (szczegóły w logach z `X-Request-ID`) |
| 503 | `/ready` gdy LLM nie skonfigurowane |

## Nagłówki odpowiedzi

- `X-Request-ID` — do korelacji logów.
- `HX-Refresh: true` — HTMX specyficzne, wymusza refresh strony (używane w delete repo).
- `Retry-After` — przy 429.

## OpenAPI / Swagger

`include_in_schema=False` dla endpointów HTML/metryk — Swagger pokaże tylko te, które mają sens jako JSON API.

```
http://localhost:8088/docs        # Swagger UI
http://localhost:8088/redoc       # ReDoc
http://localhost:8088/openapi.json
```

## Przykład pełnego cyklu

```powershell
$KEY = "twój-klucz"
$BASE = "http://localhost:8088"

# 1. Dodaj repo
curl -X POST "$BASE/repos" -H "X-API-Key: $KEY" `
  -d "path=C:/repos/acme&name=acme"

# Z odpowiedzi wyciągnij repo_id (np. acme-abc123)

# 2. Indeksuj
curl -X POST "$BASE/repos/acme-abc123/index" `
  -H "X-API-Key: $KEY" -d "incremental=false"

# 3. Szukaj
curl -X POST "$BASE/repos/acme-abc123/search" `
  -H "X-API-Key: $KEY" -d "query=autoryzacja&top_k=5"

# 4. Analiza
curl -X POST "$BASE/repos/acme-abc123/chat" `
  -H "X-API-Key: $KEY" -d "message=gdzie jest logowanie?"

# 5. Workflow
curl -X POST "$BASE/repos/acme-abc123/workflow" `
  -H "X-API-Key: $KEY" -d "workflow_id=code_review"
```

Następnie: [Testy](testy.md).

# Konfiguracja — wszystkie zmienne środowiskowe

Konfiguracja przez Pydantic Settings — każda zmienna ENV mapuje się na pole klasy `Settings` w [`config.py`](../architektura/komponenty.md). Jest też `.env.template` w repo.

## Zmienne obowiązkowe

### Dostawca LLM

=== "Gemini API (klucz)"

    ```env
    GOOGLE_GENAI_USE_VERTEXAI=FALSE
    GOOGLE_API_KEY=xxx-z-google-ai-studio
    ```

=== "Vertex AI (project)"

    ```env
    GOOGLE_GENAI_USE_VERTEXAI=TRUE
    GOOGLE_CLOUD_PROJECT=your-project-id
    GOOGLE_CLOUD_LOCATION=europe-west1
    # gcloud auth application-default login
    ```

!!! tip "Który wybrać?"
    **Gemini API** — szybki start, pay-as-you-go, klucz API.
    **Vertex AI** — rekomendowany do prod: IAM, audit logs, residency (EU). Tak skonfigurowano Cloud Run w projektach szkoleniowych.

### API key dla web UI

```env
CODE_ANALYST_API_KEY=base64-32-bytes
```

- **Puste** → auth wyłączony (tylko localhost dev!).
- **Ustawione** → każdy request do endpointów wymaga `X-API-Key` lub `?api_key=`.
- Generacja: patrz [Autoryzacja](../bezpieczenstwo/autoryzacja.md).

## Zmienne opcjonalne — grupowane tematycznie

### Aplikacja

```env
CODE_ANALYST_HOST=0.0.0.0
CODE_ANALYST_PORT=8088
CODE_ANALYST_LOG_LEVEL=INFO          # DEBUG/INFO/WARNING/ERROR
CODE_ANALYST_LOG_FORMAT=json         # json | plain
CODE_ANALYST_DATA_DIR=./web_data     # gdzie trzymać indeksy RAG per-repo
```

### CORS

```env
# Lista origin-ów oddzielona przecinkiem; puste = CORS wyłączony
CODE_ANALYST_CORS_ORIGINS=https://analyst.internal.example.com
```

### Rate limiting (SlowAPI, per IP)

```env
CODE_ANALYST_RATE_LIMIT_INDEX=2/minute
CODE_ANALYST_RATE_LIMIT_SEARCH=30/minute
CODE_ANALYST_RATE_LIMIT_WORKFLOW=10/minute
CODE_ANALYST_RATE_LIMIT_CHAT=20/minute
```

### RAG / indeksacja

```env
CODE_ANALYST_CHUNK_SIZE=768          # rozmiar chunka (tokenów)
CODE_ANALYST_CHUNK_OVERLAP=100       # nakładka między chunkami
CODE_ANALYST_SIMILARITY_CUTOFF=0.35  # niżej = więcej wyników, słabsza trafność
CODE_ANALYST_SIMILARITY_TOP_K=8      # ile chunków zwracać
CODE_ANALYST_MAX_FILE_SIZE=1048576   # 1 MB — większe pliki pomijane
```

### Modele

```env
CODE_ANALYST_LLM_MODEL=gemini-2.5-pro
CODE_ANALYST_EMBED_MODEL=text-embedding-004
```

### Build tools

```env
CODE_ANALYST_PYTEST_TIMEOUT=300      # sek, na wywołanie run_tests
CODE_ANALYST_MAX_TEST_FILTER_LEN=200
```

## `.env` — kompletny przykład (dev)

```env
# LLM provider
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=paste-your-key

# App
CODE_ANALYST_HOST=127.0.0.1
CODE_ANALYST_PORT=8088
CODE_ANALYST_LOG_FORMAT=plain
CODE_ANALYST_LOG_LEVEL=DEBUG

# Auth (pusty = dev lokalny)
CODE_ANALYST_API_KEY=

# CORS wyłączony w dev
CODE_ANALYST_CORS_ORIGINS=

# RAG tuning
CODE_ANALYST_CHUNK_SIZE=768
CODE_ANALYST_SIMILARITY_CUTOFF=0.35
```

## `.env` — kompletny przykład (prod)

```env
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=analyst-prod
GOOGLE_CLOUD_LOCATION=europe-west1

CODE_ANALYST_HOST=0.0.0.0
CODE_ANALYST_PORT=8088
CODE_ANALYST_LOG_FORMAT=json
CODE_ANALYST_LOG_LEVEL=INFO

CODE_ANALYST_API_KEY=base64-32-bytes-secret-generated-per-env
CODE_ANALYST_CORS_ORIGINS=https://analyst.internal.company.com

CODE_ANALYST_RATE_LIMIT_WORKFLOW=5/minute

CODE_ANALYST_DATA_DIR=/data/code_analyst
```

## Walidacja przy starcie

`config.py` używa Pydantic Settings — przy starcie aplikacji:

- brakujący wymagany → `ValidationError`, aplikacja nie wstaje,
- zły typ (np. port `abc`) → natychmiastowy błąd,
- `/ready` endpoint sprawdza poprawność konfiguracji LLM.

```powershell
# Sprawdzenie przed uruchomieniem
python -c "from config import settings; print(settings.model_dump_json(indent=2))"
```

## Priority — kolejność ładowania

Pydantic Settings sczytuje w kolejności (późniejsze nadpisują wcześniejsze):

1. Wartości domyślne w klasie `Settings`.
2. Plik `.env` z katalogu aplikacji.
3. Zmienne środowiskowe procesu (ENV).
4. (nieużywane) parametry konstruktora.

**W praktyce**: dev używa `.env`, prod nadpisuje przez ENV w K8s/Cloud Run/Compose.

Następnie: [API — endpointy](api.md).

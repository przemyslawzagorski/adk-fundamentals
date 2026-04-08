# FilesRetrieval vs Vertex AI Search — porównanie podejść do RAG

## Architektura

```
┌─────────────────────────────────────────────────────────────────┐
│              FilesRetrieval (Moduł 10)                          │
│                                                                 │
│  Pliki lokalne → LlamaIndex → VectorStoreIndex (RAM)           │
│  Embeddingi: text-embedding-004 (Google API)                    │
│  Wszystko działa lokalnie, indeks w pamięci procesu             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              Vertex AI Search (Moduł 03)                        │
│                                                                 │
│  Pliki w Cloud Storage → Data Store → Search Engine (chmura)   │
│  Embeddingi: wewnętrzne modele Google (zarządzane)              │
│  Infrastruktura w pełni zarządzana przez GCP                    │
└─────────────────────────────────────────────────────────────────┘
```

## Tabela porównawcza

| Aspekt | FilesRetrieval (Moduł 10) | Vertex AI Search (Moduł 03) |
|--------|---------------------------|------------------------------|
| **Lokalizacja danych** | Pliki lokalne na dysku | Cloud Storage / BigQuery / Website |
| **Indeks** | W pamięci RAM (VectorStoreIndex) | Zarządzany w chmurze Google |
| **Czas indeksowania** | **Sekundy** (3 pliki MD ~1-3s) | **10-30 minut** (zależy od rozmiaru) |
| **Trwałość indeksu** | ❌ Znika po restarcie procesu | ✅ Persystentny w chmurze |
| **Model embeddingów** | text-embedding-004 (Google API) | Wewnętrzne modele Google |
| **Skalowalność** | Ograniczona (RAM maszyny) | Praktycznie nieograniczona |
| **Konfiguracja** | Minimalna (katalog + API key) | Konsola GCP, Data Store, Engine |
| **Zależności** | llama-index-core, llama-index-embeddings-google | Vertex AI Search API |
| **Offline** | ❌ (wymaga Google API do embeddingów) | ❌ (wymaga dostępu do GCP) |
| **Format plików** | MD, TXT, PDF, DOCX, CSV, JSON, HTML | PDF, HTML, TXT (Cloud Storage) |

## Koszty

### FilesRetrieval (Moduł 10)

| Składnik | Koszt |
|----------|-------|
| Generowanie embeddingów (text-embedding-004) | **$0.000025 / 1K tokenów** |
| Przechowywanie | $0 (lokalna pamięć RAM) |
| Zapytania wyszukiwania | $0 (lokalny vector search) |
| Infrastruktura | $0 (działa na Twoim laptopie) |

**Przykład:** 100 stron dokumentacji ≈ 50K tokenów → embeddingowanie kosztuje ~$0.00125 (jednorazowo).
Każde zapytanie agenta to koszt embeddingu zapytania (~$0.000001) + koszt LLM (~$0.001).

**Szacunek miesięczny dla małego zespołu (1000 zapytań/miesiąc):** ~$1-2 (sam LLM)

### Vertex AI Search (Moduł 03)

| Składnik | Koszt |
|----------|-------|
| Search Standard Edition | **$1.50 / 1,000 zapytań** |
| Search Enterprise Edition (z AI Answers) | **$4.00 / 1,000 zapytań** |
| Advanced Generative Answers | **+$4.00 / 1,000 zapytań** |
| Storage (IndexStorage) | **$5.00 / GB / miesiąc** |
| Free tier | 10,000 zapytań/konto/miesiąc + 10 GB storage |

**Przykład:** 100 stron dokumentacji (~100 MB) z 10,000 zapytań/miesiąc:
- Standard: Free tier pokrywa (10K zapytań + 10 GB storage)
- Enterprise z AI: ~$80/miesiąc po przekroczeniu free tier

**Szacunek miesięczny (50K zapytań, 100K dokumentów, 100 GB):**
- Standard: ~$75 (zapytania) + $540 (storage roczny) ≈ **$120/miesiąc**
- Enterprise: ~$200 + $540 ≈ **$245/miesiąc**

## Czas indeksowania

### FilesRetrieval
- **3 pliki Markdown (łącznie ~5 KB):** ~1-3 sekundy
- **100 plików tekstowych (~1 MB):** ~15-30 sekund
- **1000 plików (~10 MB):** ~2-5 minut
- Indeksowanie odbywa się w RAM przy starcie agenta
- Każdy restart = ponowne indeksowanie

### Vertex AI Search
- **Upload do Cloud Storage:** sekundy-minuty (zależy od łącza)
- **Indeksowanie w Data Store:** **10-30 minut** (niezależnie od rozmiaru*)
- *Bardzo duże zbiory mogą trwać dłużej
- Indeksowanie jednorazowe, aktualizacja automatyczna

## Kiedy co wybrać?

### Wybierz FilesRetrieval gdy:
- 🏠 **Prototypujesz** lub budujesz PoC
- 📂 Masz **małą bazę wiedzy** (<1000 dokumentów)
- 🔒 Dane **nie mogą** opuścić Twojej maszyny (embeddingi API to wyjątek)
- 💰 Chcesz **minimalizować koszty** w fazie rozwoju
- 🚀 Potrzebujesz **szybkiego startu** bez konfiguracji infrastruktury

### Wybierz Vertex AI Search gdy:
- 🏢 Budujesz **produkcyjny** system RAG
- 📚 Masz **dużą bazę dokumentów** (tysiące-miliony)
- 🔄 Potrzebujesz **automatycznej aktualizacji** indeksu
- 👥 Wielu użytkowników jednocześnie odpytuje bazę
- 📊 Potrzebujesz **zaawansowanych funkcji**: ranking, AI Answers, analytics
- ☁️ Dane są już w **Google Cloud Storage / BigQuery**

## Ścieżka migracji

Typowy scenariusz w firmie:

```
1. Prototyp z FilesRetrieval (ten moduł)
   ↓ Walidacja konceptu, feedback użytkowników
2. Przeniesienie do Vertex AI Search (moduł 03)
   ↓ Upload dokumentów do Cloud Storage
   ↓ Konfiguracja Data Store + Search Engine
3. Produkcja z Vertex AI Search
   ↓ Integracja z CI/CD, monitoring, autoscaling
```

Zmiana z FilesRetrieval na Vertex AI Search wymaga tylko zamiany narzędzia w konfiguracji agenta:

```python
# Z tego (Moduł 10):
from google.adk.tools.retrieval.files_retrieval import FilesRetrieval
tools = [FilesRetrieval(name="baza", description="...", input_dir="./docs")]

# Na to (Moduł 03):
from google.adk.tools import VertexAiSearchTool
tools = [VertexAiSearchTool(search_engine_id="...", max_results=10)]
```

Prompt i logika agenta pozostają bez zmian.

## Źródła

- [ADK FilesRetrieval source code](https://github.com/google/adk-python/blob/main/src/google/adk/tools/retrieval/files_retrieval.py)
- [Vertex AI Search Pricing](https://cloud.google.com/generative-ai-app-builder/pricing)
- [Google Embeddings Pricing](https://cloud.google.com/vertex-ai/generative-ai/pricing#embeddings)
- [LlamaIndex SimpleDirectoryReader](https://docs.llamaindex.ai/en/stable/module_guides/loading/simpledirectoryreader/)

# Moduł 10: Local RAG - Przeszukiwanie plików firmowych 📁

## Cel modułu

Zbudowanie agenta RAG (Retrieval-Augmented Generation) opartego na **lokalnych plikach**
za pomocą `FilesRetrieval` z ADK. Agent przeszukuje dokumentację firmową TechCorp
(polityki, instrukcje, architektura) bez potrzeby konfiguracji chmury.

## Co robi FilesRetrieval?

```
Pliki (.md, .txt, .pdf, ...)
        ↓
SimpleDirectoryReader (LlamaIndex)
        ↓
Chunking na fragmenty tekstu
        ↓
gemini-embedding-2-preview (Google)  → Embeddingi wektorowe
        ↓
VectorStoreIndex (w pamięci RAM)
        ↓
Agent zadaje pytanie → Semantic search → Top-K fragmentów → LLM generuje odpowiedź
```

## Wymagania

```bash
pip install google-adk llama-index-core llama-index-embeddings-google-genai
```

Potrzebujesz jednego z:
- **Vertex AI** (zalecane): `GOOGLE_GENAI_USE_VERTEXAI=1` + projekt GCP z włączonym Vertex AI
- **Google AI Studio**: `GOOGLE_API_KEY` — uzyskaj z https://aistudio.google.com/apikey

## Szybki start

```bash
# 1. Skopiuj .env
cp .env.template .env
# Uzupełnij GOOGLE_API_KEY

# 2. Uruchom agenta
cd module_10_local_rag
adk run .

# 3. Zapytaj agenta
> Jaka jest polityka haseł w firmie?
> Co dostaję na onboardingu?
> Jakie mikroserwisy ma system?
```

## Ćwiczenia

### Ćwiczenie 1: Podstawowe pytania do bazy wiedzy
Uruchom agenta i zadaj pytania:
- "Jaka jest minimalna długość hasła?"
- "Jaki laptop dostanę na start?"
- "Na jakim porcie działa order-service?"

Obserwuj jak agent korzysta z narzędzia `baza_wiedzy_firmowej`.

### Ćwiczenie 2: Porównanie z agentem bez RAG
W `agent_solution.py` znajdziesz `agent_bez_rag` — agenta bez dostępu do dokumentów.
Porównaj odpowiedzi na te same pytania. Zwróć uwagę na halucynacje.

### Ćwiczenie 3: Dodaj własne dokumenty
1. Utwórz katalog `docs_custom/`
2. Dodaj własne pliki (np. notatki z projektu, wiki zespołu)
3. Skonfiguruj nowego agenta w `agent_solution.py`
4. Przetestuj wyszukiwanie

## Kluczowe pojęcia

| Pojęcie | Opis |
|---------|------|
| **FilesRetrieval** | Narzędzie ADK do RAG na plikach lokalnych, oparte na LlamaIndex |
| **Embedding** | Reprezentacja wektorowa tekstu (gemini-embedding-2-preview) |
| **VectorStoreIndex** | Indeks wektorowy w pamięci RAM do wyszukiwania semantycznego |
| **SimpleDirectoryReader** | Ładuje pliki z katalogu (MD, TXT, PDF, DOCX, CSV, JSON...) |
| **Chunking** | Podział dokumentu na fragmenty odpowiednie dla embeddingów |
| **Semantic Search** | Wyszukiwanie oparte na znaczeniu, nie na słowach kluczowych |

## Struktura plików

```
module_10_local_rag/
├── agent.py              # Główny agent z FilesRetrieval
├── agent_solution.py     # Ćwiczenia (basic, bez_rag, custom)
├── docs/                 # Dokumenty firmowe do zaindeksowania
│   ├── polityka_bezpieczenstwa.md
│   ├── onboarding.md
│   └── architektura.md
├── teoria.md             # Porównanie FilesRetrieval vs Vertex AI Search
├── .env.template         # Szablon konfiguracji
├── requirements.txt      # Zależności Python
└── README.md             # Ten plik
```

## Jak to naprawdę działa — analiza kodu źródłowego ADK

Na podstawie kodu `google-adk` (pakiet `google.adk.tools.retrieval`):

### Łańcuch klas

```
BaseTool
  └── BaseRetrievalTool          — deklaruje function declaration z parametrem "query"
        └── LlamaIndexRetrieval  — trzyma retriever, wywołuje retrieve(query)[0].text
              └── FilesRetrieval — buduje VectorStoreIndex z plików w __init__
```

### Co się dzieje przy ładowaniu agenta?

```python
# FilesRetrieval.__init__() robi TO WSZYSTKO w konstruktorze:
retriever = VectorStoreIndex.from_documents(
    SimpleDirectoryReader(input_dir).load_data(),  # 1. Wczytaj pliki
    embed_model=embedding_model,                   # 2. Wygeneruj embeddingi
).as_retriever()                                   # 3. Zwróć retriever
```

1. **`SimpleDirectoryReader`** skanuje katalog i parsuje pliki (MD, TXT, PDF, DOCX, CSV...)
2. **LlamaIndex** dzieli je na chunki (fragmenty ~1024 tokenów)
3. **`gemini-embedding-2-preview`** generuje wektor 768-wymiarowy dla każdego chunka
   (wymaga połączenia z API — Vertex AI lub Google AI Studio)
4. **`VectorStoreIndex`** buduje indeks w pamięci RAM

### Co się dzieje przy zapytaniu agenta?

```python
# LlamaIndexRetrieval.run_async():
return self.retriever.retrieve(args['query'])[0].text
```

1. LLM (Gemini) widzi narzędzie `baza_wiedzy_firmowej` z parametrem `query: string`
2. Gemini decyduje "to pytanie o firmę → wywołaj narzędzie" i generuje `query`
3. LlamaIndex liczy embedding zapytania, szuka najbliższych wektorów (cosine similarity)
4. **Zwraca TYLKO JEDEN najlepszy fragment** (`[0].text`) — to ograniczenie ADK!
5. LLM dostaje ten fragment jako kontekst i generuje odpowiedź

### ⚠️ Ważne ograniczenie w źródle ADK

`LlamaIndexRetrieval.run_async()` zwraca **tylko `[0].text`** — pierwszy (najlepszy) wynik.
Jeśli odpowiedź wymaga informacji z kilku fragmentów, agent może ją przegapić.
To świadoma decyzja uproszczenia w ADK — w produkcji warto to rozszerzyć.

## Ulotność indeksu — co trzeba wiedzieć

### Indeks żyje TYLKO w pamięci RAM procesu

```
adk run .          → indeks budowany → odpowiadanie na pytania → Ctrl+C → indeks ZNIKA
adk run .          → indeks budowany OD NOWA (ponowne embeddingi = ponowne wywołania API)
```

- **Każdy restart** = ponowne wczytanie plików + ponowne generowanie embeddingów
- **Brak persystencji** — nie ma żadnego cache na dysku
- **Czas budowania:** 3 pliki MD ~2-3 sekundy, 100 plików ~30 sekund, 1000+ plików = minuty
- **Koszt:** każde uruchomienie to wywołania API embeddingów (choć tanie: ~$0.00125 za 100 stron)

### Dlaczego nie przeszkadza to w praktyce?

Dla małych baz (<100 plików) czas indeksowania jest na tyle krótki, że nie stanowi problemu.
Jeśli indeksujesz tysiące dokumentów lub potrzebujesz persystencji — czas przejść na
Vertex AI Search (moduł 03) lub Vertex AI RAG (`VertexAiRagRetrieval`).

## Kiedy to podejście ma sens w realnej pracy?

### ✅ TAK — realne scenariusze dla programisty/analityka

| Scenariusz | Dlaczego FilesRetrieval | Przykład |
|------------|------------------------|---------|
| **Szybki PoC / prototyp** | Zero konfiguracji infrastruktury, działa w 2 minuty | "Sprawdźmy czy RAG na naszym wiki ma sens, zanim kupujemy Vertex AI Search" |
| **Asystent dokumentacji zespołowej** | Wrzuć pliki MD/PDF z Confluence/Notion i pytaj | Agent odpowiadający na pytania o architekturze projektu |
| **Onboarding nowych osób** | Zindeksuj wiki, runbooki, ADR-y, README | Nowy dev pyta "jak postawić środowisko?" zamiast szukać po Confluence |
| **Prywatne notatki + LLM** | Twoje lokalne pliki nigdy nie opuszczają maszyny* | Notatki z retrospektyw, design doc-i, meeting notes |
| **Code review z kontekstem** | Zindeksuj coding guidelines, standardy, checklisty | Agent podpowiada: "wg naszych standardów hasło musi mieć 12 znaków" |
| **Hackathon / warsztat** | Pełny RAG pod kontrolą, bez czekania 30 min na Data Store | Dokładnie ten moduł szkoleniowy |

*\* Embeddingi są generowane przez API Google (Vertex AI lub AI Studio) — sam tekst chunków
jest wysyłany do API. Pliki nie są "w pełni lokalne" w sensie offline.*

### ❌ NIE — kiedy użyć czegoś innego

| Sytuacja | Problem z FilesRetrieval | Lepsze rozwiązanie |
|----------|--------------------------|-------------------|
| Tysiące dokumentów | Indeks w RAM, długie budowanie | Vertex AI Search, Vertex AI RAG |
| Wielu użytkowników | Jeden proces = jeden indeks | Vertex AI Search (zarządzana infra) |
| Indeks musi przetrwać restart | Brak persystencji | Vertex AI RAG, Pinecone, Weaviate |
| Offline (bez internetu) | Embeddingi wymagają API | Lokalne modele (sentence-transformers) |
| Zaawansowany ranking | ADK zwraca tylko top-1 wynik | Custom LlamaIndex retriever |

## Hierarchia narzędzi RAG w ADK

ADK oferuje **3 wbudowane podejścia** do RAG (od najprostszego):

```
1. FilesRetrieval          ← TEN MODUŁ — pliki lokalne, indeks w RAM
   └── LlamaIndexRetrieval ← można podać własny LlamaIndex retriever

2. VertexAiRagRetrieval    ← Vertex AI RAG Engine (persystentne korpusy w chmurze)

3. VertexAiSearchTool      ← Vertex AI Search (pełny silnik wyszukiwania, moduł 03)
```

Każde z nich to narzędzie (`tool`), które agent wywołuje gdy uzna,
że pytanie wymaga wyszukiwania w bazie wiedzy.

## Porównanie z Vertex AI Search (Moduł 03)

Szczegółowe porównanie (koszty, czas indeksowania, kiedy co wybrać) — patrz `teoria.md`.

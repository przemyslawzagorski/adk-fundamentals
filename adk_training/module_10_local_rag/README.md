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
text-embedding-004 (Google)  → Embeddingi wektorowe
        ↓
VectorStoreIndex (w pamięci RAM)
        ↓
Agent zadaje pytanie → Semantic search → Top-K fragmentów → LLM generuje odpowiedź
```

## Wymagania

```bash
pip install google-adk llama-index-core llama-index-embeddings-google
```

Potrzebujesz `GOOGLE_API_KEY` (do embeddingów) — uzyskaj z https://aistudio.google.com/apikey

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
| **Embedding** | Reprezentacja wektorowa tekstu (text-embedding-004, 768 wymiarów) |
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
├── .env.template         # Szablon konfiguracji
├── requirements.txt      # Zależności Python
└── README.md             # Ten plik
```

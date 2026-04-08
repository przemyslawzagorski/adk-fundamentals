# Module 03: RAG Agent - Teoria i Koncepcje

## 📚 Spis Treści
1. [Wprowadzenie do RAG](#wprowadzenie-do-rag)
2. [Architektura RAG w ADK](#architektura-rag-w-adk)
3. [Vertex AI Search](#vertex-ai-search)
4. [Przypadki Użycia Biznesowego](#przypadki-użycia-biznesowego)
5. [Najlepsze Praktyki](#najlepsze-praktyki)
6. [Typowe Pułapki](#typowe-pułapki)

---

## 🎯 Wprowadzenie do RAG

### Czym jest RAG?

**RAG (Retrieval-Augmented Generation)** to wzorzec łączący:
- **Retrieval** - Wyszukiwanie relevantnych dokumentów
- **Augmented** - Wzbogacenie kontekstu LLM
- **Generation** - Generowanie odpowiedzi przez LLM

### Problem który rozwiązuje RAG

**Bez RAG:**
```
User: "Jakie są procedury wdrożeniowe w naszej firmie?"
   ↓
LLM: "Nie mam dostępu do dokumentacji Twojej firmy.
      Mogę podać ogólne best practices..." ❌ Hallucination!
```

**Z RAG:**
```
User: "Jakie są procedury wdrożeniowe w naszej firmie?"
   ↓
RAG Tool: Wyszukuje w dokumentacji → Znajduje "Procedury_Wdrozeniowe.pdf"
   ↓
LLM: "Według dokumentu 'Procedury Wdrożeniowe' (sekcja 3.1),
      proces składa się z 5 kroków: 1) Analiza wymagań..." ✅ Fakty!
```

### Kluczowe Korzyści RAG

1. **Eliminacja Hallucinations** - Odpowiedzi oparte na faktach
2. **Aktualność** - Zawsze najnowsze dane (aktualizuj dokumenty)
3. **Weryfikowalność** - Cytowanie źródeł
4. **Specjalizacja** - Wiedza specyficzna dla organizacji
5. **Bezpieczeństwo** - Kontrola nad danymi (nie w treningu modelu)

---

## 🏗️ Architektura RAG w ADK

### Przepływ Danych

```
┌─────────────────────────────────────────────────────────┐
│                    User Query                           │
│         "Jakie są procedury wdrożeniowe?"               │
└────────────────────────┬────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│              LlmAgent (z VertexAiSearchTool)            │
│  1. Analizuje pytanie                                   │
│  2. Decyduje użyć RAG tool                              │
└────────────────────────┬────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│           VertexAiSearchTool.search()                   │
│  Query: "procedury wdrożeniowe"                         │
└────────────────────────┬────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│              Vertex AI Search Engine                    │
│  1. Semantic search w Data Store                       │
│  2. Ranking wyników                                     │
│  3. Zwraca top N dokumentów                             │
└────────────────────────┬────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                  Retrieved Documents                    │
│  - Procedury_Wdrozeniowe.pdf (score: 0.95)             │
│  - Polityka_Bezpieczenstwa.pdf (score: 0.72)           │
│  - FAQ_Produktu.pdf (score: 0.65)                      │
└────────────────────────┬────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│              LlmAgent (Gemini Model)                    │
│  Context: [Retrieved Documents]                         │
│  Generuje odpowiedź na podstawie dokumentów             │
└────────────────────────┬────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                  Final Response                         │
│  "Według dokumentu 'Procedury Wdrożeniowe'..."         │
│  [Cytuje źródła, podaje konkretne informacje]           │
└─────────────────────────────────────────────────────────┘
```

### Komponenty w ADK

**1. VertexAiSearchTool**
```python
from google.adk.tools import VertexAiSearchTool

rag_tool = VertexAiSearchTool(
    search_engine_id="projects/.../engines/my-engine",  # LUB
    data_store_id="projects/.../dataStores/my-store",   # LUB
    max_results=10  # Liczba dokumentów do pobrania
)
```

**2. LlmAgent z RAG Tool**
```python
agent = LlmAgent(
    name="rag_assistant",
    model="gemini-2.5-flash",
    instruction="Używaj narzędzia wyszukiwania...",
    tools=[rag_tool]  # Dodaj RAG tool
)
```

---

## 🔍 Vertex AI Search

### Czym jest Vertex AI Search?

**Vertex AI Search** to zarządzana usługa Google Cloud do:
- Indeksowania dokumentów (PDF, HTML, JSON, CSV)
- Semantic search (wyszukiwanie semantyczne)
- Ranking wyników (ML-based)
- Integracji z ADK

### Typy Źródeł Danych

| Typ | Opis | Przykład |
|-----|------|----------|
| **Cloud Storage** | Pliki w GCS bucket | PDFy, dokumenty Word |
| **Website** | Crawling strony www | Dokumentacja online |
| **BigQuery** | Tabele BigQuery | Dane strukturalne |
| **Unstructured** | Dowolne dokumenty | Mieszane formaty |

### Proces Konfiguracji

**Krok 1: Utwórz Data Store**
```bash
# W GCP Console:
Vertex AI → Search & Conversation → Create App → Search
→ Create Data Store → Wybierz źródło danych
```

**Krok 2: Wgraj Dokumenty**
```bash
# Dla Cloud Storage:
gsutil cp dokumenty/*.pdf gs://my-bucket/docs/

# Vertex AI automatycznie zindeksuje
```

**Krok 3: Pobierz ID**
```bash
# Data Store ID format:
projects/{project}/locations/{location}/collections/default_collection/dataStores/{id}

# Search Engine ID format:
projects/{project}/locations/{location}/collections/default_collection/engines/{id}
```

**Krok 4: Użyj w ADK**
```python
rag_tool = VertexAiSearchTool(
    data_store_id="projects/my-project/locations/global/collections/default_collection/dataStores/my-docs",
    max_results=10
)
```

---

## 💼 Przypadki Użycia Biznesowego

### 1. **Obsługa Klienta - FAQ Bot**

**Scenariusz:** Firma ma 500+ stron dokumentacji produktu. Klienci zadają powtarzające się pytania.

**Rozwiązanie RAG:**
```python
# Data Store: Dokumentacja produktu (PDFy, HTML)
faq_tool = VertexAiSearchTool(
    data_store_id="...",
    max_results=5
)

faq_agent = LlmAgent(
    name="faq_bot",
    model="gemini-2.5-flash",
    instruction="""Jesteś botem FAQ dla produktu TechPro.
    
    Gdy klient zadaje pytanie:
    1. Wyszukaj w dokumentacji
    2. Podaj odpowiedź z dokumentu
    3. Zacytuj źródło (numer strony, sekcja)
    4. Zaproponuj powiązane tematy
    """,
    tools=[faq_tool]
)
```

**Korzyści:**
- 📉 Redukcja ticketów do supportu o 70%
- ⏰ Odpowiedzi 24/7 bez dodatkowych kosztów
- 📚 Zawsze aktualna wiedza (aktualizuj dokumenty)
- 😊 Lepsza satysfakcja klientów (szybkie odpowiedzi)

### 2. **HR - Polityki i Procedury**

**Scenariusz:** Pracownicy pytają o polityki firmy, benefity, procedury.

**Rozwiązanie RAG:**
```python
# Data Store: Regulaminy, polityki, procedury HR
hr_tool = VertexAiSearchTool(
    data_store_id="...",
    max_results=3
)

hr_agent = LlmAgent(
    name="hr_assistant",
    model="gemini-2.5-flash",
    instruction="""Jesteś asystentem HR.
    
    Odpowiadasz na pytania o:
    - Polityki urlopowe
    - Benefity (ubezpieczenie, karta sportowa)
    - Procedury (onboarding, offboarding)
    - Regulaminy pracy
    
    ZAWSZE cytuj konkretny dokument i sekcję!
    """,
    tools=[hr_tool]
)
```

**Korzyści:**
- ⏱️ Oszczędność czasu HR (mniej powtarzalnych pytań)
- 📖 Pracownicy mają dostęp do informacji 24/7
- ✅ Spójne odpowiedzi (nie ma różnic między HR-owcami)
- 🔒 Kontrola dostępu (tylko autoryzowani użytkownicy)

### 3. **Compliance - Regulacje Prawne**

**Scenariusz:** Firma musi przestrzegać RODO, ISO, branżowych regulacji.

**Rozwiązanie RAG:**
```python
# Data Store: Regulacje, standardy, audyty
compliance_tool = VertexAiSearchTool(
    data_store_id="...",
    max_results=10  # Więcej dla compliance
)

compliance_agent = LlmAgent(
    name="compliance_assistant",
    model="gemini-2.5-flash",
    instruction="""Jesteś asystentem compliance.
    
    Pomagasz w:
    - Interpretacji regulacji RODO
    - Wymaganiach ISO 27001
    - Procedurach audytowych
    
    KRYTYCZNE: Zawsze cytuj konkretny artykuł/sekcję regulacji!
    Jeśli nie jesteś pewien, zasugeruj konsultację z prawnikiem.
    """,
    tools=[compliance_tool]
)
```

**Korzyści:**
- ⚖️ Redukcja ryzyka prawnego
- 📋 Szybki dostęp do regulacji
- ✅ Audyty łatwiejsze (ślad decyzji)
- 💰 Oszczędność na konsultacjach prawnych

---

## ✅ Najlepsze Praktyki

### 1. **Optymalizacja max_results**

| max_results | Użycie | Szybkość | Koszt | Jakość |
|-------------|--------|----------|-------|--------|
| 1-3 | Proste pytania | ⚡⚡⚡ | 💰 | ⭐⭐ |
| 5-10 | Standardowe | ⚡⚡ | 💰💰 | ⭐⭐⭐⭐ |
| 15-20 | Złożone | ⚡ | 💰💰💰 | ⭐⭐⭐⭐⭐ |

**Zalecenie:** Zacznij od 5, zwiększaj tylko gdy potrzebne.

### 2. **Jakość Dokumentów**

**DO:**
- ✅ Strukturyzuj dokumenty (nagłówki, sekcje)
- ✅ Używaj opisowych tytułów
- ✅ Aktualizuj regularnie
- ✅ Usuwaj duplikaty
- ✅ Dodawaj metadata (autor, data, kategoria)

**NIE:**
- ❌ Nie wgrywaj skanów niskiej jakości
- ❌ Nie mieszaj języków w jednym dokumencie
- ❌ Nie używaj skomplikowanych formatów (lepiej PDF niż DOCX)

### 3. **Instrukcje dla Agenta**

**Dobra instrukcja:**
```python
instruction="""Jesteś asystentem z dostępem do bazy wiedzy.

PROCES:
1. Gdy użytkownik zadaje pytanie merytoryczne, UŻYJ wyszukiwania
2. Przeanalizuj znalezione dokumenty
3. Sformułuj odpowiedź cytując źródła
4. Podaj tytuł dokumentu i sekcję

FORMAT ODPOWIEDZI:
"Według dokumentu '[Tytuł]' (sekcja X.Y):
[Treść odpowiedzi]

Źródło: [Tytuł dokumentu], sekcja X.Y"

Jeśli brak informacji w bazie, powiedz:
"Nie znalazłem tej informacji w dokumentacji. Czy mogę pomóc w czymś innym?"
"""
```

### 4. **Monitorowanie i Optymalizacja**

**Metryki do śledzenia:**
- 📊 Liczba zapytań / dzień
- ⏱️ Średni czas odpowiedzi
- 💰 Koszt / zapytanie
- 😊 Satysfakcja użytkowników (thumbs up/down)
- 🎯 % zapytań z wynikami (coverage)

**Narzędzia:**
- Google Cloud Console → Vertex AI Search → Analytics
- Logi ADK (callback logging)
- Custom dashboards (Looker, Data Studio)

---

## ⚠️ Typowe Pułapki

### 1. **Zbyt Duży max_results**

**Problem:** max_results=50 → wolne, drogie, często gorsze wyniki (noise)

**Rozwiązanie:** Zacznij od 5-10, zwiększaj tylko gdy potrzebne.

### 2. **Słaba Jakość Dokumentów**

**Problem:** Dokumenty niestrukturyzowane, duplikaty, nieaktualne.

**Rozwiązanie:**
- Regularny audyt dokumentów
- Usuwanie duplikatów
- Aktualizacja co miesiąc/kwartał

### 3. **Brak Cytowania Źródeł**

**Problem:** Agent nie cytuje źródeł → użytkownicy nie ufają.

**Rozwiązanie:** Wymuszaj cytowanie w instrukcji:
```python
instruction="""...
ZAWSZE podawaj źródło w formacie:
Źródło: [Tytuł dokumentu], sekcja [X.Y]
"""
```

### 4. **Ignorowanie Kosztów**

**Problem:** Każde zapytanie RAG kosztuje (search + LLM tokens).

**Rozwiązanie:**
- Monitoruj koszty w GCP Console
- Ustaw budżety i alerty
- Optymalizuj max_results
- Cache częste zapytania

### 5. **Brak Fallback**

**Problem:** Co gdy brak wyników w bazie?

**Rozwiązanie:**
```python
instruction="""...
Jeśli wyszukiwanie nie zwróci wyników:
1. Powiedz: "Nie znalazłem tej informacji w dokumentacji"
2. Zaproponuj alternatywę: "Mogę przekierować do działu X"
3. NIE wymyślaj informacji!
"""
```

---

## 🔗 Odniesienia do Dokumentacji

### ADK
- [RAG Overview](https://google.github.io/adk-docs/rag/)
- [VertexAiSearchTool](https://google.github.io/adk-docs/tools/vertex-ai-search/)

### Vertex AI Search
- [Vertex AI Search Docs](https://cloud.google.com/generative-ai-app-builder/docs/enterprise-search-introduction)
- [Data Store Setup](https://cloud.google.com/generative-ai-app-builder/docs/create-data-store-es)

---

## 📝 Podsumowanie

**Kluczowe wnioski:**

1. **RAG eliminuje hallucinations** - odpowiedzi oparte na faktach
2. **Vertex AI Search** - potężne narzędzie do semantic search
3. **max_results** - balansuj jakość vs koszt vs szybkość
4. **Jakość dokumentów** - garbage in, garbage out
5. **Cytowanie źródeł** - buduje zaufanie użytkowników

**Następne kroki:**
- Module 04: Sequential Agents - orkiestracja wielu agentów
- Module 05: Human-in-the-Loop - zatwierdzanie przez człowieka

---

*"Dobry agent RAG łączy moc LLM z dokładnością wyszukiwania w dokumentach."* 🔍


# Moduł 3: Agent RAG - Wyszukiwanie Wspomagane Generowaniem

## 📚 Przegląd
Ten moduł wprowadza **Retrieval-Augmented Generation (RAG)** używając Vertex AI Search. Agent może przeszukiwać korporacyjne bazy wiedzy aby dostarczać dokładne, udokumentowane odpowiedzi.

## Cele Edukacyjne
- Zrozumienie wzorca RAG i kiedy go używać
- Konfiguracja `VertexAiSearchTool` z magazynami danych lub silnikami wyszukiwania
- Integracja dokumentów korporacyjnych z agentami AI
- Obserwacja jak pobrany kontekst poprawia jakość odpowiedzi

## Wymagania Wstępne
- Ukończony Moduł 1 i Moduł 2
- Vertex AI Search włączony w projekcie GCP
- Data Store z zindeksowanymi dokumentami

## Instrukcje Konfiguracji

### Krok 1: Stwórz Vertex AI Search Data Store

1. Przejdź do **Google Cloud Console** → **Vertex AI** → **Search & Conversation**
2. Kliknij **Create App** → Wybierz typ **Search**
3. Skonfiguruj ustawienia aplikacji
4. Kliknij **Create Data Store** → Wybierz typ źródła danych:
   - **Cloud Storage**: Wgraj pliki do bucketa GCS
   - **Website**: Przeszukaj stronę internetową
   - **BigQuery**: Zindeksuj tabele BigQuery
5. Wgraj przykładowe dokumenty (PDFy, HTML, lub dane strukturalne)
6. Poczekaj na zakończenie indeksowania (może zająć 10-30 minut)

### Krok 2: Pobierz Engine/Data Store ID

Po utworzeniu, znajdź swoje ID w konsoli:
- **Engine ID**: `projects/{project}/locations/{location}/collections/default_collection/engines/{engine_id}`
- **Data Store ID**: `projects/{project}/locations/{location}/collections/default_collection/dataStores/{datastore_id}`

### Krok 3: Skonfiguruj Środowisko

```bash
# Skopiuj szablon
cp .env.template .env

# Edytuj .env ze swoją konfiguracją
# Ustaw ALBO SEARCH_ENGINE_ID ALBO SEARCH_DATASTORE_ID (nie oba!)
```

### Krok 4: Uruchom Agenta

```bash
# Zainstaluj zależności
pip install -r requirements.txt

# Uruchom interfejs webowy
adk web
```

## Kluczowe Koncepcje

### Konfiguracja VertexAiSearchTool

```python
from google.adk.tools import VertexAiSearchTool

# Opcja 1: Używanie Search Engine ID
rag_tool = VertexAiSearchTool(
    search_engine_id="projects/.../engines/my-engine",
    max_results=10
)

# Opcja 2: Używanie Data Store ID
rag_tool = VertexAiSearchTool(
    data_store_id="projects/.../dataStores/my-datastore",
    max_results=10
)
```

### Ważne Uwagi
- Musisz użyć **albo** `search_engine_id` **albo** `data_store_id` (nie obu!)
- `max_results` kontroluje ile dokumentów pobrać
- Narzędzie jest wbudowane w modele Gemini 2.x (nie potrzeba niestandardowej funkcji)

## Ćwiczenia

### Ćwiczenie 3.1: Podstawowy RAG
1. Wgraj 2-3 przykładowe dokumenty do magazynu danych
2. Zadaj agentowi pytania wymagające przeszukania tych dokumentów
3. Obserwuj jak cytuje źródła w odpowiedzi

### Ćwiczenie 3.2: Porównanie Z i Bez RAG
1. Zadaj konkretne pytanie o swoje dokumenty
2. Usuń narzędzie i zadaj to samo pytanie
3. Porównaj jakość i dokładność odpowiedzi

### Ćwiczenie 3.3: Testowanie Limitów Pobierania
1. Wypróbuj różne wartości `max_results` (1, 5, 10, 20)
2. Zobacz jak wpływa to na jakość odpowiedzi i czas reakcji

## Rozwiązywanie Problemów

| Problem | Rozwiązanie |
|---------|-------------|
| "Data store not found" | Sprawdź format ID i uprawnienia |
| "Indexing not complete" | Poczekaj na zakończenie indeksowania |
| Brak zwróconych wyników | Zweryfikuj czy dokumenty są poprawnie zindeksowane |
| Permission denied | Upewnij się że service account ma dostęp do Vertex AI Search |

## 🎯 Wyzwanie
Stwórz magazyn danych z:
- Dokumentacją techniczną
- Procedurami operacyjnymi
- Bazą wiedzy produktowej

Następnie przetestuj agenta zadając pytania wymagające przeszukania tej wiedzy!

---
*"Dobry agent RAG łączy moc LLM z dokładnością wyszukiwania w dokumentach."*


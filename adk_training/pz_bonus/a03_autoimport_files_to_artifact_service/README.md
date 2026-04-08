# Moduł A03: Autoimport Files to Artifact Service

## 🎯 Czego się nauczysz?

W tym module poznasz:
- **SaveFilesAsArtifactsPlugin** - automatyczny import plików do artifact service
- **App** - klasa opakowująca agenta z pluginami
- **Pluginy ADK** - rozszerzanie funkcjonalności agenta
- **Automatyzację** - pliki są importowane bez ręcznej interwencji

## 💼 Po co jest ten moduł? (Przypadki biznesowe)

### 1. Analiza Dokumentów
**Scenariusz:** Użytkownik uploaduje PDF, agent automatycznie go analizuje
- Użytkownik przeciąga plik do interfejsu
- Plugin automatycznie importuje do artifact service
- Agent może od razu analizować zawartość

**Korzyści:** Zero ręcznej konfiguracji, natychmiastowa dostępność plików

### 2. Przetwarzanie Obrazów
**Scenariusz:** Batch processing zdjęć
- Użytkownik uploaduje 10 zdjęć
- Wszystkie są automatycznie dostępne dla agenta
- Agent może je przetwarzać, analizować, modyfikować

### 3. Data Pipeline
**Scenariusz:** Automatyczne przetwarzanie danych
- CSV/Excel uploadowane przez użytkownika
- Plugin importuje do artifact service
- Agent może analizować dane, generować raporty

---

## 🏗️ Architektura i Flow

```
User: Przeciąga plik do interfejsu (drag & drop)
    ↓
SaveFilesAsArtifactsPlugin: Przechwytuje plik
    ↓
Plugin: Automatycznie zapisuje do artifact service
    ↓
Agent: Ma natychmiastowy dostęp przez load_artifacts()
    ↓
User: Może zapytać "Analyze the uploaded file"
```

### Różnica: Z pluginem vs Bez pluginu

**BEZ pluginu:**
```
User: Upload file → Manual save_artifact() → Agent access
```

**Z pluginem:**
```
User: Upload file → ✨ AUTOMATIC ✨ → Agent access
```

---

## 🔑 Kluczowe Koncepcje ADK

### 1. **SaveFilesAsArtifactsPlugin**

Plugin który automatycznie importuje pliki uploadowane przez użytkownika:

```python
from google.adk.plugins.save_files_as_artifacts_plugin import SaveFilesAsArtifactsPlugin

plugin = SaveFilesAsArtifactsPlugin()
```

**Co robi:**
- Nasłuchuje na pliki uploadowane w UI
- Automatycznie zapisuje je do artifact service
- Pliki są dostępne dla agenta przez `load_artifacts()`

### 2. **App** - Aplikacja ADK

`App` to wrapper który łączy agenta z pluginami:

```python
from google.adk.apps import App

app = App(
    name='my_app',
    root_agent=my_agent,
    plugins=[SaveFilesAsArtifactsPlugin()]
)
```

**Dlaczego App?**
- Pozwala dodawać pluginy
- Zarządza lifecycle aplikacji
- Integruje różne komponenty ADK

### 3. **Pluginy ADK**

Pluginy to rozszerzenia funkcjonalności agenta:

| Plugin | Funkcja |
|--------|---------|
| **SaveFilesAsArtifactsPlugin** | Auto-import plików |
| **LoggingPlugin** | Logowanie zdarzeń |
| **MetricsPlugin** | Zbieranie metryk |
| **CustomPlugin** | Własne rozszerzenia |

### 4. **load_artifacts()** - Ładowanie Plików

Narzędzie do ładowania plików z artifact service:

```python
from google.adk.tools import load_artifacts

agent = LlmAgent(
    tools=[load_artifacts]  # Agent może ładować pliki
)
```

**Użycie:**
- User: "Load the uploaded image"
- Agent: Wywołuje `load_artifacts()` → zwraca plik

---

## 📋 Wymagania

### 1. Zmienne środowiskowe (.env)
```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=true
ADK_MODEL=gemini-2.5-flash
```

### 2. Instalacja
```bash
pip install google-adk python-dotenv
```

---

## 🚀 Quick Start

### Krok 1: Uruchom aplikację
```bash
cd adk_training/a03_autoimport_files_to_artifact_service
adk web
```

### Krok 2: Otwórz przeglądarkę
```
http://127.0.0.1:8000
```

### Krok 3: Testuj
1. **Upload pliku:**
   - Przeciągnij obraz/PDF do interfejsu (drag & drop)
   - Plugin automatycznie importuje

2. **Zapytaj agenta:**
   - "What files do I have?"
   - "Load the uploaded image"
   - "Analyze the document"

---

## 🧪 Ćwiczenia

### Ćwiczenie 1: Dodaj narzędzie `list_artifacts_with_metadata()`
**Cel:** Wyświetl pliki z dodatkowymi informacjami (rozmiar, typ)

**Zadanie:**
1. Stwórz funkcję która listuje pliki
2. Dla każdego pliku pokaż: nazwę, typ MIME, rozmiar
3. Dodaj narzędzie do agenta

**Wskazówka:**
```python
async def list_artifacts_with_metadata(tool_context: ToolContext):
    files = await tool_context.list_artifacts()
    # Pobierz metadata dla każdego pliku
    for file in files:
        artifact = await tool_context.load_artifact(f'user:{file}')
        # Wyświetl info
```

### Ćwiczenie 2: Dodaj filtrowanie po typie pliku
**Cel:** Agent może filtrować pliki (np. tylko obrazy, tylko PDF)

**Zadanie:**
1. Stwórz `list_artifacts_by_type(file_type: str)`
2. Filtruj pliki po MIME type (image/*, application/pdf, etc.)
3. Zwróć tylko pasujące pliki

### Ćwiczenie 3: Dodaj automatyczną analizę po uploadziepo
**Cel:** Agent automatycznie analizuje plik po uploadzie

**Zadanie:**
1. Stwórz callback który uruchamia się po dodaniu pliku
2. Agent automatycznie wywołuje analizę (np. OCR dla PDF, opis dla obrazu)
3. Wynik zapisz jako osobny artifact

---

## 🔧 Troubleshooting

### Problem 1: "Plugin not working"
**Objawy:** Pliki nie są automatycznie importowane

**Rozwiązanie:**
- Upewnij się że używasz `App` zamiast samego agenta
- Sprawdź czy plugin jest w liście `plugins=[]`
- Użyj `adk web` (nie `adk run`)

### Problem 2: "Cannot load artifacts"
**Przyczyna:** Brak narzędzia `load_artifacts` w agencie

**Rozwiązanie:**
```python
from google.adk.tools import load_artifacts

agent = LlmAgent(
    tools=[load_artifacts]  # Dodaj to narzędzie!
)
```

### Problem 3: "File not found after upload"
**Możliwe przyczyny:**
- Plik jest zbyt duży (limit: 10MB domyślnie)
- Nieprawidłowy format pliku
- Błąd w pluginie

**Rozwiązanie:**
- Sprawdź rozmiar pliku
- Użyj wspieranych formatów (PNG, JPG, PDF, TXT)
- Sprawdź logi: `adk web --log-level DEBUG`

---

## 📚 Odniesienia

- [ADK Plugins Docs](https://google.github.io/adk-docs/plugins/)
- [SaveFilesAsArtifactsPlugin](https://google.github.io/adk-docs/plugins/save-files/)
- [App Class](https://google.github.io/adk-docs/apps/)
- [Artifact Service](https://google.github.io/adk-docs/artifacts/)

---

## 📝 Podsumowanie

| Koncepcja | Kluczowy Punkt |
|-----------|----------------|
| **SaveFilesAsArtifactsPlugin** | Auto-import uploadowanych plików |
| **App** | Wrapper łączący agenta z pluginami |
| **Pluginy** | Rozszerzenia funkcjonalności agenta |
| **load_artifacts** | Narzędzie do ładowania plików |
| **Automatyzacja** | Zero ręcznej konfiguracji |

**Poprzedni moduł:** A01 - Wprowadzenie do ADK  
**Następny moduł:** ADK06 - OAuth API Integration


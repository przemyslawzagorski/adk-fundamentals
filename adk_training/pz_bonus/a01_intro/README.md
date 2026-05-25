# Moduł A01: Wprowadzenie do ADK - Generowanie Obrazów z Imagen

## 🎯 Czego się nauczysz?

W tym module poznasz:
- **Generowanie obrazów** z użyciem Imagen 3.0 (Google's image generation model)
- **Artifact Service** - przechowywanie i zarządzanie plikami generowanymi przez agenta
- **ToolContext** - kontekst narzędzi umożliwiający dostęp do artifact service
- **Custom Tools** - tworzenie własnych narzędzi asynchronicznych
- **Integrację** agenta z Google GenAI Client

## 💼 Po co jest ten moduł? (Przypadki biznesowe)

### 1. Marketing & Content Creation
**Scenariusz:** Automatyczne generowanie grafik marketingowych
- Agent generuje obrazy produktów na podstawie opisów
- Zapisuje je w artifact service
- Użytkownik może je pobrać i użyć w kampaniach

**Korzyści:** Oszczędność czasu, spójność wizualna, szybkie prototypowanie

### 2. E-commerce
**Scenariusz:** Wizualizacje produktów
- Klient opisuje produkt słowami
- Agent generuje wizualizację
- Obrazy są automatycznie zapisywane i dostępne

### 3. Edukacja
**Scenariusz:** Materiały dydaktyczne
- Nauczyciel prosi o ilustracje do lekcji
- Agent generuje obrazy edukacyjne
- Materiały są przechowywane i można je ponownie wykorzystać

---

## 🏗️ Architektura i Flow

```
User: "Wygeneruj obraz kota na kanapie"
    ↓
LlmAgent: Analizuje zapytanie
    ↓
LlmAgent: Wywołuje generate_image(prompt="cat on couch...")
    ↓
generate_image():
  1. Wywołuje Imagen 3.0 API
  2. Otrzymuje image_bytes
  3. Zapisuje do artifact service przez tool_context.save_artifact()
  4. Zwraca status success
    ↓
User: Otrzymuje potwierdzenie + może pobrać obraz
```

---

## 🔑 Kluczowe Koncepcje ADK

### 1. **ToolContext** - Kontekst Narzędzi

`ToolContext` to obiekt przekazywany do narzędzi, który daje dostęp do:
- **Artifact Service** - `save_artifact()`, `load_artifact()`, `list_artifacts()`
- **Session** - informacje o bieżącej sesji
- **User** - informacje o użytkowniku

```python
async def my_tool(param: str, tool_context: ToolContext):
    # Zapisz plik
    await tool_context.save_artifact(
        'user:file.png',
        Part.from_bytes(data=bytes, mime_type='image/png')
    )
```

### 2. **Artifact Service** - Przechowywanie Plików

Artifact Service to system przechowywania plików generowanych przez agenta:
- Obrazy, dokumenty, dane
- Dostępne dla użytkownika do pobrania
- Persystentne w ramach sesji

**Namespace:**
- `user:filename` - pliki użytkownika (widoczne w UI)
- `agent:filename` - pliki wewnętrzne agenta

### 3. **Imagen 3.0** - Generowanie Obrazów

Google's model generowania obrazów:
```python
client = Client()  # Google GenAI Client

response = client.models.generate_images(
    model='imagen-3.0-generate-002',
    prompt="A cat sitting on a couch",
    config={'number_of_images': 1}
)

image_bytes = response.generated_images[0].image.image_bytes
```

### 4. **Asynchroniczne Narzędzia**

Narzędzia w ADK mogą być asynchroniczne (`async def`):
```python
async def generate_image(prompt: str, tool_context: ToolContext):
    # Asynchroniczne operacje
    await tool_context.save_artifact(...)
    return {'status': 'success'}
```

---

## 📋 Wymagania

### 1. Google Cloud Project
- Projekt GCP z włączonym Vertex AI
- Włączony Imagen API

### 2. Zmienne środowiskowe (.env)
```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=true
ADK_MODEL=gemini-2.0-flash-001
```

### 3. Instalacja
```bash
pip install google-adk python-dotenv
```

---

## 🚀 Quick Start

### Krok 1: Uruchom agenta
```bash
cd adk_training/a01_intro
adk web
```

### Krok 2: Otwórz przeglądarkę
```
http://127.0.0.1:8000
```

### Krok 3: Testuj
**Przykładowe zapytania:**
- "Generate an image of a cat sitting on a couch eating popcorn"
- "Wygeneruj obraz zachodu słońca nad oceanem"
- "List my files" (pokaż zapisane obrazy)
- "Load the image" (załaduj ostatni obraz)

---

## 🧪 Ćwiczenia

### Ćwiczenie 1: Dodaj parametr `number_of_images`
**Cel:** Pozwól użytkownikowi generować wiele obrazów naraz

**Zadanie:**
1. Zmodyfikuj `generate_image()` aby przyjmowała parametr `count: int = 1`
2. Ustaw `config={'number_of_images': count}`
3. Zapisz wszystkie obrazy z unikalnymi nazwami (`image_1.png`, `image_2.png`, ...)

**Wskazówka:**
```python
for i, img in enumerate(response.generated_images):
    await tool_context.save_artifact(
        f'user:image_{i+1}.png',
        Part.from_bytes(...)
    )
```

### Ćwiczenie 2: Dodaj narzędzie `delete_artifact()`
**Cel:** Pozwól użytkownikowi usuwać zapisane pliki

**Zadanie:**
1. Stwórz funkcję `async def delete_artifact(filename: str, tool_context: ToolContext)`
2. Użyj `await tool_context.delete_artifact(f'user:{filename}')`
3. Dodaj narzędzie do agenta

### Ćwiczenie 3: Dodaj walidację promptu
**Cel:** Sprawdzaj czy prompt jest odpowiedni przed generowaniem

**Zadanie:**
1. Dodaj walidację długości promptu (min 10 znaków)
2. Sprawdź czy prompt nie zawiera zabronionych słów
3. Zwróć błąd jeśli walidacja nie przejdzie

**Przykład:**
```python
if len(prompt) < 10:
    return {'status': 'failed', 'detail': 'Prompt too short (min 10 chars)'}
```

---

## 🔧 Troubleshooting

### Problem 1: "Imagen API not enabled"
**Rozwiązanie:**
```bash
gcloud services enable aiplatform.googleapis.com --project=YOUR_PROJECT
```

### Problem 2: "Could not save artifact"
**Przyczyna:** Brak konfiguracji artifact service

**Rozwiązanie:** Upewnij się że używasz `adk web` (ma wbudowany artifact service)

### Problem 3: "Image generation failed"
**Możliwe przyczyny:**
- Prompt narusza content policy (np. przemoc, nagość)
- Quota exceeded (przekroczono limit API)
- Błędny region (Imagen dostępny tylko w niektórych regionach)

**Rozwiązanie:**
- Zmień prompt na bezpieczny
- Sprawdź quota w GCP Console
- Użyj regionu `us-central1`

---

## 📚 Odniesienia

- [Imagen 3.0 Docs](https://cloud.google.com/vertex-ai/generative-ai/docs/image/overview)
- [ADK Artifact Service](https://google.github.io/adk-docs/artifacts/)
- [ToolContext API](https://google.github.io/adk-docs/tools/tool-context/)
- [Google GenAI Client](https://googleapis.github.io/python-genai/)

---

## 📝 Podsumowanie

| Koncepcja | Kluczowy Punkt |
|-----------|----------------|
| **Imagen 3.0** | Model generowania obrazów Google |
| **ToolContext** | Dostęp do artifact service w narzędziach |
| **Artifact Service** | Przechowywanie plików generowanych przez agenta |
| **Async Tools** | Narzędzia mogą być asynchroniczne |
| **GenAI Client** | Klient do Google's generative AI models |

**Następny moduł:** A03 - Autoimport Files to Artifact Service


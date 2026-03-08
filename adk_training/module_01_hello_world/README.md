# Moduł 1: Hello World Agent - Podstawowy Agent

## 📚 Przegląd

Witaj! To Twoja pierwsza podróż w świat agentów ADK. W tym module stworzysz prostego, ale funkcjonalnego agenta AI - podstawowego asystenta.

**Czas trwania:** 45 minut
**Poziom trudności:** Początkujący (nie wymaga wcześniejszego doświadczenia z ADK)

## 🎯 Cele Edukacyjne

Po ukończeniu tego modułu będziesz potrafił:
- Zrozumieć podstawową strukturę `LlmAgent`
- Skonfigurować parametry: nazwę agenta, model i instrukcje
- Uruchomić agenta za pomocą komendy `adk web`
- Wchodzić w interakcję z agentem przez interfejs webowy

## 📁 Zawartość Modułu

```
module_01_hello_world/
├── agent.py          # Główny kod agenta
├── .env.template     # Szablon konfiguracji środowiska
├── requirements.txt  # Zależności Python
└── README.md         # Ten plik
```

## 🚀 Szybki Start

### Krok 1: Konfiguracja Środowiska

```bash
# Przejdź do tego modułu
cd adk_training/module_01_hello_world

# Stwórz środowisko wirtualne (opcjonalne, ale zalecane)
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Zainstaluj zależności
pip install -r requirements.txt

# Skopiuj szablon środowiska
copy .env.template .env  # Windows
# cp .env.template .env  # macOS/Linux

# Edytuj .env i wpisz swój GCP project ID
```

### Krok 2: Konfiguracja Uwierzytelniania GCP

```bash
# Zaloguj się do Google Cloud
gcloud auth application-default login

# Ustaw swój projekt
gcloud config set project TWOJ_PROJECT_ID
```

### Krok 3: Uruchomienie Agenta

```bash
# Uruchom interfejs webowy ADK
adk web
```

### Krok 4: Testowanie Agenta

1. Otwórz URL pokazany w terminalu (zazwyczaj http://localhost:8000)
2. Wybierz "asystent_podstawowy" z listy rozwijanej agentów
3. Wypróbuj te przykładowe pytania:
   - "Cześć! Kim jesteś?"
   - "Opowiedz mi o Pythonie"
   - "Co sprawia, że agent AI jest dobry?"

## 🔑 Kluczowe Koncepcje

### Klasa LlmAgent

```python
from google.adk.agents import LlmAgent

root_agent = LlmAgent(
    name="nazwa_agenta",         # Unikalny identyfikator
    model="gemini-2.5-flash",    # Model LLM do użycia
    instruction="...",           # Prompt systemowy
    description="...",           # Dla systemów wieloagentowych
)
```

### Ważne Parametry

| Parametr | Opis | Wymagany |
|----------|------|----------|
| `name` | Unikalny identyfikator agenta | Tak |
| `model` | Model LLM (gemini-2.5-flash, itp.) | Tak |
| `instruction` | Prompt systemowy definiujący zachowanie | Tak |
| `description` | Opis celu dla innych agentów | Nie |

## 🏋️ Ćwiczenia

### Ćwiczenie 1.1: Modyfikacja Osobowości
Zmień instrukcję, aby agent był bardziej formalny lub bardziej swobodny.

### Ćwiczenie 1.2: Wypróbuj Różne Modele
Zmień `gemini-2.5-flash` na `gemini-2.0-flash` i zaobserwuj różnice.

### Ćwiczenie 1.3: Dodaj Kontekst
Dodaj specyficzną wiedzę do instrukcji (np. historię firmy, nazwy produktów).

## ❓ Częste Problemy

### Błąd "Could not authenticate"
```bash
# Ponownie uwierzytelnij się z GCP
gcloud auth application-default login
```

### "Vertex AI API not enabled"
```bash
# Włącz API
gcloud services enable aiplatform.googleapis.com
```

### Agent Nie Pojawia Się w Interfejsie Web
- Upewnij się, że zmienna nazywa się `root_agent` (ADK szuka tej nazwy)
- Sprawdź, czy jesteś we właściwym katalogu

## 🎓 Co Dalej?

W **Module 2** nauczysz się dawać agentowi niestandardowe narzędzia - specjalne zdolności do interakcji ze światem poza zwykłą konwersacją!

---

*"Podróż tysiąca linii kodu zaczyna się od jednego agenta."*


# Module 11: Memory Bank Agent - The Ship's Chronicler 📜

## 📖 Czym jest Memory Bank?

**Memory Bank** to system długoterminowej pamięci dla agentów AI, który:
- 🧠 **Pamięta rozmowy** - agent nie zapomina poprzednich interakcji
- 💾 **Przechowuje w chmurze** - dane są persystentne między sesjami
- 🔍 **Wyszukuje semantycznie** - znajduje relevantne informacje z przeszłości
- 🔄 **Konsoliduje wiedzę** - nowe informacje łączą się z istniejącymi

**Przykład:** Powiesz agentowi "Lubię kawę z mlekiem" → Tydzień później agent pamięta Twoje preferencje!

---

## 🆚 Search Engine vs Agent Engine - Różnice

| Cecha | **Vertex AI Search** (Module 3) | **Agent Engine** (Module 11) |
|-------|--------------------------------|------------------------------|
| **Cel** | Wyszukiwanie w dokumentach | Zarządzanie pamięcią agenta |
| **Funkcja** | Indeksuje i przeszukuje pliki | Przechowuje memories z rozmów |
| **Użycie** | RAG - odpowiedzi z dokumentów | Memory Bank - długoterminowa pamięć |
| **Dane** | Statyczne dokumenty (PDF, HTML) | Dynamiczne memories z konwersacji |
| **Przykład** | "Znajdź w dokumentacji info o API" | "Pamiętaj że lubię kawę z mlekiem" |

**Krótko:**
- **Search Engine** = Wyszukiwarka w Twoich dokumentach
- **Agent Engine** = Mózg agenta z długoterminową pamięcią

---

## 🏗️ Czym jest Agent Engine?

**Agent Engine** to zasób w Vertex AI, który:

1. **Zarządza Memory Bank** - przechowuje memories w vector database
2. **Obsługuje Sessions** - śledzi historię rozmów
3. **Zapewnia API** - GenerateMemories, RetrieveMemories
4. **Skaluje automatycznie** - zarządzane przez Google Cloud

**Analogia:** Agent Engine to jak "serwer bazy danych" dla pamięci Twojego agenta.

### Czy można go wyklikać w GCP Console?

**TAK!** Podobnie jak Search Engine:

1. Przejdź do: https://console.cloud.google.com/vertex-ai/agent-builder
2. Kliknij "Create Agent Engine"
3. Wybierz konfigurację
4. Skopiuj Agent Engine ID

**ALE** w tym module używamy **skryptu Python** (`create_agent_engine.py`), który robi to automatycznie - szybciej i wygodniej!

---

## 🎯 Czego się nauczysz?

- ✅ Jak działa Memory Bank w ADK
- ✅ Jak utworzyć Agent Engine (skrypt lub GUI)
- ✅ Jak agent automatycznie zapisuje memories
- ✅ Jak agent wyszukuje memories z przeszłości
- ✅ Jak testować pamięć między sesjami
- ✅ Jak używać `adk web` do interaktywnego testowania

---

## 📁 Pliki w Module

| Plik | Opis |
|------|------|
| **`agent.py`** | Agent produkcyjny z Memory Bank |
| **`.env.template`** | Template konfiguracji (skopiuj do `.env`) |
| **`create_agent_engine.py`** | Skrypt do tworzenia Agent Engine |
| **`test_connection.py`** | Test połączenia z GCP |
| **`test_memory_production.py`** | Test end-to-end Memory Bank |
| `requirements.txt` | Zależności Python |
| `diagrams/` | Diagramy architektury (Mermaid) |

---

## 🔧 Jak działa Memory Bank?

### 1. **Generowanie Memories** (automatyczne)

```
User: "Znaleźliśmy skarb na Skull Island!"
  ↓
Agent odpowiada
  ↓
Callback (auto): zapisuje do Memory Bank
  ↓
Vertex AI: ekstrahuje "User found treasure on Skull Island"
  ↓
Memory Bank: zapisuje w vector database
```

### 2. **Wyszukiwanie Memories** (automatyczne)

```
User: "Gdzie znaleźliśmy skarb?" (nowa sesja!)
  ↓
PreloadMemoryTool: automatycznie ładuje memories
  ↓
Vertex AI: wyszukuje semantycznie "treasure location"
  ↓
Memory Bank: zwraca "treasure on Skull Island"
  ↓
Agent: "Skarb był na Skull Island!"
```

### 3. **Kod - Inicjalizacja**

```python
from google.adk.memory import VertexAiMemoryBankService
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

# Memory Service
memory_service = VertexAiMemoryBankService(
    project="your-project-id",
    location="us-central1",
    agent_engine_id="1234567890"  # Z create_agent_engine.py
)

# Auto-save callback
async def auto_save(callback_context):
    recent_events = callback_context.session.events[-5:]
    await callback_context.add_events_to_memory(events=recent_events)

# Agent z pamięcią
agent = LlmAgent(
    model="gemini-2.5-flash",
    tools=[PreloadMemoryTool()],  # Auto-load memories
    after_agent_callback=auto_save  # Auto-save memories
)
```

**Zobacz diagramy:** `diagrams/architecture.mmd` i `diagrams/flow.mmd`

---

## 🚀 Quick Start (5 minut)

### Wymagania

- ✅ Projekt Google Cloud
- ✅ Python 3.10+
- ✅ `gcloud` CLI zainstalowane

### Krok 1: Uwierzytelnienie GCP

```bash
# Zaloguj się do GCP
gcloud auth login

# Ustaw domyślne uwierzytelnianie dla aplikacji
gcloud auth application-default login

# Włącz Vertex AI API
gcloud services enable aiplatform.googleapis.com
```

### Krok 2: Konfiguracja Projektu

```bash
cd adk_training/module_11_memory_bank

# Skopiuj template
cp .env.template .env

# Edytuj .env i wpisz:
# GOOGLE_CLOUD_PROJECT=twoj-projekt-id
# GOOGLE_CLOUD_LOCATION=us-central1
```

### Krok 3: Utwórz Agent Engine

**Opcja A: Przez skrypt (zalecane)**
```bash
python create_agent_engine.py
# Skopiuj wyświetlony Agent Engine ID do .env
```

**Opcja B: Przez GCP Console**
1. Przejdź do: https://console.cloud.google.com/vertex-ai/agent-builder
2. Kliknij "Create Agent Engine"
3. Skopiuj ID do `.env` jako `AGENT_ENGINE_ID`

### Krok 4: Test Połączenia

```bash
python test_connection.py
# Oczekiwany wynik: ✅ ALL TESTS PASSED!
```

### Krok 5: Testowanie z `adk web`

```bash
# Uruchom interfejs webowy
adk web --memory_service_uri=agentengine://1234567890

# Otwórz w przeglądarce: http://localhost:8000
```

**Testuj pamięć:**
1. Powiedz: "Znaleźliśmy skarb na Skull Island!"
2. Zamknij przeglądarkę
3. Otwórz ponownie i zapytaj: "Gdzie znaleźliśmy skarb?"
4. Agent powinien pamiętać! 🎉

---

## 💰 Koszty

| Operacja | Koszt (szacunkowy) |
|----------|-------------------|
| Memory Generation | ~$0.001 / 1K chars |
| Memory Retrieval | ~$0.0005 / query |
| Storage | ~$0.30 / GB / month |

**Przykłady:**
- 10 konwersacji: ~$0.01
- 100 konwersacji: ~$0.10 - $0.50
- 1000 konwersacji: ~$1.00 - $5.00

💡 **Free Tier:** Nowi użytkownicy GCP dostają $300 credits - wystarczy na tysiące testów!

---

## ❓ Rozwiązywanie Problemów

### Problem: "Permission denied"
```bash
gcloud projects add-iam-policy-binding YOUR-PROJECT \
    --member="user:YOUR-EMAIL" \
    --role="roles/aiplatform.user"
```

### Problem: "API not enabled"
```bash
gcloud services enable aiplatform.googleapis.com
```

### Problem: "Invalid Agent Engine ID"
- Użyj tylko ID (liczby), nie pełnej nazwy zasobu
- ✅ Poprawnie: `1234567890`
- ❌ Błędnie: `projects/.../reasoningEngines/1234567890`

### Problem: "Authentication error"
```bash
gcloud auth application-default login
```

### Problem: Agent nie pamięta między sesjami
- Sprawdź czy `after_agent_callback` jest ustawiony
- Poczekaj 5-10 sekund na przetworzenie memories
- Sprawdź logi: `python test_memory_production.py`

---

## 📚 Dodatkowe Zasoby

- **Diagramy:** `diagrams/architecture.mmd`, `diagrams/flow.mmd`
- **ADK Docs:** https://google.github.io/adk-docs/sessions/memory/
- **Vertex AI Docs:** https://cloud.google.com/vertex-ai/docs/agent-builder/memory-bank
- **GCP Console:** https://console.cloud.google.com/vertex-ai/agent-builder

---

## ✅ Checklist

Przed uruchomieniem sprawdź:

- [ ] Projekt GCP utworzony/wybrany
- [ ] Vertex AI API włączone (`gcloud services enable aiplatform.googleapis.com`)
- [ ] Uwierzytelnienie OK (`gcloud auth application-default login`)
- [ ] Agent Engine utworzony (`python create_agent_engine.py`)
- [ ] Plik `.env` wypełniony (PROJECT_ID + AGENT_ENGINE_ID)
- [ ] Test połączenia przeszedł (`python test_connection.py`)
- [ ] Dependencies zainstalowane (`pip install -r requirements.txt`)

---

## 🎯 Podsumowanie

**Module 11** pokazuje jak zbudować agenta z **prawdziwą długoterminową pamięcią**:

✅ **Agent Engine** zarządza pamięcią w chmurze
✅ **Memory Bank** przechowuje memories między sesjami
✅ **PreloadMemoryTool** automatycznie ładuje kontekst
✅ **Callback** automatycznie zapisuje nowe informacje
✅ **Semantic search** znajduje relevantne memories

**Testuj z `adk web`** - najprostszy sposób na eksperymentowanie! 🚀

---

*"Those who forget history are doomed to sail in circles!"* 🏴‍☠️

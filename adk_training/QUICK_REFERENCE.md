# 🏴‍☠️ QUICK REFERENCE - Google ADK
## *Ściągawka dla Kapitanów*

---

## 🚀 PODSTAWY

### Uruchomienie Agenta
```bash
# Web UI (polecane)
adk web

# CLI
adk run

# Custom port
adk web --port 8001
```

### Struktura Projektu
```
my_agent/
├── agent.py          # Główny plik agenta
├── .env              # Zmienne środowiskowe
├── __init__.py       # Pusty plik (wymagany)
└── README.md         # Dokumentacja
```

---

## 📚 WZORCE KODU

### 1. Hello World - Podstawowy Agent
```python
from google.adk.agents import LlmAgent

agent = LlmAgent(
    name="kapitan",
    model="gemini-2.5-flash",
    instruction="Jesteś kapitanem piratów...",
    description="Kapitan statku"
)
```

### 2. Custom Tool - Narzędzie
```python
def sprawdz_skarb(nazwa: str) -> str:
    """Sprawdza ile mamy skarbu.
    
    Args:
        nazwa: Nazwa skarbu
    """
    return f"Mamy {SKARBY[nazwa]} sztuk"

agent = LlmAgent(
    tools=[sprawdz_skarb]  # Dodaj narzędzie
)
```

### 3. Sequential - Pipeline
```python
from google.adk.agents import SequentialAgent

zwiadowca = LlmAgent(
    name="zwiadowca",
    output_key="raport"  # Zapisz wynik
)

strateg = LlmAgent(
    name="strateg",
    instruction="Na podstawie: {raport}"  # Użyj wyniku
)

pipeline = SequentialAgent(
    sub_agents=[zwiadowca, strateg]  # Po kolei
)
```

### 4. Parallel - Równoległość
```python
from google.adk.agents import ParallelAgent

parallel = ParallelAgent(
    sub_agents=[agent1, agent2, agent3]  # Równocześnie
)
```

### 5. Router - Routing
```python
from google.adk.agents import RouterAgent

navigator = LlmAgent(
    description="Ekspert od nawigacji"  # Ważne!
)

router = RouterAgent(
    sub_agents=[navigator, gunner, cook]  # Wybierze 1
)
```

### 6. Human-in-Loop - Zatwierdzenia
```python
from google.adk.tools import FunctionTool

agent = LlmAgent(
    tools=[
        FunctionTool(wydaj_zloto, require_confirmation=True)
    ]
)
```

### 7. Loop - Iteracje
```python
from google.adk.agents import LoopAgent

loop = LoopAgent(
    sub_agents=[creator, critic],
    max_iterations=5  # Max 5 iteracji
)
```

### 8. Database - SQLite
```python
import sqlite3

def zapisz(data: str) -> str:
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ...")
    conn.commit()
    conn.close()
```

### 9. Memory Bank - Pamięć
```python
from google.adk.memory import VertexAiMemoryBankService
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

memory = VertexAiMemoryBankService(
    project=PROJECT_ID,
    location=REGION,
    agent_engine_id=ENGINE_ID
)

agent = LlmAgent(
    tools=[PreloadMemoryTool()]  # Auto-load
)
```

### 10. RAG - Wyszukiwanie
```python
from google.adk.tools import VertexAiSearchTool

search = VertexAiSearchTool(
    data_store_id="my_datastore",
    max_results=5
)

agent = LlmAgent(
    tools=[search]
)
```

---

## 🔧 ZMIENNE ŚRODOWISKOWE (.env)

```bash
# Podstawowe
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=true
ADK_MODEL=gemini-2.5-flash

# OAuth (Module 15, 16)
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx

# Memory Bank (Module 11)
AGENT_ENGINE_RESOURCE_NAME=projects/.../agentEngines/...
```

---

## 🐛 DEBUGGING

### Sprawdź Logi
```bash
# Verbose mode
adk web --log-level DEBUG

# Sprawdź błędy importu
python -c "from google.adk.agents import LlmAgent"
```

### Typowe Błędy

**1. NameError: 'FunctionTool' is not defined**
```python
# Dodaj import
from google.adk.tools import FunctionTool
```

**2. Tool nie działa**
```python
# Sprawdź:
# ✅ Docstring?
# ✅ Type hints?
# ✅ Dodany do tools=[]?
```

**3. State nie przekazuje się**
```python
# Sprawdź:
# ✅ output_key ustawiony?
# ✅ {key_name} w instruction?
```

**4. Agent nie odpowiada**
```bash
# Sprawdź quota
gcloud alpha billing quotas list --service=aiplatform.googleapis.com
```

---

## 📖 SŁOWNIK TERMINÓW

| Termin | Znaczenie | Przykład |
|--------|-----------|----------|
| **LlmAgent** | Podstawowy agent | Kapitan, Quartermaster |
| **Tool** | Narzędzie (funkcja Python) | sprawdz_skarb() |
| **Instruction** | System prompt | "Jesteś kapitanem..." |
| **output_key** | Klucz do zapisania wyniku | "raport_wywiadu" |
| **State** | Stan sesji (dane między agentami) | {raport: "..."} |
| **SequentialAgent** | Pipeline (po kolei) | A → B → C |
| **ParallelAgent** | Równoległość | A + B + C |
| **RouterAgent** | Routing (wybiera 1) | A lub B lub C |
| **Callback** | Funkcja wywoływana przed/po | before_tool_callback |
| **LoopAgent** | Iteracje | A → B → A → B ... |
| **Memory Bank** | Pamięć długoterminowa | Vertex AI |
| **RAG** | Retrieval-Augmented Generation | LLM + Search |

---

## 🎯 BEST PRACTICES

### ✅ DO
- Używaj jasnych nazw (agent, tool, key)
- Pisz szczegółowe docstringi
- Dodawaj type hints
- Testuj każdy moduł osobno
- Używaj `adk web` (łatwiejsze debugowanie)
- Zapisuj dane (database, memory)
- Waliduj input w tools
- Dodawaj confirmation dla ważnych akcji

### ❌ DON'T
- Nie używaj zbyt długich instructions (max 500 słów)
- Nie zapominaj o `output_key` w Sequential
- Nie używaj Parallel dla zależnych zadań
- Nie używaj zbyt wysokiej temperature (>0.9)
- Nie zapominaj o `conn.commit()` w database
- Nie twórz nieskończonych pętli (max_iterations!)
- Nie używaj production API keys w kodzie (użyj .env)

---

## 🔗 LINKI

- **ADK Docs:** https://google.github.io/adk-docs/
- **Gemini API:** https://ai.google.dev/gemini-api
- **Vertex AI:** https://cloud.google.com/vertex-ai
- **GitHub:** https://github.com/google/adk
- **Przykłady:** https://github.com/google/adk/tree/main/examples

---

## 🏴‍☠️ PIRACKI SŁOWNIK

| Polski | Piracki | Użycie |
|--------|---------|--------|
| Witaj | Ahoj! | Powitanie |
| Tak | Aye! | Zgoda |
| Nie | Nay! | Odmowa |
| Wow | Shiver me timbers! | Zdziwienie |
| Cholera | Blimey! | Frustracja |
| Idź | Weigh anchor! | Rozpoczęcie |
| Stop | Avast! | Zatrzymanie |
| Pieniądze | Doubloons | Złoto |
| Statek | Ship, Vessel | Galeon |
| Kapitan | Captain | Dowódca |

---

**Powodzenia, Kapitanie!** ⚓🏴‍☠️


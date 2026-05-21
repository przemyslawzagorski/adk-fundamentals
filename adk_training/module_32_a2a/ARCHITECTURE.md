# Module 32 — A2A Protocol: Exposing & Consuming Remote Agents

> Dokumentacja: https://adk.dev/a2a/quickstart-exposing/ | https://adk.dev/a2a/quickstart-consuming/

## 1. Czym jest A2A (Agent-to-Agent)?

A2A to protokół Google pozwalający agentom komunikować się ze sobą przez HTTP/JSON, niezależnie od frameworka, języka czy lokalizacji. Agent wystawiający się przez A2A staje się **mikrousługą** wywoływalną przez inne agenty.

```
┌──────────────────────────────┐
│  PRODUCER (port 8001)        │  ← wystawiany przez to_a2a() lub adk api_server --a2a
│  code_analyst_agent          │
│  scan_for_hardcoded_secrets  │
│  scan_for_sql_injection      │
└──────────┬───────────────────┘
           │ A2A Protocol (HTTP/JSON)
           ▼
┌──────────────────────────────┐
│  CONSUMER (port 8000)        │  ← root_agent z RemoteA2aAgent
│  code_security_orchestrator  │
│  read_file_snippet (local)   │
│  code_analyst_remote (A2A)   │
└──────────────────────────────┘
```

---

## 2. Dwa sposoby wystawiania agenta przez A2A

### Sposób A: `to_a2a()` — prosta konwersja istniejącego agenta ✅ (ten moduł)

```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a

root_agent = LlmAgent(name="code_analyst_agent", ...)
a2a_app = to_a2a(root_agent, port=8001)
```

**Zalety:**
- ✅ Auto-generuje `agent-card.json` z metadanych agenta
- ✅ Jeden endpoint = jeden agent
- ✅ Pełna kontrola nad serwerem (uvicorn)

**Uruchomienie:**
```bash
uvicorn adk_training.module_32_a2a.remote_a2a.code_analyst.agent:a2a_app \
    --host localhost --port 8001
```

### Sposób B: `adk api_server --a2a` — wielu agentów z jednego folderu

```bash
# Serwuje wszystkich agentów z folderu mających agent-card.json
adk api_server --a2a --port 8001 adk_training/module_32_a2a/remote_a2a/
```

Każdy agent musi mieć plik `agent-card.json` w swoim katalogu.
URL agenta: `http://localhost:8001/a2a/{agent_name}`

---

## 3. Under the hood: co robi `to_a2a()`?

```
to_a2a(root_agent, port=8001)
│
├── A2aAgentExecutor         ← mostek ADK ↔ A2A (obsługuje zapytania)
│   └── default Runner       ← InMemoryArtifactService, InMemorySessionService
│
├── InMemoryTaskStore        ← śledzi status zadań A2A
├── InMemoryPushNotificationConfigStore
│
├── DefaultRequestHandler    ← routuje HTTP → Executor
│
└── Starlette App
    ├── GET /.well-known/agent-card.json   ← auto-generowany agent card
    └── POST /                              ← endpoint A2A (JSON-RPC)
```

---

## 4. Konsumowanie zdalnego agenta: `RemoteA2aAgent`

```python
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH

code_analyst_remote = RemoteA2aAgent(
    name="code_analyst_agent",
    description="Analizuje bezpieczeństwo kodu przez A2A.",
    agent_card=f"http://localhost:8001{AGENT_CARD_WELL_KNOWN_PATH}",
    use_legacy=False,   # ✅ nowy executor z A2A extension
)
```

**Parametry:**
| Parametr | Opis |
|---|---|
| `name` | Unikalna nazwa — musi pasować do nazwy zdalnego agenta |
| `description` | Jak orchestratorowy LLM ma wiedzieć kiedy delegować |
| `agent_card` | URL do `.well-known/agent-card.json` |
| `use_legacy=False` | Nowy executor (wysyła A2A extension header) |

**Jak ADK używa `RemoteA2aAgent`:**
1. Orchestrator LLM decyduje że task pasuje do `code_analyst_agent`
2. ADK serializuje request do formatu A2A (JSON-RPC)
3. HTTP POST do `http://localhost:8001/`
4. Zdalny agent przetwarza, zwraca JSON
5. ADK deserializuje odpowiedź i zwraca ją jako `Event` do orchestratora

---

## 5. Agent Card — format i znaczenie

```json
{
  "name": "code_analyst_agent",
  "description": "...",
  "url": "http://localhost:8001/a2a/code_analyst_agent",
  "version": "1.0.0",
  "capabilities": {},
  "defaultInputModes": ["text/plain"],
  "defaultOutputModes": ["application/json"],
  "skills": [
    {
      "id": "secret_detection",
      "name": "Hardcoded Secrets Detection",
      "description": "...",
      "tags": ["security", "secrets"]
    }
  ]
}
```

Agent card to **kontrakt** między producentem a konsumentem.
Dostępny pod: `GET http://localhost:8001/.well-known/agent-card.json`

---

## 6. Krok po kroku — jak uruchomić moduł

### Terminal 1 — PRODUCER (remote agent):
```bash
# Z katalogu głównego projektu:
uvicorn adk_training.module_32_a2a.remote_a2a.code_analyst.agent:a2a_app \
    --host localhost --port 8001

# Weryfikacja:
curl http://localhost:8001/.well-known/agent-card.json
```

### Terminal 2 — CONSUMER (root agent):
```bash
adk web adk_training/
# Wybierz: module_32_a2a
# Otwórz: http://localhost:8000
```

### Przykładowe prompty:
```
# Analiza wklejonego kodu:
"Przeanalizuj bezpieczeństwo tego kodu:
password = 'admin123'
query = 'SELECT * FROM users WHERE id = ' + user_id"

# Analiza pliku z dysku:
"Sprawdź bezpieczeństwo pliku adk_training/module_09_database_simple/database_tools.py"
```

---

## 7. Zaawansowane: Custom Converters i Interceptors

```python
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, A2aRemoteAgentConfig

def my_before_request(message, context):
    """Dodaj custom header lub zmodyfikuj request przed wysłaniem."""
    print(f"[INTERCEPTOR] Wysyłam do A2A: {message}")
    return message

code_analyst_remote = RemoteA2aAgent(
    name="code_analyst_agent",
    agent_card=f"http://localhost:8001{AGENT_CARD_WELL_KNOWN_PATH}",
    use_legacy=False,
    config=A2aRemoteAgentConfig(
        request_interceptors=[my_before_request],
    ),
)
```

**Hooks dostępne w A2aRemoteAgentConfig:**
| Hook | Kiedy wywoływany |
|---|---|
| `before_request` | Przed wysłaniem do zdalnego agenta — modyfikuj lub blokuj |
| `after_request` | Po otrzymaniu odpowiedzi — filtruj lub transformuj |
| `a2a_message_converter` | Konwertuje A2A Message → ADK Event |
| `a2a_part_converter` | Konwertuje A2A Part → GenAI Part (low-level) |

---

## 8. Agent Executor V2 (nowy)

```python
from google.adk.a2a.executor import A2aAgentExecutor

executor = A2aAgentExecutor(
    ...,
    force_new_version=True  # wymusza V2 bez sprawdzania nagłówka
)
a2a_app = to_a2a(root_agent, port=8001, executor=executor)
```

Użyj gdy chcesz przetestować nowy executor bez modyfikowania klientów.

---

## 9. TODO dla developera

- [ ] Dodaj autentykację: `A2aRemoteAgentConfig(request_metadata={"X-API-Key": "..."})` 
- [ ] Przetestuj z dwoma instancjami tego samego agenta (load balancing)
- [ ] Zamień `to_a2a()` na `adk api_server --a2a` i porównaj DX
- [ ] Dodaj `push_notification_config` dla asynchronicznych odpowiedzi
- [ ] Utwórz `agent-card.json` z własnym AgentCard object zamiast auto-generate
- [ ] Zmień port przez `ADK_A2A_PORT=8002` env var
- [ ] Zaimplementuj własny `adk_event_converter` dla niestandardowego formatu JSON

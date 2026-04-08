# 🧪 Test Flow — Analyst Assistant Demo

## Przygotowanie (zrób to PRZED demo)

### 1. Uzupełnij tokeny w `.env`
```
GOOGLE_API_KEY=...
JIRA_BEARER_TOKEN=...
WIKI_BEARER_TOKEN=...
```

### 2. Terminal 1 — uruchom MCP server
```powershell
cd adk_training/pz_bonus/copilot/analyst_assistant
.\start_mcp.ps1
```
✅ Oczekiwany output: `Listening on http://127.0.0.1:3000`

### 3. Terminal 2 — uruchom agenta
```powershell
cd adk_training/pz_bonus/copilot/analyst_assistant
pip install -r requirements.txt   # tylko raz
adk web
```
✅ Oczekiwany output: `ADK Web UI available at http://localhost:8000`

Otwórz: **http://localhost:8000**

---

## Scenariusz 1 — HLD dla Notification Hub 🏗️

**Pliki do wklejenia** (z `test_materials/hld/`):
- `feature_request.txt` — wklej całą zawartość do chatu
- `existing_architecture_notes.txt` — wklej całą zawartość do chatu

### Krok 1: Uruchom
```
Wygeneruj HLD dla Notification Hub Service na podstawie poniższych dokumentów:

[wklej zawartość feature_request.txt]

--- ARCHITEKTURA ---

[wklej zawartość existing_architecture_notes.txt]
```

### Czego się spodziewać

| Etap | Co pokaże agent |
|------|----------------|
| Routing | Orchestrator rozpoznaje HLD i przekazuje do `hld_pipeline` |
| Pytania (HITL) | Agent pyta o brakujące NFR: latency, throughput, availability targets |
| Pytania (HITL) | Agent pyta o decyzję SMS provider: Twilio vs AWS SNS |
| Pytania (HITL) | Agent pyta o primary interface: Kafka vs REST |
| Iteracja 1 | Writer generuje pierwszy draft HLD |
| Iteracja 2 | Critic wskazuje braki, writer poprawia |
| Finalizacja | generate_docx() zapisuje plik do `output/HLD_Notification_Hub_*.docx` |

---

## Scenariusz 2 — Test Cases dla Document Upload 📋

**Pliki do wklejenia** (z `test_materials/test_cases/`):
- `acceptance_criteria.txt`
- `api_spec_partial.txt`

### Krok 1: Uruchom
```
Napisz test cases dla funkcjonalności Document Upload KYC na podstawie:

[wklej zawartość acceptance_criteria.txt]

--- API SPEC ---

[wklej zawartość api_spec_partial.txt]
```

### Czego się spodziewać

| Etap | Co pokaże agent |
|------|----------------|
| Routing | Orchestrator przekazuje do `test_cases_pipeline` |
| Pytania (HITL) | Agent pyta o max liczbę dokumentów per klient (AC nie definiuje) |
| Pytania (HITL) | Agent pyta o środowiska testowe (SIT/UAT — storage backend niezdefiniowany) |
| Pytania (HITL) | Agent pyta o virus scanner (ClamAV vs Defender) |
| Iteracja 1 | Writer generuje ≥ 5 positive + 3 negative + 1 NFR test case |
| Iteracja 2 | Critic weryfikuje TC-ID, preconditions, expected results |
| Finalizacja | generate_docx() zapisuje `output/TEST_CASES_Document_Upload_*.docx` |

---

## Scenariusz 3 — Kombinacja z Jira (bonus, jeśli MCP działa) 🎯

```
Wygeneruj HLD dla Notification Hub. Pobierz kontekst z Jira — epic CLM6-8821
i powiązane stories. Użyj tego jako głównego źródła wymagań.
```

Agent sam zaquery'uje Jira przez MCP i uzupełni kontekst bez wklejania plików.

---

## Lokalizacja wygenerowanych plików

```
analyst_assistant/output/
  HLD_Notification_Hub_Service_20260324_143022.docx
  TEST_CASES_Document_Upload_KYC_20260324_151545.docx
```

---

## Troubleshooting

| Problem | Rozwiązanie |
|---------|-------------|
| MCP nie startuje | Sprawdź czy Node.js v18+ jest zainstalowany: `node --version` |
| `npx` nie pobiera pakietu | Sprawdź połączenie z siecią Comarch / VPN |
| Agent nie widzi MCP tools | Sprawdź czy serwer działa na porcie 3000 i `.env` ma poprawny `MCP_SERVER_URL` |
| generate_docx() fail | Sprawdź czy `python-docx` jest zainstalowany: `pip install python-docx` |
| Agent zapętla się | Sprawdź logi w terminalu 2 — limit 3 iteracje w LoopAgent |


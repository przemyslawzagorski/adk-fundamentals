# ADK Training Materials

Materiały szkoleniowe do Google Agent Development Kit (ADK) z przykładami agentów AI.

## 🚀 Quick Start

### 1. Wymagania wstępne

- Python 3.12 lub nowszy
- Konto Google Cloud Platform (GCP)
- `gcloud` CLI zainstalowane i skonfigurowane

### 2. Instalacja

```bash
# Sklonuj repozytorium
git clone <your-repo-url>
cd adk_training

# Utwórz wirtualne środowisko
python -m venv venv

# Aktywuj środowisko
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Zainstaluj zależności
pip install -r d1_01_hello_agent/requirements.txt
```

### 3. Konfiguracja GCP

```bash
# Zaloguj się do GCP
gcloud auth application-default login

# Ustaw domyślny projekt (opcjonalnie)
gcloud config set project YOUR_PROJECT_ID
```

### 4. Konfiguracja zmiennych środowiskowych

```bash
# Skopiuj przykładowy plik .env
cp .env.example .env

# Edytuj .env i wypełnij swoimi wartościami:
# - GOOGLE_CLOUD_PROJECT=twoj-projekt-id
# - GOOGLE_CLOUD_LOCATION=global
```

## 🗓️ Program szkolenia (ADK 2.13, model `gemini-3.5-flash-lite`)

Katalogi mają nazwy `d<dzień>_<nr ćwiczenia><wariant>_<temat>`, zgodne z numeracją ćwiczeń
na slajdach (D1.1 … D2.6). Dropdown `adk web` sortuje alfabetycznie, więc pokazuje moduły
**dokładnie w kolejności szkolenia**.

- `a` / `b`: warianty jednego ćwiczenia (np. `a` = ADK 1 legacy, `b` = ADK 2 `Workflow`);
- `x_ext`: moduł rozszerzający (opcjonalny), wstawiony tam, gdzie pasuje tematycznie.

```powershell
cd adk_training
adk web --reload_agents      # wszystkie moduły w jednym dropdownie
```

Wyjątek: D1.5 (`python ui.py` z katalogu modułu).

### Dzień 1 – agent i orkiestracja

| Ćw. | Katalog | Temat |
|---|---|---|
| D1.1 | `d1_01_hello_agent` | Pierwszy agent, model w `.env`, `google_search` |
| D1.2 | `d1_02_custom_tools` | Własne narzędzia, łańcuch wywołań |
| D1.3 | `d1_03_rag_vertex_search` | RAG: Vertex AI Search (indeks prowadzącego) |
| ext | `d1_03x_ext_local_rag` | RAG na lokalnych plikach |
| D1.4 | `d1_03_rag_vertex_search` (zmiana `.env`) | RAG na **własnym** indeksie (bucket → datastore → app) |
| D1.5 | `d1_05_runner_session_gradio` | Runner, sesja i stan we własnym UI (Gradio) |
| D1.6 | `d1_06a_sequence_adk1_legacy` → `d1_06b_workflow_sequence` | Sekwencja: `SequentialAgent` → `Workflow` |
| ext | `d1_06x_ext_data_handling` | Przepływ danych w grafie |
| D1.7 | `d1_07a_parallel_adk1_legacy` → `d1_07b_workflow_parallel` | Równoległość: fan-out + `JoinNode` |
| D1.8 | `d1_08a_loop_adk1_legacy` → `d1_08b_workflow_loop` | Pętla krytyki przez routing |
| ext | `d1_08x_ext_collaboration`, `d1_08x_ext_dynamic_graphs` | `@node`, `ctx.run_node`, dynamiczne grafy |
| D1.9 | `d1_09_hitl_callbacks` | Human-in-the-loop przez callbacki |
| ext | `d1_09x_ext_human_input_workflow` | HITL natywnie w Workflow (`RequestInput`) |
| D1.10 | `d1_10a_router_transfer`, `d1_10b_task_api` | Delegacja: transfer / AgentTool / Task API |
| ext | `d1_10x_ext_graph_routes` | Routing deterministyczny `Event(route=)` |
| D1.11 | `d1_11a_react_planner` vs `d1_11b_builtin_planner` | Plannery: ReAct vs thinking modelu |
| D1.12 | `d1_12_deploy_cloud_run` | Deploy na Cloud Run |

### Dzień 2 – integracje i produkcja

| Ćw. | Katalog | Temat |
|---|---|---|
| D2.1 | `d2_01_artifacts` | Obrazy i wersjonowane artefakty |
| ext | `d2_01x_ext_autoimport_artifacts` | `SaveFilesAsArtifactsPlugin` |
| D2.2 | `d2_02_memory_bank` | Memory Bank (Agent Engine) |
| D2.3 | `d2_03a_database_sqlite` → `d2_03b_database_postgres_mcp` | Baza danych: SQLite, potem Postgres przez MCP Toolbox |
| D2.4 | `d2_04a_mcp_servers`, `d2_04b_oauth_openapi` | MCP (gotowy i własny serwer), OAuth + OpenAPI |
| ext | `d2_04x_ext_a2a`, `d2_04x_ext_gmail` | A2A, Gmail |
| D2.5 | `d2_05_agent_skills` | Agent Skills |
| D2.6 | `d2_06a_evaluation` → `d2_06b_e2e_tester` | Ewaluacja (`adk eval`), testy E2E |

> `Workflow` nie może jeszcze być sub-agentem `LlmAgent` (ograniczenie ADK 2.13),
> dlatego router z `d1_10a` i ewaluacja z `d2_06a` nadal bazują na `Agent`/`LlmAgent`.

**Rozwiązania** (`agent_solution.py`) prowadzący publikuje po ćwiczeniu, a Ty pobierasz je przez `git pull`.

Moduły produkcyjne spoza programu (code analyst, analyst system, spec generator, Auggie,
AuditOps, workflows) są dostępne na branchu `main`.

## 📧 `d2_04x_ext_gmail`: Gmail Integration – konfiguracja OAuth

**WAŻNE**: Każdy użytkownik musi skonfigurować własne OAuth credentials!

### Dlaczego nie mogę użyć Twoich credentials?

OAuth 2.0 dla Gmail wymaga **interaktywnego logowania** przez przeglądarkę. Proces wygląda tak:

1. **Developer (Ty)** tworzy OAuth Client ID w swoim projekcie GCP
2. **User (kolega)** musi zalogować się przez przeglądarkę do **swojego** konta Gmail
3. Google generuje token dostępu dla **tego konkretnego użytkownika**

**Nie można** udostępnić tokenu, bo:
- Token jest przypisany do konkretnego konta Gmail
- Token wygasa i wymaga odświeżenia
- Naruszałoby to bezpieczeństwo (dostęp do cudzego Gmaila)

### Jak skonfigurować Gmail dla kolegi?

#### Opcja A: Kolega używa Twojego projektu GCP (ZALECANE)

1. **Ty (właściciel projektu GCP)**:
   - Dodaj kolegę jako użytkownika testowego w OAuth consent screen
   - Udostępnij mu Client ID i Client Secret (można przez .env)

2. **Kolega**:
   - Kopiuje Client ID i Client Secret do swojego `.env`
   - Uruchamia `adk web` i loguje się do **swojego** Gmaila
   - Google generuje token dla jego konta

#### Opcja B: Kolega tworzy własny projekt GCP

1. Kolega tworzy własny projekt GCP
2. Włącza Gmail API
3. Tworzy własny OAuth Client ID
4. Konfiguruje OAuth consent screen
5. Używa swoich credentials

### Instrukcje dla kolegi (Opcja A)

```bash
# 1. Skopiuj .env.example jako .env
cp .env.example .env

# 2. Wypełnij .env (dostaniesz ode mnie):
# GOOGLE_CLOUD_PROJECT=moj-projekt-id
# GMAIL_CLIENT_ID=twoj-client-id.apps.googleusercontent.com
# GMAIL_CLIENT_SECRET=twoj-client-secret

# 3. Uruchom ADK web interface
cd adk_training/d2_04x_ext_gmail
adk web

# 4. Otwórz przeglądarkę i zaloguj się do SWOJEGO Gmaila
# 5. Zatwierdź dostęp
# 6. Token zostanie zapisany lokalnie (NIE commituj go!)
```

## 📁 Struktura projektu

```
adk_training/
├── .env.example              # Przykładowa konfiguracja
├── .gitignore               # Ignorowane pliki
├── README.md                # Ten plik
├── d1_01_hello_agent/       # Dzień 1, ćwiczenie D1.1
├── d1_02_custom_tools/
├── ...
├── d2_06b_e2e_tester/       # Dzień 2, ćwiczenie D2.6
└── prezentacja_v2/          # Prowadzenie i skrypt budujący deck
```

## ⚠️ Bezpieczeństwo

**NIGDY NIE COMMITUJ:**
- ❌ `.env` - zawiera ID projektu i credentials
- ❌ `*-key.json` - service account keys
- ❌ `token.json` - OAuth tokens
- ❌ `credentials.json` - OAuth credentials
- ❌ `*.db` - bazy danych z danymi testowymi

Wszystkie te pliki są w `.gitignore`!

## 🆘 Troubleshooting

### "Permission denied" / brak dostępu do Vertex AI

```bash
# Upewnij się że jesteś zalogowany do GCP
gcloud auth application-default login
```

### "Module not found: google.adk"

```bash
# Zainstaluj ADK
pip install google-adk
```

### "GOOGLE_CLOUD_PROJECT not set"

```bash
# Skopiuj .env.example jako .env i wypełnij wartości
cp .env.example .env
# Edytuj .env
```

### Gmail OAuth nie działa

- Sprawdź czy masz poprawny Client ID i Secret w `.env`
- Sprawdź czy jesteś dodany jako test user w OAuth consent screen
- Usuń stary `token.json` i zaloguj się ponownie

## 📞 Kontakt

Jeśli masz pytania lub problemy, skontaktuj się ze mną!

## 📄 Licencja

Materiały szkoleniowe - użytek wewnętrzny.


# 🏗️ Setup Atlassian Cloud — Instrukcja krok po kroku

Instrukcja przygotowania **darmowego tenanta Atlassian Cloud** (Jira + Confluence)
pod serwer MCP do ćwiczeń szkoleniowych. Jedno konto współdzielone, read-only.

> ⏱️ Czas realizacji: **10–15 minut**

---

## Krok 1 — Załóż darmowe konto Atlassian Cloud

1. Wejdź na **https://www.atlassian.com/try/cloud/signup**
2. Kliknij **„Sign up for free"**
3. Zarejestruj się emailem (np. `trener-mcp@twojadomena.com`) lub kontem Google
4. Wybierz plan **Free** (0 zł, do 10 użytkowników)
5. Nadaj nazwę instancji — np. `mcp-training`
   - Twój URL to: **`https://mcp-training.atlassian.net`**
6. Atlassian utworzy automatycznie Jira + Confluence na tym tenancie

> 💡 Nazwa instancji pojawi się w URLach. Użyj czegoś krótkiego i związanego ze szkoleniem.
---https://adk-training.atlassian.net?continue=https%3A%2F%2Fadk-training.atlassian.net%2Fwelcome%2Fsoftware&atlOrigin=eyJpIjoiNGEyMGNiMDRjMmRjNDA3YzlhNTM4YTk0YjA1NjExYjIiLCJwIjoiaiJ9
---

## Krok 2 — Utwórz projekt Jira

1. Wejdź: **https://mcp-training.atlassian.net/jira**
2. Kliknij **„Projects"** (lewy panel) → **„Create project"**
3. Wybierz typ: **Scrum** lub **Kanban** (dla ćwiczeń obojętne)
4. Podaj:
   - **Name**: `MCP Training`
   - **Key**: `TRAIN` ← ten klucz wpiszesz do `.env` jako `JIRA_DEFAULT_PROJECT_KEY`
5. Kliknij **„Create"**
6. **(Opcjonalnie)** Dodaj 2–3 przykładowe tickety:
   - `TRAIN-1`: „Testowy ticket MCP" — Task
   - `TRAIN-2`: „Przeczytać dokumentację ADK" — Story
   - `TRAIN-3`: „Bug w integracji" — Bug

> 💡 Tickety możesz dodać ręcznie klikając **„+ Create"** w Jira lub zostawić pusty projekt — serwer MCP zadziała i tak.

---

## Krok 3 — Utwórz space Confluence

1. Wejdź: **https://mcp-training.atlassian.net/wiki**
2. Kliknij **„Spaces"** (lewy panel) → **„Create a space"**
3. Wybierz: **Blank space**
4. Podaj:
   - **Space name**: `MCP Training Wiki`
   - **Space key**: `TRAIN` (lub zostaw automatyczny)
5. Kliknij **„Create"**
6. Dodaj 1–2 przykładowe strony:
   - Strona „Witaj w MCP Training" — wpisz dowolny tekst
   - Strona „Architektura projektu" — wklej dowolny opis

> 💡 Space key przyda się do wyszukiwania CQL, np. `space=TRAIN AND type=page`.
#vekivem746@duoley.com
---
<YOUR_ATLASSIAN_API_TOKEN>

https://adk-training.atlassian.net/jira/projects?page=1&sortKey=name&sortOrder=ASC&types=software%2Cbusiness
https://adk-mcp-training.atlassian.net/wiki/spaces/~71202000a0c9bdb44347809e010221df8f489d/pages/622625/Project+Plan+Overview


<YOUR_ATLASSIAN_API_TOKEN>
## Krok 4 — Wygeneruj API Token

1. Wejdź: **https://id.atlassian.com/manage-profile/security/api-tokens**
2. Kliknij **„Create API token"**
3. Podaj etykietę: `mcp-server-training`
4. Kliknij **„Create"**
5. **SKOPIUJ TOKEN** — wyświetli się tylko raz!

> ⚠️ Ten token + Twój email = dane dostępowe do API.  
> Nie commituj ich do repozytorium. Plik `.env` jest w `.gitignore`.

---

## Krok 5 — Uzupełnij plik `.env`

```powershell
# Windows
copy .env.example .env
```

```bash
# Linux/Mac
cp .env.example .env
```

Otwórz `.env` i uzupełnij:

```dotenv
# --- Jira ---
JIRA_BASE_URL=https://mcp-training.atlassian.net/rest/api/2
JIRA_AUTH_TYPE=basic
JIRA_USER_EMAIL=trener-mcp@twojadomena.com
JIRA_API_TOKEN=WKLEJ-SWOJ-TOKEN-TUTAJ

JIRA_DEFAULT_PROJECT_KEY=TRAIN
JIRA_DEFAULT_ISSUE_TYPE=Task
JIRA_DEFAULT_LABEL=mcp-training

# --- Confluence Wiki ---
ENABLE_WIKI_INTEGRATION=true
WIKI_BASE_URL=https://mcp-training.atlassian.net/wiki/rest/api
WIKI_AUTH_TYPE=basic
WIKI_USER_EMAIL=trener-mcp@twojadomena.com
WIKI_API_TOKEN=WKLEJ-SWOJ-TOKEN-TUTAJ
```

> 💡 Dla Atlassian Cloud email i token są takie same dla Jira i Confluence — to jedno konto.

---

## Krok 6 — Zainstaluj zależności

```powershell
cd python-jira-wiki-mcp
pip install -r requirements.txt
```

---

## Krok 7 — Uruchom serwer MCP

Serwer działa w trybie **stdio** — to standardowy transport MCP.
Klient MCP (Claude Desktop, Cursor, etc.) uruchamia serwer jako subprocess.

**Ręczny test (PowerShell):**
```powershell
cd python-jira-wiki-mcp
.\run_mcp_server.ps1
```

**Lub bezpośrednio:**
```bash
python jira_wiki_mcpserver.py
```

---

## Krok 7b — Konfiguracja klienta MCP

Skopiuj `mcp_client_config.json` do konfiguracji swojego klienta MCP.

**Claude Desktop** (`%APPDATA%\Claude\claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "jira-wiki": {
      "command": "python",
      "args": ["jira_wiki_mcpserver.py"],
      "cwd": "C:\\sciezka\\do\\python-jira-wiki-mcp",
      "env": {
        "JIRA_BASE_URL": "https://mcp-training.atlassian.net/rest/api/2",
        "JIRA_AUTH_TYPE": "basic",
        "JIRA_USER_EMAIL": "trener-mcp@twojadomena.com",
        "JIRA_API_TOKEN": "WKLEJ-TOKEN",
        "ENABLE_WIKI_INTEGRATION": "true",
        "WIKI_BASE_URL": "https://mcp-training.atlassian.net/wiki/rest/api",
        "WIKI_AUTH_TYPE": "basic",
        "WIKI_USER_EMAIL": "trener-mcp@twojadomena.com",
        "WIKI_API_TOKEN": "WKLEJ-TOKEN"
      }
    }
  }
}
```

> 💡 Gotowy szablon: `mcp_client_config.json` w katalogu projektu.

---

## Krok 8 — Smoke test

Szybki test czy serwer poprawnie inicjalizuje klienty i narzędzia:

```powershell
cd python-jira-wiki-mcp
python -c "
import os, sys; sys.path.insert(0, '.')
from dotenv import load_dotenv; load_dotenv()
from jira_client import JiraClient
from wiki_client import WikiClient
jira = JiraClient(); print('Jira OK:', jira.base_url)
wiki = WikiClient(); print('Wiki OK:', wiki.base_url)
print('SMOKE TEST PASSED')
"
```

Oczekiwany output:
```
Jira OK: https://mcp-training.atlassian.net/rest/api/2
Wiki OK: https://mcp-training.atlassian.net/wiki/rest/api
SMOKE TEST PASSED
```

---

## 🔧 Troubleshooting

| Problem | Rozwiązanie |
|---------|-------------|
| `ValueError: JIRA_BASE_URL must be set` | Brak pliku `.env` lub puste `JIRA_BASE_URL` |
| `401 Unauthorized` | Błędny email lub API token. Sprawdź `.env` |
| `403 Forbidden` | Konto nie ma dostępu do projektu. Sprawdź uprawnienia w Jira → Project Settings → People |
| `404 Not Found` | Błędny URL. Dla Cloud: `https://INSTANCJA.atlassian.net/rest/api/2` |
| `Wiki integration disabled` | `ENABLE_WIKI_INTEGRATION=true` nie ustawione lub błędne dane Wiki |
| `Connection refused :8080` | Serwer nie uruchomiony lub zablokowany port. Sprawdź firewall |

---

## 👥 Onboarding zespołu (dla prowadzącego)

1. Prowadzący zakłada **jeden tenant** i generuje **jeden API token**
2. Prowadzący udostępnia kursantom:
   - URL instancji (np. `mcp-training.atlassian.net`)
   - Email konta technicznego
   - API token (np. przez secure channel / password manager)
3. Każdy kursant:
   - Kopiuje `.env.example` → `.env`
   - Wkleja dane od prowadzącego
   - Uruchamia `run_mcp_server.ps1` lub `2_run_mcp_server_locally.sh`

---

## 🔒 Bezpieczeństwo

- **Nigdy nie commituj `.env`** — jest w `.gitignore`
- API token daje dostęp z uprawnieniami konta → nadaj konto **read-only** w projekcie
- Aby ograniczyć uprawnienia: Jira → Project Settings → People → dodaj konto jako **Viewer**
- Token możesz w każdej chwili odwołać: https://id.atlassian.com/manage-profile/security/api-tokens




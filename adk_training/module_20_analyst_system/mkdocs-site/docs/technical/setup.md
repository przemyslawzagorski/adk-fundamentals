# Konfiguracja i uruchomienie

## Wymagania

| Wymaganie | Minimum |
|-----------|---------|
| Python | 3.11+ |
| Google API Key | Wymagany (Google AI Studio) |
| Node.js | Opcjonalnie (dla Comarch MCP) |

---

## Szybki start

### 1. Konfiguracja zmiennych środowiskowych

```bash
cd module_20_analyst_system
cp .env.template .env
```

Edytuj `.env`:

```bash
# Wymagane
GOOGLE_API_KEY=your-google-api-key

# Opcjonalne — modele
ADK_MODEL=gemini-2.5-flash          # Domyślny model
ADK_STRONG_MODEL=gemini-2.5-pro     # Dla złożonych zadań

# Opcjonalne — katalogi
OUTPUT_DIR=./output                   # Katalog wyjściowy
SKILLS_DIR=./skills                   # Repozytorium skilli

# Opcjonalne — MCP (integracja z Jira/Wiki/GitLab)
COMARCH_MCP_COMMAND=npx -y @comarch/mcp-server
JIRA_URL=https://jira.comarch/
WIKI_URL=https://wiki.comarch/
GITLAB_URL=https://gitlab.comarch/
NODE_EXTRA_CA_CERTS=/path/to/ca-cert.pem
```

### 2. Instalacja zależności

```bash
pip install -r requirements.txt
```

### 3. Uruchomienie

=== "ADK CLI (terminal)"

    ```bash
    adk run .
    ```

    Interaktywna sesja w terminalu. Wpisuj polecenia w języku naturalnym.

=== "ADK Web UI (przeglądarka)"

    ```bash
    adk web .
    ```

    Interfejs webowy z historią konwersacji i podglądem stanu sesji.

---

## Przykładowe polecenia

Po uruchomieniu systemu możesz korzystać z naturalnego języka:

### Analiza wymagań

```
Przeanalizuj wymaganie: system musi obsługiwać masową aktywację
10 000 kart SIM w jednej partii z powiadomieniem SMS.
```

### Generowanie dokumentacji

```
Wygeneruj High-Level Design dla modułu zarządzania
alertami sieciowymi w projekcie IoT Connect.
```

### Tworzenie epiku

```
Utwórz epik Jira dla implementacji eksportu CDR
do formatu CSV z możliwością filtrowania po dacie.
```

### Recenzja dokumentu

```
Zrecenzuj plik docs/architecture.md pod kątem
zgodności z Diátaxis i naszym style guide'em.
```

### Tworzenie skilla (Knowledge Loop)

```
Utwórz nowy skill dotyczący konwencji nazewnictwa
w naszym API GraphQL na podstawie istniejącego schematu.
```

---

## Weryfikacja instalacji

Uruchom testy E2E aby sprawdzić poprawność konfiguracji:

```bash
python e2e_tests/test_module_20.py
```

Oczekiwany wynik:

```
======================================================================
🧪 E2E Test: Module 20 - Analyst System
======================================================================
[TEST] Test 1: Root agent loads correctly
PASS: root_agent 'analyst_captain' loaded with 6 orchestrators
...
======================================================================
🎉 SUCCESS! All 16 tests passed!
```

---

## Rozwiązywanie problemów

???+ warning "Brak `GOOGLE_API_KEY`"
    Bez klucza API system nie będzie w stanie komunikować się z Gemini. Uzyskaj klucz:

    1. Otwórz [Google AI Studio](https://aistudio.google.com/apikey)
    2. Utwórz projekt (lub wybierz istniejący)
    3. Wygeneruj klucz API
    4. Ustaw w `.env`

???+ warning "MCP nie łączy się"
    Sprawdź:

    - Czy `NODE_EXTRA_CA_CERTS` wskazuje na poprawny certyfikat CA
    - Czy masz dostęp sieciowy do Jira/Wiki/GitLab
    - Czy `npx` jest dostępny w PATH

    MCP jest opcjonalny — system działa bez niego.

???+ warning "Testy nie przechodzą"
    Upewnij się, że:

    - Uruchamiasz testy z katalogu `adk_training/` lub ustawiasz `SKILLS_DIR`
    - Python >= 3.11
    - Zainstalowane zależności: `pip install -r requirements.txt`

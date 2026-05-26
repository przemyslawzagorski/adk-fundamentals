# Moduł 21 — ADK Web Tester 🧪

Agent Computer Use, który automatycznie testuje inne agenty ADK przez interfejs ADK web.

## Jak to działa?

Agent steruje przeglądarką (Playwright) by:
1. Otworzyć ADK web (localhost:8000)
2. Wybrać agenta z dropdown
3. Wysłać prompt testowy
4. Odczytać odpowiedź ze screenshota
5. Ocenić wynik i zapisać raport

## Wymagania

```bash
pip install -r requirements.txt
playwright install chromium
```

## Konfiguracja

Plik `.env` w katalogu modułu:

```env
GOOGLE_CLOUD_PROJECT=adk-training-pz
COMPUTER_USE_MODEL=gemini-2.5-flash-preview-04-17
ADK_WEB_URL=http://localhost:8000
TESTER_PORT=8001
HEADLESS=false
```

## Użycie

### 1. Uruchom ADK web z agentami

```bash
cd adk_training
adk web
# → http://localhost:8000
```

### 2a. Tryb CLI — testuj wybrane moduły

```bash
cd adk_training
python -m module_21_adk_tester.cli --module 01 02 04 12
# lub wszystkie:
python -m module_21_adk_tester.cli --module all
```

### 2b. Tryb interaktywny

```bash
python -m module_21_adk_tester.cli --interactive
```

Komendy w trybie interaktywnym:
- `/modules` — pokaż dostępne moduły
- `/test 01 02` — testuj moduły
- `/test all` — testuj wszystkie
- `/quit` — zakończ

### 2c. Jako agent w ADK web

Agent jest widoczny jako **adk_web_tester** w dropdown (port 8001):

```bash
cd adk_training/module_21_adk_tester
adk web --port 8001
```

## Opcje CLI

| Flaga | Opis |
|-------|------|
| `--module 01 02` | Moduły do testowania |
| `--interactive` | Tryb interaktywny |
| `--headless` | Bez okna przeglądarki |
| `--model MODEL` | Model Gemini |
| `--adk-url URL` | URL ADK web |
| `--verbose` | Debug logging |

## Raporty

Generowane w `~/.adk-tester/reports/`:
- `report_module_01_YYYYMMDD_HHMMSS.md` — Markdown
- `report_module_01_YYYYMMDD_HHMMSS.json` — JSON
- `report_summary_YYYYMMDD_HHMMSS.md` — zbiorczy

## Dostępne scenariusze testowe

| Moduł | Agent | Testy |
|-------|-------|-------|
| 01 Hello World | asystent_podstawowy | 3 (powitanie, pytanie, follow-up) |
| 02 Custom Tool | zarzadca_skarbow | 4 (skarby, count, dodanie, weryfikacja) |
| 04 Sequential | pipeline_z_kwatermistrzem | 2 (rajd, brak danych) |
| 12 Router | captain_with_tools | 4 (nawigator, kwatermistrz, kanonier, kucharz) |

## Architektura

```
module_21_adk_tester/
├── agent.py                  # root_agent + AgentTesterSystem
├── cli.py                    # CLI (argparse)
├── config.py                 # Config dataclass
├── prompts.py                # System prompt QA testera
├── computer/
│   └── playwright_computer.py  # BaseComputer adapter
├── tools/
│   ├── test_scenarios.py     # Scenariusze testowe
│   ├── test_report.py        # Generator raportów
│   └── conversation_store.py # Zapis konwersacji
├── .adk/adk.toml
├── .env
└── requirements.txt
```

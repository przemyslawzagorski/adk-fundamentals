# Quick start

Pełen system w 4 krokach. Wymaga **Python 3.12** (`.venv312`), Node 18+, npm.

!!! warning "Krytyczne"
    Backend **musi** być uruchomiony z `.venv312` — globalny Python 3.12 nie ma zależności
    AuditOps i `app.py` zamilcza ImportError, przez co `/api/audit/*` zwraca 404.
    Zawsze sprawdź `(Get-CimInstance Win32_Process -Filter "ProcessId=<pid>").CommandLine`.

## 1. Instalacja (raz)

```powershell
# venv
py -3.12 -m venv .venv312
& .venv312\Scripts\Activate.ps1
python -m pip install -U pip

# zależności
pip install -r adk_training\module_23_auggie_integration\requirements.txt
pip install -r adk_training\module_24_audit_ops\requirements.txt
pip install mkdocs-material mkdocs-monorepo-plugin
playwright install chromium

# frontend
Push-Location adk_training\module_23_auggie_integration\web\frontend
npm install
Pop-Location
```

## 2. Uruchom wszystko jednym skryptem

```powershell
.\start_all.ps1            # podnosi backend (8770) + frontend (5173) + docs (8765)
.\start_all.ps1 -restart backend
.\start_all.ps1 -restart docs
.\start_all.ps1 -restart all
```

Skrypt otwiera 3 okna PowerShell (każde wypisuje swoje logi) i po 3 s otwiera
[http://localhost:5173](http://localhost:5173).

## 3. Ręczne uruchomienie (gdy coś się sypie)

=== "Backend"

    ```powershell
    & .venv312\Scripts\Activate.ps1
    python -m uvicorn adk_training.module_23_auggie_integration.web.app:app `
        --port 8770 --reload
    ```
    W logu musi być: `AuditOps router mounted at /api/audit`.

=== "Frontend"

    ```powershell
    cd adk_training\module_23_auggie_integration\web\frontend
    npm run dev          # 5173, proxy /api → 127.0.0.1:8770
    ```

=== "Docs (cała platforma)"

    ```powershell
    & .venv312\Scripts\Activate.ps1
    python -m mkdocs serve --dev-addr 127.0.0.1:8765
    ```
    Używa **głównego** `mkdocs.yml` w roocie repo (monorepo plugin scali docs/
    Concierge i AuditOps).

## 4. Smoke test

```powershell
(Invoke-WebRequest http://127.0.0.1:8770/api/health -UseBasicParsing).StatusCode      # 200
(Invoke-WebRequest http://127.0.0.1:8770/api/audit/skills -UseBasicParsing).StatusCode # 200
Start-Process http://localhost:5173
Start-Process http://localhost:8765
```

## Troubleshooting

| Objaw | Przyczyna | Fix |
|---|---|---|
| `/api/audit/*` → 404 | backend uruchomiony globalnym Pythonem | restart z `.venv312` |
| `WinError 10013` na porcie 8001 | Hyper-V exclusion range | użyj 8765 (już ustawione) |
| `playwright._impl._errors.Error: Executable doesn't exist` | brak chromium | `playwright install chromium` |
| port 5173 / 8770 zajęty | stary proces | `.\start_all.ps1 -restart all` (zabija po porcie) |
| `mkdocs: Config value 'plugins': monorepo` nieznane | brak pluginu | `pip install mkdocs-monorepo-plugin` |

## Co dalej

- [Architecture](architecture.md) — co siedzi pod maską.
- [Patterns](patterns/index.md) — jak przenieść skille/wiki do innych modułów.
- [Decision guide](decision-guide.md) — kiedy używać czego.

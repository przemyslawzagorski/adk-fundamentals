# Szybki Start — ADK Fundamentals

## Wymagania wstępne

| Składnik | Wymagana wersja |
|---|---|
| Python | 3.12 |
| Node.js | 18+ |
| `uv` lub `pip` | najnowszy |
| Playwright Chromium | zainstalowany (patrz niżej) |

---

## 1. Instalacja (jednorazowo)

```powershell
# 1. Wirtualne środowisko Python
python -m venv .venv312
.venv312\Scripts\Activate.ps1

# 2. Zależności Python
pip install -r requirements.txt          # lub: uv pip install -r requirements.txt

# 3. Playwright Chromium (wymagany do AuditOps)
.venv312\Scripts\python.exe -m playwright install chromium

# 4. Zależności frontendu
cd adk_training\module_23_auggie_integration\web\frontend
npm install
cd ..\..\..\..\..   # wróć do root repo
```

---

## 2. Uruchomienie wszystkiego (skrypt)

```powershell
.\start_all.ps1
```

Skrypt uruchamia w osobnych oknach:
- **Backend** (FastAPI + AuditOps) → `http://localhost:8770`
- **Frontend** (Vite dev server) → `http://localhost:5173`
- **MkDocs** (dokumentacja) → `http://localhost:8765`

---

## 3. Ręczne uruchamianie

### Backend FastAPI
```powershell
cd C:\Users\NBPZAGORSKI\IdeaProjects\adk-fundamentals
.venv312\Scripts\python.exe -m uvicorn adk_training.module_23_auggie_integration.web.app:app `
    --port 8770 --reload --log-level info
```

### Frontend (Vite dev server)
```powershell
cd adk_training\module_23_auggie_integration\web\frontend
npm run dev
```

### MkDocs (cała platforma — Concierge + AuditOps)
```powershell
cd C:\Users\NBPZAGORSKI\IdeaProjects\adk-fundamentals
.venv312\Scripts\python.exe -m mkdocs serve --dev-addr 127.0.0.1:8765
```
Używa głównego `mkdocs.yml` w roocie repo (monorepo plugin scali docs Concierge i AuditOps).

---

## 4. Weryfikacja działania

```powershell
# Backend health
Invoke-WebRequest http://localhost:8770/api/health -UseBasicParsing | Select-Object StatusCode

# Audit Skills (wymaga AuditOps router)
Invoke-WebRequest http://localhost:8770/api/audit/skills -UseBasicParsing | Select-Object StatusCode

# Frontend
Start-Process "http://localhost:5173"

# Dokumentacja
Start-Process "http://localhost:8765"
```

---

## 5. Playwright — diagnoza

Jeśli w UI widoczny badge **"Playwright missing"**:

```powershell
# Instalacja
.venv312\Scripts\python.exe -m playwright install chromium

# Weryfikacja
.venv312\Scripts\python.exe -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); b=p.chromium.launch(); print('OK', b.version); b.close(); p.stop()"
```

---

## 6. Adresy aplikacji

| Usługa | Adres | Opis |
|---|---|---|
| Frontend (UI) | http://localhost:5173 | React + Vite dev server |
| Backend API | http://localhost:8770 | FastAPI + AuditOps |
| API Docs | http://localhost:8770/docs | Swagger UI |
| Dokumentacja PL/EN | http://localhost:8765 | MkDocs Material |
| Dokumentacja PL | http://localhost:8765/pl/ | Wersja polska |

---

## 7. Rozwiązywanie problemów

| Objaw | Przyczyna | Rozwiązanie |
|---|---|---|
| `404` na `/api/audit/*` | Backend uruchomiony bez venv lub bez restart po zmianach | Restart backendu skryptem `start_all.ps1` lub `.\start_all.ps1 -restart backend` |
| "Playwright missing" | Brak binarek Chromium | `python -m playwright install chromium` |
| `5173` już zajęty | Stary Vite wciąż działa | `npx kill-port 5173` lub zamknij stare okno |
| `8770` już zajęty | Stary backend wciąż działa | `Get-Process python | Stop-Process` (ostrożnie!) |
| MkDocs "unrecognized link" | Link `../` zamiast `../index.md` w pl/index.md | Już naprawione — zignoruj INFO |
| `WinError 10013` przy mkdocs | Port `8001` zarezerwowany przez Windows (Hyper-V exclusion range) | Używaj portu `8765` (już ustawione domyślnie) |
| 404 na `/api/audit/*` mimo restartu | Backend uruchomiony **globalnym** Pythonem zamiast `.venv312` — brak zależności AuditOps powoduje cichy try/except w `app.py` | Zawsze startuj poprzez `.venv312\Scripts\python.exe -m uvicorn ...` lub `start_all.ps1` |

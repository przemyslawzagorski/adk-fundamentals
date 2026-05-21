<#
.SYNOPSIS
    start_all.ps1 — uruchamia wszystkie komponenty ADK Fundamentals

.DESCRIPTION
    Uruchamia w nowych oknach PowerShell:
      - Backend FastAPI (port 8770)
      - Frontend Vite dev server (port 5173)
      - MkDocs Material (port 8001)

.PARAMETER restart
    Opcjonalnie wskaż co chcesz zrestartować: "backend", "frontend", "mkdocs", "all"
    Domyślnie: "all"

.EXAMPLE
    .\start_all.ps1
    .\start_all.ps1 -restart backend
    .\start_all.ps1 -restart mkdocs
#>
param(
    [ValidateSet("backend","frontend","mkdocs","all")]
    [string]$restart = "all"
)

$ROOT = "C:\Users\NBPZAGORSKI\IdeaProjects\adk-fundamentals"
$PYTHON = "$ROOT\.venv312\Scripts\python.exe"

# ─── pomocnicze ───────────────────────────────────────────────────────────────
function Kill-Port([int]$port) {
    $pids = netstat -ano | Select-String ":$port " | ForEach-Object {
        ($_ -split '\s+')[-1]
    } | Sort-Object -Unique
    foreach ($p in $pids) {
        if ($p -match '^\d+$' -and $p -ne '0') {
            Write-Host "  Zatrzymuję PID $p (port $port)..." -ForegroundColor Yellow
            Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
        }
    }
}

function Start-InWindow([string]$title, [string]$cmd) {
    Start-Process powershell -ArgumentList "-NoExit","-Command","cd '$ROOT'; $cmd" `
        -WindowStyle Normal
    Write-Host "  ✓ $title uruchomiony" -ForegroundColor Green
}

# ─── backend ──────────────────────────────────────────────────────────────────
if ($restart -in @("all","backend")) {
    Write-Host "`n[1/3] Backend FastAPI (port 8770)" -ForegroundColor Cyan
    Kill-Port 8770
    Start-Sleep -Milliseconds 800
    Start-InWindow "Backend" @"
Write-Host 'Backend FastAPI + AuditOps' -ForegroundColor Cyan
& '$PYTHON' -m uvicorn adk_training.module_23_auggie_integration.web.app:app --port 8770 --reload --log-level info
"@
}

# ─── frontend ─────────────────────────────────────────────────────────────────
if ($restart -in @("all","frontend")) {
    Write-Host "`n[2/3] Frontend Vite (port 5173)" -ForegroundColor Cyan
    Kill-Port 5173
    Start-Sleep -Milliseconds 500
    Start-InWindow "Frontend" @"
Write-Host 'Frontend Vite dev server' -ForegroundColor Cyan
cd '$ROOT\adk_training\module_23_auggie_integration\web\frontend'
npm run dev
"@
}

# ─── mkdocs ───────────────────────────────────────────────────────────────────
if ($restart -in @("all","mkdocs")) {
    Write-Host "`n[3/3] MkDocs Material (port 8765)" -ForegroundColor Cyan
    Kill-Port 8765
    Kill-Port 8000   # stary mkdocs mógł być na 8000
    Start-Sleep -Milliseconds 500
    Start-InWindow "MkDocs" @"
Write-Host 'MkDocs Material — Platform docs (Concierge + AuditOps)' -ForegroundColor Cyan
& '$PYTHON' -m mkdocs serve --dev-addr 127.0.0.1:8765
"@
}

Write-Host @"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ADK Fundamentals — uruchomione!

  Frontend:  http://localhost:5173
  Backend:   http://localhost:8770
  API Docs:  http://localhost:8770/docs
  MkDocs:    http://localhost:8765
  MkDocs PL: http://localhost:8765/pl/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"@ -ForegroundColor Green

# Opcjonalne: otwórz w przeglądarce po chwili
Start-Sleep -Seconds 3
Start-Process "http://localhost:5173"

# ============================================================
#  restart_all.ps1 — JEDEN skrypt: ubij wszystko + odpal od nowa
#
#  Co robi:
#    1. Kill: MCP (node), backend (8766), frontend (5173), Playwright
#    2. Start MCP (background, minimized window)
#    3. Wait for MCP ready
#    4. Start frontend (osobne okno, nie blokuje)
#    5. Start backend (TEN terminal — tu widzisz logi pipeline)
#
#  Uzycie:  .\restart_all.ps1
# ============================================================

$ErrorActionPreference = "Stop"
$scriptDir  = $PSScriptRoot
$repoRoot   = Resolve-Path (Join-Path $scriptDir "..\..\..")

# --- 1. KILL ALL ------------------------------------------------
Write-Host ""
Write-Host "==============================" -ForegroundColor Red
Write-Host "  PHASE 1: KILL ALL"           -ForegroundColor Red
Write-Host "==============================" -ForegroundColor Red

# Kill by process name (MCP node, Playwright chromium)
Get-Process node, chrome -ErrorAction SilentlyContinue | Where-Object {
    $cmd = (Get-CimInstance Win32_Process -Filter "ProcessId=$($_.Id)" -ErrorAction SilentlyContinue).CommandLine
    $cmd -match 'comarch-mcp|playwright_chromiumdev'
} | ForEach-Object {
    Write-Host "  killing $($_.ProcessName) PID=$($_.Id)" -ForegroundColor DarkGray
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
}

# Kill by port
foreach ($port in 3001, 8766, 5173, 5174) {
    $conns = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    foreach ($c in $conns) {
        $p = Get-Process -Id $c.OwningProcess -ErrorAction SilentlyContinue
        if ($p) {
            Write-Host "  port $port -> killing $($p.ProcessName) PID=$($p.Id)" -ForegroundColor DarkGray
            Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
        }
    }
}

Start-Sleep -Milliseconds 800

# Verify
$allClear = $true
foreach ($port in 3001, 8766, 5173) {
    $c = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($c) {
        Write-Host "  WARNING: port $port still in use (PID=$($c.OwningProcess))" -ForegroundColor Red
        $allClear = $false
    }
}
if ($allClear) { Write-Host "  All ports free." -ForegroundColor Green }

# --- 2. ACTIVATE VENV --------------------------------------------
Set-Location $repoRoot
$venvActivate = Join-Path $repoRoot ".venv312\Scripts\Activate.ps1"
if (-not (Test-Path $venvActivate)) {
    Write-Host "[ERROR] Brak venva: $venvActivate" -ForegroundColor Red
    exit 1
}
. $venvActivate

# --- 3. START MCP (background) -----------------------------------
Write-Host ""
Write-Host "==============================" -ForegroundColor Cyan
Write-Host "  PHASE 2: START MCP"          -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan

$mcpScript = Join-Path (Join-Path $scriptDir "..") "start_mcp.ps1"
$mcpProc = Start-Process -FilePath powershell -ArgumentList @(
    "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Resolve-Path $mcpScript)
) -PassThru -WindowStyle Minimized

Write-Host "  MCP starting (PID: $($mcpProc.Id))..." -ForegroundColor Yellow

# Wait for MCP to be ready (any HTTP response = alive)
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Seconds 1
    try {
        $null = Invoke-WebRequest -Uri "http://127.0.0.1:3001/mcp" -Method POST `
            -Body '{"jsonrpc":"2.0","method":"ping","id":0}' `
            -ContentType "application/json" -TimeoutSec 2 -ErrorAction Stop
        $ready = $true; break
    } catch {
        # 406 etc. -- httpx throws on non-2xx, but server IS listening
        if ($_.Exception.Response) { $ready = $true; break }
    }
}
if ($ready) {
    Write-Host "  MCP ready at http://127.0.0.1:3001/mcp" -ForegroundColor Green
} else {
    Write-Host "  WARNING: MCP not ready after 30s -- backend has auto-restart fallback" -ForegroundColor Red
}

# --- 4. START FRONTEND (osobne okno) -----------------------------
Write-Host ""
Write-Host "==============================" -ForegroundColor Cyan
Write-Host "  PHASE 3: START FRONTEND"     -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan

$frontendDir = Resolve-Path (Join-Path (Join-Path $scriptDir "..") "web\frontend")
Start-Process -FilePath powershell -ArgumentList @(
    "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
    "Set-Location '$frontendDir'; npm run dev"
) -WindowStyle Normal

Write-Host "  Frontend starting at http://localhost:5173" -ForegroundColor Green

# --- 5. START BACKEND (ten terminal) -----------------------------
Write-Host ""
Write-Host "==============================" -ForegroundColor Cyan
Write-Host "  PHASE 4: START BACKEND"      -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host "  URL:  http://127.0.0.1:8766" -ForegroundColor Green
Write-Host "  MCP:  http://127.0.0.1:3001" -ForegroundColor Green
Write-Host "  UI:   http://localhost:5173"  -ForegroundColor Green
Write-Host ""
Write-Host "  Logi pipeline ida tutaj. Ctrl+C aby zatrzymac." -ForegroundColor Gray
Write-Host ""

$env:PYTHONIOENCODING = "utf-8"
$env:SPEC_GEN_LOG_LEVEL = "INFO"

python -m uvicorn adk_training.module_22_spec_generator.web.app:app `
    --host 127.0.0.1 --port 8766 --log-level info

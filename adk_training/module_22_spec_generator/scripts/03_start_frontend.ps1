# ============================================================
#  03_start_frontend.ps1 - Vite + React (port 5173)
#  ZAGI Studio UI (ten "netflix-style" web).
# ============================================================

$ErrorActionPreference = "Stop"
$frontend = Resolve-Path (Join-Path $PSScriptRoot "..\web\frontend")
Set-Location $frontend

if (-not (Test-Path "node_modules")) {
    Write-Host "[INFO] node_modules brak, instaluje (npm install)..." -ForegroundColor Yellow
    npm install
}

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Frontend ZAGI Studio (Vite)"             -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  URL: http://localhost:5173"              -ForegroundColor Green
Write-Host ""

npm run dev

# Concierge Web — Windows launcher
# Uruchamia backend + (opcjonalnie) otwiera przeglądarkę.
#
# Użycie: .\start.ps1                # backend only (frontend dev start manualnie)
#         .\start.ps1 -BuildFrontend # build frontend + serwuj statycznie z FastAPI
#         .\start.ps1 -OpenBrowser

[CmdletBinding()]
param(
  [int]$Port = 8770,
  [switch]$BuildFrontend,
  [switch]$OpenBrowser,
  [switch]$UseCli = $true   # Windows-friendly default
)

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $here "..\..\..")

Write-Host "==> Concierge Web launcher" -ForegroundColor Cyan
Write-Host "    Repo:    $repoRoot"
Write-Host "    Port:    $Port"
Write-Host "    UseCLI:  $UseCli"

# 1. Frontend build (jeśli zażądane)
if ($BuildFrontend) {
  Write-Host "==> Building frontend..." -ForegroundColor Cyan
  Push-Location (Join-Path $here "frontend")
  if (-not (Test-Path "node_modules")) {
    Write-Host "    npm install (first time)..."
    npm install
  }
  npm run build
  Pop-Location
}

# 2. Env
$env:CONCIERGE_PORT = "$Port"
if ($UseCli) { $env:AUGGIE_USE_CLI = "1" }

# 3. Open browser (after a moment)
if ($OpenBrowser) {
  Start-Job -ScriptBlock {
    Start-Sleep -Seconds 2
    Start-Process "http://127.0.0.1:$using:Port"
  } | Out-Null
}

# 4. Run backend
Push-Location $repoRoot
try {
  Write-Host "==> Starting FastAPI on http://127.0.0.1:$Port" -ForegroundColor Green
  python -m adk_training.module_23_auggie_integration.web.app
} finally {
  Pop-Location
}

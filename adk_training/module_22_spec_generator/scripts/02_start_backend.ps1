# ============================================================
#  02_start_backend.ps1 - Backend FastAPI/uvicorn (port 8766)
#  Logi spec_generator.* (m.in. [NotebookLM] QUESTION / RAW ANSWER)
#  ida do TEGO terminala. Tu sledzisz pipeline.
#  MCP jest auto-restartowane (stateful = 1 sesja na proces node).
# ============================================================

$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..\..")
Set-Location $repoRoot

$venvActivate = Join-Path $repoRoot ".venv312\Scripts\Activate.ps1"
if (-not (Test-Path $venvActivate)) {
    Write-Host "[ERROR] Brak venva: $venvActivate" -ForegroundColor Red
    exit 1
}
. $venvActivate

$env:PYTHONIOENCODING = "utf-8"
$env:SPEC_GEN_LOG_LEVEL = "INFO"   # zeby [NotebookLM] QUESTION/RAW ANSWER bylo widoczne

# --- Kill stale MCP (stateful = 1 initialize na proces node) ---
Write-Host "[pre-flight] Killing stale MCP on port 3001..." -ForegroundColor Yellow
$listeners = Get-NetTCPConnection -LocalPort 3001 -State Listen -ErrorAction SilentlyContinue
if ($listeners) {
    $listeners | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
    Write-Host "[pre-flight] Old MCP killed (PIDs: $($listeners.OwningProcess -join ', '))" -ForegroundColor Yellow
    Start-Sleep -Seconds 2
} else {
    Write-Host "[pre-flight] No stale MCP found." -ForegroundColor Gray
}

# --- Start fresh MCP in background ---
Write-Host "[pre-flight] Starting fresh MCP server..." -ForegroundColor Yellow
$mcpScript = Join-Path $PSScriptRoot ".." "start_mcp.ps1"
$mcpProc = Start-Process -FilePath powershell -ArgumentList @(
    "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $mcpScript
) -PassThru -WindowStyle Minimized

# Wait for MCP to be ready
$ready = $false
for ($i = 0; $i -lt 20; $i++) {
    Start-Sleep -Seconds 1
    try {
        $r = Invoke-WebRequest -Uri "http://127.0.0.1:3001/mcp" -Method POST `
            -Body '{"jsonrpc":"2.0","method":"ping","id":0}' `
            -ContentType "application/json" -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($r.StatusCode -in 200, 202, 400, 405) {
            $ready = $true
            break
        }
    } catch { }
}
if ($ready) {
    Write-Host "[pre-flight] MCP ready (PID: $($mcpProc.Id))" -ForegroundColor Green
} else {
    Write-Host "[pre-flight] WARNING: MCP not ready after 20s — backend will retry" -ForegroundColor Red
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Backend Spec Generator (uvicorn)"        -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  URL:  http://127.0.0.1:8766"             -ForegroundColor Green
Write-Host "  MCP:  http://127.0.0.1:3001/mcp"         -ForegroundColor Green
Write-Host "  Logi: spec_generator.* + uvicorn.*"      -ForegroundColor Gray
Write-Host ""

python -m uvicorn adk_training.module_22_spec_generator.web.app:app `
    --host 127.0.0.1 --port 8766 --log-level info

# ============================================================
#  04_export_cookies.ps1 - re-eksport ciastek NotebookLM
#  Uzywa istniejacego adk_training\notebooklm_agent\export_via_devtools.py.
#  WAZNE: zamknij wszystkie okna Chrome PRZED uruchomieniem.
#  Po sukcesie zrestartuj backend (02_start_backend.ps1), bo cookies
#  ladowane sa raz przy starcie singletona NotebookLM.
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

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Re-eksport cookies NotebookLM"           -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Out: $env:USERPROFILE\.notebooklm-agent\cookies.json" -ForegroundColor Gray
Write-Host ""
Write-Host "  Upewnij sie, ze WSZYSTKIE okna Chrome sa zamkniete."  -ForegroundColor Yellow
Write-Host "  Skrypt poprowadzi Cie przez kroki w DevTools."        -ForegroundColor Yellow
Write-Host ""

python adk_training\notebooklm_agent\export_via_devtools.py

Write-Host ""
Write-Host "[NEXT] zrestartuj backend (02_start_backend.ps1) zeby singleton wczytal nowe ciastka." -ForegroundColor Green

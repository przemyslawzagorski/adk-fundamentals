# ============================================================
#  00_kill_all.ps1 - twardy reset calego stacku Spec Generator
#  Ubija: MCP (node), Playwright chromium, backend uvicorn (port 8766),
#         Vite dev server (port 5173).
#  NIE rusza zwyklego Chrome z Twoim profilem.
# ============================================================

$ErrorActionPreference = "SilentlyContinue"

Write-Host "=== KILL: MCP (node) + Playwright chromium ===" -ForegroundColor Yellow
Get-Process node, chrome -ErrorAction SilentlyContinue | Where-Object {
    $cmd = (Get-CimInstance Win32_Process -Filter "ProcessId=$($_.Id)" -ErrorAction SilentlyContinue).CommandLine
    $cmd -match 'comarch-mcp|playwright_chromiumdev'
} | ForEach-Object {
    Write-Host "  killing $($_.ProcessName) PID=$($_.Id)" -ForegroundColor DarkGray
    Stop-Process -Id $_.Id -Force
}

Write-Host ""
Write-Host "=== KILL: porty 3001 / 8766 / 5173 ===" -ForegroundColor Yellow
foreach ($port in 3001, 8766, 5173) {
    $conns = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    foreach ($c in $conns) {
        $p = Get-Process -Id $c.OwningProcess -ErrorAction SilentlyContinue
        if ($p) {
            Write-Host "  port $port -> killing $($p.ProcessName) PID=$($p.Id)" -ForegroundColor DarkGray
            Stop-Process -Id $p.Id -Force
        }
    }
}

Start-Sleep -Milliseconds 500

Write-Host ""
Write-Host "=== STATUS portow po kill ===" -ForegroundColor Cyan
foreach ($port in 3001, 8766, 5173) {
    $c = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($c) {
        Write-Host ("  {0} STILL LISTENING PID={1}" -f $port, $c.OwningProcess) -ForegroundColor Red
    } else {
        Write-Host ("  {0} wolny" -f $port) -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Gotowe. Mozesz teraz odpalac 01_start_mcp / 02_start_backend / 03_start_frontend." -ForegroundColor Green

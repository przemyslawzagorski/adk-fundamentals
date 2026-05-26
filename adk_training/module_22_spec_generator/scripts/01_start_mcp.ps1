# ============================================================
#  01_start_mcp.ps1 - MCP Comarch (port 3001)
#  Wrapper na istniejacy ..\start_mcp.ps1 (zachowuje cala konfiguracje
#  env + nexus + CA cert). Ten skrypt MUSI lecec w wlasnym terminalu
#  i zyc razem z backendem (stateful: 1 init na proces).
# ============================================================

$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..")
& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $root "start_mcp.ps1")

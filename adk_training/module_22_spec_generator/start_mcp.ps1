# ============================================================
#  Comarch MCP Server (streamable-http) — dla Spec Generator
#  Uruchom w OSOBNYM terminalu PRZED `uvicorn ... web.app:app`
#  Sluchapy na http://127.0.0.1:3001/mcp
# ============================================================

$ErrorActionPreference = "Stop"

# Wczytaj zmienne z adk_training/.env (jira/wiki/gitlab tokens + CA cert)
$envFile = Resolve-Path (Join-Path $PSScriptRoot "..\.env")
if (-not (Test-Path $envFile)) {
    Write-Host "[ERROR] Brak adk_training\.env" -ForegroundColor Red
    exit 1
}

Get-Content $envFile | ForEach-Object {
    if ($_ -match '^\s*([^#=][^=]*)=(.*)$') {
        $key = $matches[1].Trim()
        $val = $matches[2].Trim().Trim('"')
        [System.Environment]::SetEnvironmentVariable($key, $val, "Process")
    }
}

$required = @("JIRA_BASE_URL", "JIRA_BEARER_TOKEN")
$missing = $required | Where-Object { -not [System.Environment]::GetEnvironmentVariable($_, "Process") }
if ($missing) {
    Write-Host "[ERROR] Brakuje w .env: $($missing -join ', ')" -ForegroundColor Red
    exit 1
}

# MCP server config
$env:MCP_MODE         = "streamable-http"
$env:MCP_SESSION_MODE = "stateful"   # KRYTYCZNE: stateless w tym buildzie comarch MCP jest zepsute (single-use transport globalnie). Stateful = JEDEN initialize na proces -> ZAWSZE restart MCP razem z backendem.
$env:MCP_AUTH_MODE    = "none"
$env:HTTP_PORT        = "3001"
$env:HTTP_HOST        = "127.0.0.1"
$env:LOG_LEVEL        = "info"
$env:READ_ONLY_MODE   = "true"

# SSL bypass dla self-signed Comarch
$env:NODE_TLS_REJECT_UNAUTHORIZED = "0"
$env:HTTP_REJECT_UNAUTHORIZED     = "false"

if (-not $env:NODE_EXTRA_CA_CERTS) {
    $defaultCert = "$env:USERPROFILE\Documents\cert\GK_COMARCH_ROOT_CA.crt"
    if (Test-Path $defaultCert) { $env:NODE_EXTRA_CA_CERTS = $defaultCert }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Comarch MCP \u2014 streamable-http"           -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  URL:     http://127.0.0.1:3001/mcp"        -ForegroundColor Green
Write-Host "  Jira:    $env:JIRA_BASE_URL"               -ForegroundColor Gray
Write-Host "  Wiki:    $env:WIKI_BASE_URL"               -ForegroundColor Gray
Write-Host "  GitLab:  $env:GITLAB_BASE_URL"             -ForegroundColor Gray
Write-Host "  CA cert: $env:NODE_EXTRA_CA_CERTS"         -ForegroundColor Gray
Write-Host ""

$NEXUS = "https://nexus.czk.comarch/repository/ai-npm"
& "C:\Program Files\nodejs\npx.cmd" --yes --registry $NEXUS "@comarch/mcp-integration-tool"

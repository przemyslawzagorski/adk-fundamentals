# ============================================================
# Start Comarch MCP Server — streamable-http mode
# Uruchom w OSOBNYM terminalu PRZED `adk web`
# ============================================================

$envFile = Join-Path $PSScriptRoot ".env"
if (-not (Test-Path $envFile)) {
    Write-Host "[ERROR] Brak pliku .env!" -ForegroundColor Red
    Write-Host "  Skopiuj .env.example i uzupelnij tokeny." -ForegroundColor Yellow
    exit 1
}

# Wczytaj .env
Get-Content $envFile | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
        $key = $matches[1].Trim()
        $val = $matches[2].Trim()
        [System.Environment]::SetEnvironmentVariable($key, $val, "Process")
    }
}

# Walidacja wymaganych zmiennych
$required = @("JIRA_BASE_URL", "JIRA_BEARER_TOKEN", "WIKI_BASE_URL", "WIKI_BEARER_TOKEN")
$missing = $required | Where-Object { -not [System.Environment]::GetEnvironmentVariable($_, "Process") }
if ($missing) {
    Write-Host "[ERROR] Brakuje zmiennych w .env:" -ForegroundColor Red
    $missing | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
    exit 1
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Comarch MCP Server — streamable-http"   -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  URL:      http://localhost:3000/mcp"     -ForegroundColor Green
Write-Host "  Jira:     $env:JIRA_BASE_URL"            -ForegroundColor Gray
Write-Host "  Wiki:     $env:WIKI_BASE_URL"            -ForegroundColor Gray
Write-Host ""
Write-Host "  Ctrl+C aby zatrzymac serwer"             -ForegroundColor Yellow
Write-Host ""

$env:MCP_MODE       = "streamable-http"
$env:MCP_AUTH_MODE  = "none"
$env:HTTP_PORT      = "3000"
$env:HTTP_HOST      = "127.0.0.1"
$env:LOG_LEVEL      = "info"
$env:READ_ONLY_MODE = "true"   # bezpieczny tryb — tylko odczyt

# SSL — Comarch uzywa self-signed certs, Node.js musi miec bypass
# Tak samo jak w konfiguracji Augment (stdio mode)
$env:NODE_TLS_REJECT_UNAUTHORIZED = "0"
$env:HTTP_REJECT_UNAUTHORIZED     = "false"

# Opcjonalnie: sciezka do CA certa (z .env lub domyslna)
$caCert = [System.Environment]::GetEnvironmentVariable("NODE_EXTRA_CA_CERTS", "Process")
if (-not $caCert) {
    $defaultCert = "$env:USERPROFILE\Documents\cert\GK_COMARCH_ROOT_CA.crt"
    if (Test-Path $defaultCert) {
        $env:NODE_EXTRA_CA_CERTS = $defaultCert
        Write-Host "  SSL CA:   $defaultCert" -ForegroundColor Gray
    }
} else {
    Write-Host "  SSL CA:   $caCert" -ForegroundColor Gray
}

$NEXUS = "https://nexus.czk.comarch/repository/ai-npm"

npx --registry $NEXUS @comarch/mcp-integration-tool


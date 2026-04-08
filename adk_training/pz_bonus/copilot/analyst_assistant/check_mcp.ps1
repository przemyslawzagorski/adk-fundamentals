# ============================================================
# Diagnostics - sprawdza czy MCP + Jira/Wiki dzialaja
# Uruchom z katalogu analyst_assistant: .\check_mcp.ps1
# ============================================================

$envFile = Join-Path $PSScriptRoot ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
            [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), "Process")
        }
    }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Analyst Assistant - MCP Diagnostics"      -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 1. Env vars
Write-Host "[1/4] Zmienne srodowiskowe:" -ForegroundColor Yellow

function Show-Var($name, $value) {
    if ($value) {
        Write-Host "  [OK] $name = $value" -ForegroundColor Green
    } else {
        Write-Host "  [BRAK] $name = NOT SET" -ForegroundColor Red
    }
}

$jiraTokenMasked  = if ($env:JIRA_BEARER_TOKEN)  { "***" + $env:JIRA_BEARER_TOKEN.Substring([Math]::Max(0,$env:JIRA_BEARER_TOKEN.Length-6))  } else { $null }
$wikiTokenMasked  = if ($env:WIKI_BEARER_TOKEN)  { "***" + $env:WIKI_BEARER_TOKEN.Substring([Math]::Max(0,$env:WIKI_BEARER_TOKEN.Length-6))  } else { $null }
$googleKeyMasked  = if ($env:GOOGLE_API_KEY)     { "SET (***)" } else { $null }
$mcpUrlDisplay    = if ($env:MCP_SERVER_URL)     { $env:MCP_SERVER_URL } else { "http://localhost:3000 (default)" }

Show-Var "JIRA_BASE_URL"     $env:JIRA_BASE_URL
Show-Var "JIRA_BEARER_TOKEN" $jiraTokenMasked
Show-Var "WIKI_BASE_URL"     $env:WIKI_BASE_URL
Show-Var "WIKI_BEARER_TOKEN" $wikiTokenMasked
Show-Var "GOOGLE_API_KEY"    $googleKeyMasked
Show-Var "MCP_SERVER_URL"    $mcpUrlDisplay

# 2. MCP server
Write-Host ""
Write-Host "[2/4] MCP Server (localhost:3000):" -ForegroundColor Yellow
$mcpUp = $false
try {
    $r = Invoke-WebRequest -Uri "http://localhost:3000/" -TimeoutSec 5 -ErrorAction Stop
    $mcpUp = $true
} catch {
    $status = $_.Exception.Response.StatusCode.value__
    if ($status -gt 0) { $mcpUp = $true } else { $mcpUp = $false }
}
if ($mcpUp) {
    Write-Host "  [OK] MCP server odpowiada na localhost:3000" -ForegroundColor Green
} else {
    Write-Host "  [BLAD] MCP server NIE odpowiada - uruchom start_mcp.ps1!" -ForegroundColor Red
}

# 3. Jira REST API
# JIRA_BASE_URL already contains the API path (e.g. https://host/jira/rest/api/2)
# so we just append /myself
Write-Host ""
Write-Host "[3/4] Jira REST API:" -ForegroundColor Yellow
if ($env:JIRA_BASE_URL -and $env:JIRA_BEARER_TOKEN) {
    $jiraUri = "$($env:JIRA_BASE_URL.TrimEnd('/'))/myself"
    Write-Host "       URL: $jiraUri" -ForegroundColor Gray
    $jiraHeaders = @{ Authorization = "Bearer $($env:JIRA_BEARER_TOKEN)" }
    try {
        $resp = Invoke-RestMethod -Uri $jiraUri -Headers $jiraHeaders -TimeoutSec 10 -ErrorAction Stop
        Write-Host "  [OK] Jira auth OK - zalogowany jako: $($resp.displayName) ($($resp.emailAddress))" -ForegroundColor Green
    } catch {
        $code = $_.Exception.Response.StatusCode.value__
        Write-Host "  [BLAD] Jira auth BLAD (HTTP $code)" -ForegroundColor Red
        if ($code -eq 401) { Write-Host "         Token wygas lub niepoprawny. Wygeneruj nowy: Jira > Profile > Personal Access Tokens" -ForegroundColor Yellow }
        if ($code -eq 403) { Write-Host "         Brak uprawnien. Sprawdz scope tokenu." -ForegroundColor Yellow }
        if ($code -eq 404) { Write-Host "         404 - zly URL. Sprawdz JIRA_BASE_URL w .env (powinno konczyc sie /rest/api/2)" -ForegroundColor Yellow }
    }
} else {
    Write-Host "  [POMIN] JIRA_BASE_URL lub JIRA_BEARER_TOKEN nie ustawione w .env" -ForegroundColor Yellow
}

# 4. Wiki REST API
# WIKI_BASE_URL already contains the API path (e.g. https://host/rest/api)
# so we just append /user/current
Write-Host ""
Write-Host "[4/4] Wiki (Confluence) REST API:" -ForegroundColor Yellow
if ($env:WIKI_BASE_URL -and $env:WIKI_BEARER_TOKEN) {
    $wikiUri = "$($env:WIKI_BASE_URL.TrimEnd('/'))/user/current"
    Write-Host "       URL: $wikiUri" -ForegroundColor Gray
    $wikiHeaders = @{ Authorization = "Bearer $($env:WIKI_BEARER_TOKEN)" }
    try {
        $resp = Invoke-RestMethod -Uri $wikiUri -Headers $wikiHeaders -TimeoutSec 10 -ErrorAction Stop
        Write-Host "  [OK] Wiki auth OK - zalogowany jako: $($resp.displayName)" -ForegroundColor Green
    } catch {
        $code = $_.Exception.Response.StatusCode.value__
        Write-Host "  [BLAD] Wiki auth BLAD (HTTP $code)" -ForegroundColor Red
        if ($code -eq 401) { Write-Host "         Token wygas lub niepoprawny. Wygeneruj nowy: Confluence > Profile > Personal Access Tokens" -ForegroundColor Yellow }
        if ($code -eq 404) { Write-Host "         404 - zly URL. Sprawdz WIKI_BASE_URL w .env (powinno konczyc sie /rest/api)" -ForegroundColor Yellow }
    }
} else {
    Write-Host "  [POMIN] WIKI_BASE_URL lub WIKI_BEARER_TOKEN nie ustawione w .env" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Diagnostics zakonczone" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""


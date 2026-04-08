# Run Jira/Wiki MCP Server Locally (Windows PowerShell)
# Transport: stdio (standard for MCP clients)
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " Jira/Wiki MCP Server (stdio)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
$envFile = Join-Path $PSScriptRoot ".env"
if (-not (Test-Path $envFile)) {
    Write-Host "[ERROR] Brak pliku .env!" -ForegroundColor Red
    Write-Host "  copy .env.example .env" -ForegroundColor Yellow
    Write-Host "Instrukcja: SETUP_ATLASSIAN.md" -ForegroundColor Yellow
    exit 1
}
Write-Host "Starting MCP server (stdio transport)..." -ForegroundColor Green
Write-Host "Uzyj tego w konfiguracji klienta MCP (Claude Desktop, Cursor, etc.):" -ForegroundColor Yellow
Write-Host ""
Write-Host "  command: python" -ForegroundColor White
Write-Host "  args: [""jira_wiki_mcpserver.py""]" -ForegroundColor White
Write-Host "  cwd: $PSScriptRoot" -ForegroundColor White
Write-Host ""
Set-Location $PSScriptRoot
python jira_wiki_mcpserver.py

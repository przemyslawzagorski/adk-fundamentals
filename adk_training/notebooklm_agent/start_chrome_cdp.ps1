# start_chrome_cdp.ps1 — Uruchamia Chrome z CDP dla agenta NotebookLM
# Użycie: .\notebooklm_agent\start_chrome_cdp.ps1

$Port = 9222
$ChromePaths = @(
    "C:\Program Files\Google\Chrome\Application\chrome.exe",
    "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
)

$Chrome = $ChromePaths | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $Chrome) {
    Write-Error "Nie znaleziono Chrome. Zainstaluj Google Chrome."
    exit 1
}

# Sprawdź czy CDP już działa
try {
    $response = Invoke-WebRequest -Uri "http://localhost:$Port/json/version" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✅ Chrome CDP już działa na porcie $Port" -ForegroundColor Green
    Write-Host "   Możesz uruchomić agenta: adk web notebooklm_agent" -ForegroundColor Cyan
    exit 0
} catch {
    # CDP nie działa — uruchom Chrome
}

$ProfileDir = if ($env:CHROME_PROFILE_SUBDIR) { $env:CHROME_PROFILE_SUBDIR } else { "Default" }

Write-Host "🚀 Uruchamiam Chrome z CDP na porcie $Port..." -ForegroundColor Yellow
Write-Host "   Profil: $ProfileDir" -ForegroundColor Gray
Write-Host "   $Chrome" -ForegroundColor Gray

Start-Process -FilePath $Chrome -ArgumentList @(
    "--remote-debugging-port=$Port",
    "--profile-directory=$ProfileDir",
    "--no-first-run",
    "--no-default-browser-check"
)

# Poczekaj aż CDP będzie dostępne
Write-Host "⏳ Czekam aż Chrome się uruchomi..." -ForegroundColor Yellow
$timeout = 30
for ($i = 0; $i -lt $timeout; $i++) {
    Start-Sleep -Seconds 1
    try {
        Invoke-WebRequest -Uri "http://localhost:$Port/json/version" -TimeoutSec 1 -ErrorAction Stop | Out-Null
        Write-Host "✅ Chrome CDP gotowy na http://localhost:$Port" -ForegroundColor Green
        Write-Host ""
        Write-Host "   Teraz uruchom agenta:" -ForegroundColor Cyan
        Write-Host "   adk web notebooklm_agent" -ForegroundColor White
        exit 0
    } catch { }
}

Write-Error "❌ Chrome CDP nie odpowiada po ${timeout}s. Sprawdź czy Chrome wystartował."
exit 1

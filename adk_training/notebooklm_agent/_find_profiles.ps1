$udPath = Join-Path $env:LOCALAPPDATA "Google\Chrome\User Data"
Get-ChildItem $udPath -Directory | Where-Object { $_.Name -match "^(Default|Profile)" } | ForEach-Object {
    $prefsFile = Join-Path $_.FullName "Preferences"
    if (Test-Path $prefsFile) {
        $json = Get-Content $prefsFile -Raw | ConvertFrom-Json -ErrorAction SilentlyContinue
        $name = $json.profile.name
        $email = if ($json.account_info) { $json.account_info[0].email } else { "brak konta" }
        Write-Host "$($_.Name): [$name] $email"
    }
}

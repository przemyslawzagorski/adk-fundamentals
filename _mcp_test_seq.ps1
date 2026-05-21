$ErrorActionPreference = 'Continue'
$url = 'http://127.0.0.1:3001/mcp'
$headers = @{ 'Accept' = 'application/json, text/event-stream'; 'Content-Type' = 'application/json' }

function Send-Mcp($body, $label) {
    Write-Host ""
    Write-Host "=== $label ===" -ForegroundColor Cyan
    Write-Host "REQ: $body" -ForegroundColor Gray
    try {
        $r = Invoke-WebRequest -Uri $url -Method POST -Headers $headers -Body $body -UseBasicParsing
        Write-Host "STATUS: $($r.StatusCode)" -ForegroundColor Green
        Write-Host "HEADERS: $($r.Headers | Out-String)"
        Write-Host "BODY:" -ForegroundColor Green
        Write-Host $r.Content
        return $r
    } catch {
        Write-Host "ERR: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.Exception.Response) {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $body = $reader.ReadToEnd()
            Write-Host "BODY: $body" -ForegroundColor Red
        }
    }
}

$init = '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
Send-Mcp $init 'initialize (2024-11-05)'

$notif = '{"jsonrpc":"2.0","method":"notifications/initialized"}'
Send-Mcp $notif 'notifications/initialized'

$list = '{"jsonrpc":"2.0","id":2,"method":"tools/list"}'
Send-Mcp $list 'tools/list'

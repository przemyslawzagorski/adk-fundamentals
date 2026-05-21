$url='http://127.0.0.1:3001/mcp'
$headers=@{'Accept'='application/json, text/event-stream';'Content-Type'='application/json'}
$init='{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
$r=Invoke-WebRequest -Uri $url -Method POST -Headers $headers -Body $init -UseBasicParsing
Write-Host "INIT: $($r.StatusCode)"
Write-Host $r.Content
Write-Host "---"
try {
    $r2=Invoke-WebRequest -Uri $url -Method POST -Headers $headers -Body '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' -UseBasicParsing
    Write-Host "LIST: $($r2.StatusCode)"
    Write-Host $r2.Content.Substring(0, [Math]::Min(2000, $r2.Content.Length))
} catch {
    Write-Host "LIST ERR: $($_.Exception.Message)"
}

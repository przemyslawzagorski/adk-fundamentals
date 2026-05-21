$headers = @{ "Accept" = "application/json, text/event-stream"; "Content-Type" = "application/json" }
$body = '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
try {
  $r = Invoke-WebRequest -Uri "http://127.0.0.1:3001/mcp" -Method POST -Headers $headers -Body $body -UseBasicParsing
  Write-Host "STATUS: $($r.StatusCode)"
  Write-Host "HEADERS:"
  $r.Headers | Out-String
  Write-Host "BODY:"
  $r.Content
} catch {
  Write-Host "ERR: $($_.Exception.Message)"
  if ($_.Exception.Response) {
    $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
    Write-Host "BODY:"
    $reader.ReadToEnd()
  }
}

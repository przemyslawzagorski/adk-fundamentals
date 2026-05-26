# ZAGI Studio — skrypty operatora

Wszystko czego potrzebujesz w jednym miejscu. Każdy skrypt odpalaj
**w osobnym terminalu PowerShell** (żeby logi szły na żywo i były
widoczne — to jest cały sens).

## Pliki

| # | Plik | Co robi | Port |
|---|------|---------|------|
| 00 | `00_kill_all.ps1`     | Twardy reset: ubija MCP, Playwright chromium, zwalnia porty 3001/8766/5173. Nie rusza zwykłego Chrome. | — |
| 01 | `01_start_mcp.ps1`    | Comarch MCP (Jira/Wiki/GitLab) — wrapper na `..\start_mcp.ps1`. | 3001 |
| 02 | `02_start_backend.ps1`| FastAPI/uvicorn + cały pipeline (SequentialAgent, NotebookLM tool, MCP klient). Tu lecą logi `[NotebookLM] QUESTION` i `RAW ANSWER`. | 8766 |
| 03 | `03_start_frontend.ps1`| Vite + React (ZAGI Studio UI). | 5173 |
| 04 | `04_export_cookies.ps1`| Re-eksport ciastek NotebookLM (gdy Google przekierowuje na login). | — |

## Standardowy start (3 terminale)

```powershell
# Terminal A
.\adk_training\module_22_spec_generator\scripts\01_start_mcp.ps1

# Terminal B  (poczekaj aż MCP wypisze "Streamable HTTP server listening")
.\adk_training\module_22_spec_generator\scripts\02_start_backend.ps1

# Terminal C
.\adk_training\module_22_spec_generator\scripts\03_start_frontend.ps1
```

Potem otwórz http://localhost:5173

## Restart (gdy coś wisi)

```powershell
.\adk_training\module_22_spec_generator\scripts\00_kill_all.ps1
# i powtarzasz 01 → 02 → 03
```

## Re-eksport cookies (gdy NotebookLM mówi "redirected to login")

1. **Zamknij wszystkie okna Chrome** (skrypt potrzebuje wyłącznego dostępu do profilu).
2. ```powershell
   .\adk_training\module_22_spec_generator\scripts\04_export_cookies.ps1
   ```
3. Skrypt prowadzi Cię przez DevTools (F12 → Network → Ctrl+R → Copy as cURL).
4. **Restart backendu** (02) — singleton NotebookLM ładuje cookies tylko raz.

## Co śledzić w którym terminalu

| Terminal | Czego szukać |
|----------|--------------|
| 01 MCP   | `[AuditLogger] tool=jira_get_issue status=SUCCESS` |
| 02 Backend | `[NotebookLM] QUESTION: ...`, `[NotebookLM] RAW ANSWER (len=N): ...`, błędy stack trace |
| 03 Frontend | tylko HMR / błędy buildów TS/Vite |

## Złota zasada

**MCP i backend zawsze restartujesz w parze.**
Build comarch-mcp w trybie `stateful` pozwala tylko na **jeden** `initialize`
na proces — jak backend nawiąże nową sesję, MCP musi być świeży.

## Szybki audyt portów

```powershell
@(3001,8766,5173) | ForEach-Object {
  $c = Get-NetTCPConnection -LocalPort $_ -State Listen -EA SilentlyContinue | Select -First 1
  if($c){"$_ LISTEN PID=$($c.OwningProcess)"}else{"$_ wolny"}
}
```

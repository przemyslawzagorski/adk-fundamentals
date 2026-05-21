# MCP server

`mcp_server.py` wystawia te same 9 tools z module_23 jako MCP — używaj z Claude
Desktop, Cursor, Cline lub innym MCP-aware klientem.

## Uruchomienie

```powershell
& .venv312\Scripts\Activate.ps1
python -m adk_training.module_23_auggie_integration.mcp_server
```

Domyślnie stdio transport. Server loguje do stderr (stdout zarezerwowany dla MCP).

## Konfiguracja klienta

=== "Claude Desktop"

    `~/AppData/Roaming/Claude/claude_desktop_config.json`:

    ```json
    {
      "mcpServers": {
        "adk-concierge": {
          "command": "C:/Users/NBPZAGORSKI/IdeaProjects/adk-fundamentals/.venv312/Scripts/python.exe",
          "args": ["-m", "adk_training.module_23_auggie_integration.mcp_server"]
        }
      }
    }
    ```

=== "Cursor"

    `Settings → MCP → Add server`:

    ```json
    {
      "command": "python",
      "args": ["-m", "adk_training.module_23_auggie_integration.mcp_server"],
      "env": { "PYTHONPATH": "C:\\Users\\NBPZAGORSKI\\IdeaProjects\\adk-fundamentals" }
    }
    ```

## Co dostajesz w IDE

- `RUN_AUGGIE` jako tool dostępny dla Claude w Cursor/Desktop.
- `WRITE_TESTS`, `REVIEW_PR`, `EXPLAIN_CODE`, `REFACTOR` — gotowe.
- `TELEMETRY`, `COST`, `HEALTH` — diagnostyka bez przełączania okna.

## Wywołanie z testu

```python
from adk_training.module_23_auggie_integration.mcp_server import build_server
server = build_server()
tools = server.list_tools()                # async w prawdziwym kliencie
assert any(t.name == "RUN_AUGGIE" for t in tools)
```

## Anti-patterns

- ❌ **Logowanie do `stdout`** — psuje protokół MCP. Używaj `logging` z handlerem na stderr.
- ❌ **Side effects w `list_tools`** — to ma być pure listing.
- ❌ **Brak limitów timeout** — IDE zawiśnie. `auggie_factory` ma timeout, ale tool MCP
  powinien też mieć (deadline propagacja w przyszłej wersji).

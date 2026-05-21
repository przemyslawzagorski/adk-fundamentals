# Developer guide

## Dodanie nowego tool'a

1. **Definicja** w `tools.py`:

    ```python
    @tool(
        name="MY_TOOL",
        description="Co robi w 1 zdaniu (Gemini użyje do routingu).",
        params={
            "input": {"type": "string", "description": "..."}
        },
    )
    def my_tool(input: str) -> dict:
        prompt = f"...{input}..."
        return auggie_run(prompt, opts={"model": "claude-sonnet-4.5"})
    ```

2. **Test** w `smoke_test.py` — dodaj wpis do `TOOLS_TO_TEST`.
3. **(Opcjonalnie)** wystaw przez MCP — automatycznie z `mcp_server.py` listingu.
4. **(Opcjonalnie)** dodaj kafelek w `web/frontend/src/components/Tools.tsx`.

## Debugowanie

```powershell
# pełny log Auggie
$env:AUGGIE_LOG_LEVEL="debug"
python -m adk_training.module_23_auggie_integration.health_check --full

# pojedynczy tool
python -c "from adk_training.module_23_auggie_integration.tools import dispatch; print(dispatch('HEALTH', {}))"
```

W przeglądarce: DevTools → Network → filter `text/event-stream` → SSE eventy
(`progress`, `final`, `error`).

## Konwencje

- Każda funkcja Auggie wywoływana przez `auggie_factory.auggie_run()` (jeden punkt
  wejścia → cache + resilience + cost).
- Tools zwracają `dict` (serializowane do JSON dla SSE i MCP).
- Nie loguj sekretów (`auth.py` ma `redact()`).
- Trzymaj prompty w plikach `*.md` lub stałych modułowych — nie w stringach inline
  (łatwiej je wersjonować i diffować).

## Testy

```powershell
python -m pytest adk_training\module_23_auggie_integration\tests -v
python adk_training\module_23_auggie_integration\smoke_test.py
```

Smoke test wymaga `ANTHROPIC_API_KEY` w `.env`.

## Frontend dev

```powershell
cd adk_training\module_23_auggie_integration\web\frontend
npm run dev          # 5173 + HMR
npm run build        # produkcja → dist/
npm run lint
```

Routing: React Router, stan globalny: zustand (cienki). HTTP: fetch + SSE
(`EventSource`).

## Migracja na nowy model

1. Dodaj wpis do `RATES_USD_PER_SEC` w `cost_tracker.py`.
2. Zmień default w `auggie_factory.DEFAULT_MODEL` lub `tools.py` per-tool.
3. Re-run `smoke_test.py` — porównaj koszt/latency w `tracker.snapshot()`.

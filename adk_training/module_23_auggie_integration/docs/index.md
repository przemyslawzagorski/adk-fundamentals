# AI Code Concierge — module_23

> **Two-tier orchestration**: Gemini Flash jako tani dispatcher + Auggie/Claude jako
> drogi specjalista od kodu. Płacisz za drogi model tylko gdy faktycznie potrzebujesz.

## TL;DR

```text
[User] → [ADK Gemini 2.5 Flash] → decyzja: prosta odp. / delegacja
                                ↓
                       [Auggie SDK + Claude Sonnet 4.5]
                                ↓
                       (workspace, narzędzia, weryfikacja)
```

## Co dostajesz

| Komponent | Plik | Rola |
|---|---|---|
| ADK agent | `agent.py` | `root_agent`, 9 tools, działa pod `adk web` |
| Tools | `tools.py` | 6 produkcyjnych + 3 diagnostyczne (telemetria/koszty/health) |
| Auggie factory | `auggie_factory.py` | wspólna infra: config, telemetria, listener |
| Cache | `caching.py` | LRU+TTL, thread-safe |
| Cost tracker | `cost_tracker.py` | real-time USD per tool/model |
| Resilience | `resilience.py` | retry + circuit breaker |
| ACP pool | `acp_pool.py` | singleton, eliminuje cold-start subprocess |
| MCP server | `mcp_server.py` | wystawia 9 tools dla Claude Desktop / Cursor |
| Health | `health_check.py` | standalone CLI (`python health_check.py --ping`) |
| CI review | `ci_review.py` + `.github/workflows/ai-code-review.yml` | AI review każdego PR |
| Smoke test | `smoke_test.py` | E2E test 9 tools + cache + diagnostyka |
| Web | `web/` | FastAPI + React Concierge UI (port 8770 / 5173) |

## Szybki start

```powershell
& .venv312\Scripts\Activate.ps1
python -m uvicorn adk_training.module_23_auggie_integration.web.app:app --port 8770 --reload
# w drugim oknie
cd adk_training\module_23_auggie_integration\web\frontend
npm run dev
```

Otwórz [http://localhost:5173](http://localhost:5173).

## Reading order

1. [Architecture](architecture.md) — dwie warstwy + szyna danych.
2. [Cache · cost · resilience](cost-cache-resilience.md) — guardrails kosztów i niezawodności.
3. [Developer guide](developer-guide.md) — jak dodać tool, jak debugować.
4. [MCP server](mcp-server.md) — integracja z Claude Desktop / Cursor.
5. [CI / GitHub Action](ci-review.md) — AI review w PR.
6. [Business value](business-value.md) — pitch dla decydentów.
7. [Security](security.md) — granice zaufania, allowlisty, secrets.

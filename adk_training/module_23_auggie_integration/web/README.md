# Auggie Concierge Web

Profesjonalna aplikacja webowa dla `module_23_auggie_integration` — Netflix-vibe UI w niebiesko-granatowej kolorystyce, z eksplicytnym krokiem **indeksowania workspace** jako bramą do uruchamiania toolów.

## Stack

- **Backend**: FastAPI + uvicorn, SSE streaming (`text/event-stream`)
- **Frontend**: Vite 5 + React 18 + TypeScript 5.6 + Tailwind 3.4 + Framer Motion + Radix UI + lucide-react
- **Auth**: dziedziczy z modułu 23 (`AUGGIE_SESSION_AUTH` lub `~/.augment/session.json`)

## Dlaczego backend musi działać na WSL (nie Windows)

> **To jest najważniejsza rzecz do zrozumienia zanim uruchomisz aplikację.**

Aplikacja używa dwóch trybów komunikacji z auggie:

| Tryb | Aktywacja | Czas `analyze_codebase` | Kiedy działa |
|---|---|---|---|
| **ACP (SDK)** | domyślny (brak `AUGGIE_USE_CLI`) | **~35–70 s** | tylko Linux/WSL |
| **CLI fallback** | `AUGGIE_USE_CLI=1` | ~10–20 s | Windows i Linux |

**Problem z Windows + ACP:**
Tool `analyze_codebase` używa trybu ACP (`return_type=List[CodebaseFinding]`), który spawna auggie jako lokalny serwer SDK. Na Windows ten proces trwa **~580 sekund** (praktyczny timeout). Nie jest to błąd konfiguracji — to ograniczenie wydajności auggie SDK na Windows NTFS.

**Rozwiązanie: backend na WSL.**
Na natywnym `/usr/bin/auggie` (Linux) ten sam tool kończy się w **35–70 sekund**. Dlatego backend FastAPI musi być uruchomiony w środowisku WSL2, gdzie auggie działa natywnie.

**CLI fallback (`AUGGIE_USE_CLI=1`) nie jest rozwiązaniem dla `analyze_codebase`**, bo tool ten jawnie używa `return_type=List[CodebaseFinding]` (strukturyzowany output ACP). CLI zwraca tylko surowy string.

---

## Quick start (zalecany: backend WSL + frontend Windows)

### Terminal 1 — Backend na WSL (obowiązkowe dla analyze_codebase)

Użyj gotowego skryptu startowego z rootu repo:

```powershell
# z root projektu (Windows PowerShell)
wsl -- bash /mnt/c/Users/NBPZAGORSKI/IdeaProjects/adk-fundamentals/_wsl_backend.sh
```

Skrypt automatycznie:
1. Kopiuje `~/.augment/session.json` z Windows do WSL (auth)
2. Synchronizuje pliki modułu z `/mnt/c/...` do `~/adk23-test/`
3. Ustawia `AUGGIE_CLI_PATH=/usr/bin/auggie` (natywny Linux binary, nie `.cmd` wrapper)
4. Uruchamia uvicorn na `0.0.0.0:8770` (dostępny z Windows przez WSL IP)

Backend będzie widoczny pod adresem WSL IP (np. `http://172.18.x.x:8770`).

### Terminal 2 — Python proxy (przekierowanie localhost:8770 → WSL)

WSL2 nie forwarduje portów automatycznie do `127.0.0.1` (brak uprawnień admina do `netsh`).
Uruchom lekki Python proxy, który robi to bez uprawnień:

```powershell
# z root projektu (Windows PowerShell)
python _wsl_proxy.py 8770 8770
# → [proxy] 127.0.0.1:8770 -> 172.18.x.x:8770
```

Od tego momentu `http://127.0.0.1:8770` działa z Windows i frontend może się połączyć normalnie.

### Terminal 3 — Frontend (Vite dev server, Windows)

```powershell
cd adk_training/module_23_auggie_integration/web/frontend
npm run dev
# → http://localhost:5173
```

Vite automatycznie proxy'uje `/api/*` i `/health` do `http://127.0.0.1:8770` (zdefiniowane w `vite.config.ts`).

### Weryfikacja — czy wszystko działa

```powershell
# health check backendu przez proxy
(Invoke-WebRequest http://127.0.0.1:8770/api/health -UseBasicParsing).Content

# test analyze_codebase (powinno zająć ~35-70s, NIE 580s)
$body = '{"tool_id":"analyze_codebase","inputs":{"target_path":"","max_files":5}}'
$resp = Invoke-WebRequest http://127.0.0.1:8770/api/tools/run -Method POST `
  -ContentType "application/json" -Body $body -UseBasicParsing
# Pierwsze zdarzenie SSE zawiera run_id - sprawdź wynik pod /api/runs/{run_id}
```

---

## Alternatywa: backend Windows z CLI fallback (bez analyze_codebase)

Jeśli potrzebujesz uruchomić szybko i `analyze_codebase` ci nie jest potrzebny:

```powershell
# z root projektu
$env:AUGGIE_USE_CLI     = "1"   # CLI mode — działa szybko na Windows (~10-20s)
$env:CONCIERGE_PORT     = "8770"
$env:AUGGIE_WORKSPACE   = "C:\Users\NBPZAGORSKI\IdeaProjects\adk-fundamentals"
$env:AUGGIE_CLI_PATH    = "C:\Users\NBPZAGORSKI\IdeaProjects\adk-fundamentals\tools\auggie-wsl.cmd"
$env:AUGGIE_MODEL       = "sonnet4.5"
.venv312\Scripts\python.exe -m adk_training.module_23_auggie_integration.web.app
```

**Ograniczenie:** `analyze_codebase` w tym trybie zajmie ~580s (ACP na Windows) lub zakończy się timeoutem. Wszystkie inne toole (`ask_specialist`, `review_code`, itp.) działają normalnie przez CLI.

---

## Production build (opcjonalnie)

```powershell
cd adk_training/module_23_auggie_integration/web/frontend
npm run build
# dist/ → backend serwuje statyczne pliki pod /
# Po buildzie wystarczy uruchomić tylko backend, bez npm run dev
```

## Architektura UX

```
┌─────────────────────────────────────────────┐
│ [Navbar] Concierge · Overview · Studio      │
├─────────────────────────────────────────────┤
│ [Studio]                                    │
│  ┌─────────────────────────────────────┐    │
│  │ 🔥 STEP 1: Index Workspace          │    │  ← gating UX
│  │ • Idle → [Start Indexing]           │    │
│  │ • Running → live SSE ticks          │    │
│  │ • Ready → ✓ unlock tools            │    │
│  │ • Failed → retry + error            │    │
│  └─────────────────────────────────────┘    │
│  ┌─ Telemetry: cache rate, $ cost ─┐        │
│  └────────────────────────────────────┘     │
│  ┌─ Category pills ─────────────────┐       │
│  │ [All] [Review] [Security] ...    │       │
│  └────────────────────────────────────┘     │
│  ┌─ Tool grid (locked until index ready)    │
│  │ [Card] [Card] [Card]                     │
│  │ [Card] [Card] [Card]                     │
│  └────────────────────────────────────┘     │
└─────────────────────────────────────────────┘

[Tool click] → Modal:
┌──────────────────────┬────────────────────────┐
│ Inputs (form)        │ Status pill + timeline │
│ • textarea/input     │ Live SSE events        │
│ • required validation│ Result: markdown/code  │
│ [Execute]            │ [Copy] · [Re-run]      │
└──────────────────────┴────────────────────────┘
```

## Endpoints (backend)

| Endpoint | Method | Opis |
|---|---|---|
| `/api/config` | GET | Snapshot konfiguracji + index state |
| `/api/health` | GET | Pełny `auggie_health()` (CLI, session, breaker) |
| `/api/tools` | GET | Katalog 6 produkcyjnych toolów z metadanymi |
| `/api/index/start` | POST | **SSE** — warm-up `auggie --wait-for-indexing` |
| `/api/index/status` | GET | Stan ostatniego warm-upa |
| `/api/tools/run` | POST | **SSE** — uruchamia tool, streamuje progress + final result |
| `/api/telemetry` | GET | Cache hit rate, summary, last calls |
| `/api/cost` | GET | Estymacja USD per tool/model |
| `/api/cache/clear` | POST | Czyści cache (do testów) |
| `/docs` | GET | Swagger UI |

## Customization

| Env var | Default | Opis |
|---|---|---|
| `CONCIERGE_PORT` | `8770` | Port backendu |
| `CONCIERGE_CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | CSV |
| `CONCIERGE_LOG_LEVEL` | `INFO` | DEBUG / INFO / WARNING |
| `AUGGIE_USE_CLI` | `0` | `1` = wymuś CLI fallback (Windows-friendly) |
| `AUGGIE_WORKSPACE` | repo root | Default workspace dla indexu i toolów |
| `AUGGIE_MODEL` | `claude-sonnet-4-5` | Model |
| `AUGGIE_SESSION_AUTH` | — | Path do session.json (override default) |

## Theme tokens (Tailwind)

```js
cnc: {
  bg: "#020617",          // void deep navy
  surface: "#0b1224",
  border: "#1e293b",
  ink: "#e2e8f0",
  muted: "#7d8aa3",
  azure: "#1e40af",       // deep granat
  electric: "#3b82f6",    // primary
  electric2: "#60a5fa",
  cyan: "#22d3ee",        // accent
  gold: "#fbbf24",        // warning
}
```

Gradient brand: `linear-gradient(120deg, #1e40af → #3b82f6 → #22d3ee)` (`.text-gradient-azure`).

## Troubleshooting

**Q: `Auggie CLI not found`**
A: `npm install -g @augmentcode/auggie` lub ustaw `AUGGIE_CLI_PATH=/abs/path/to/auggie`.

**Q: Indexing wisi >5min**
A: Pierwsze indexowanie dużego repo może trwać. Sprawdź `~/.augment/` — cache idzie tam. Kolejne uruchomienia są inkrementalne.

**Q: SSE nie streamuje w przeglądarce**
A: Sprawdź czy proxy w `vite.config.ts` celuje w port backendu. Przy nginx ustaw `proxy_buffering off; proxy_cache off; X-Accel-Buffering: no;`.

**Q: Tool wymaga indeksu ale dostaje halucynację**
A: Sprawdź czy `index.status === 'ready'` w `/api/config`. Jeśli `failed` — kliknij Retry w UI.

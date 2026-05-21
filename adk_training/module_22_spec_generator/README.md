# Module 22 — Spec Generator (Ticket -> HLD + Epiki Jira)

**Status: MVP** — pipeline ADK dziala end-to-end (weryfikacja live z Gemini 2.5 Pro, 3:38). 
Integracja z Comarch MCP (Jira/Wiki/GitLab) czeka na rotacje tokenow — do tego czasu agenty 
kontekstowe i ticket_fetcher dzialaja w trybie fallback (komunikat "brak MCP").

## Po co
Jeden ticket Jira (np. "potrzebujemy nowego zeznania SWOK") rozwinac automatycznie w:
1. **HLD** (High-Level Design) w jezyku polskim, dopasowany do kontekstu projektu.
2. **Epiki Jira** (rozbicie na 3-7 epikow z Acceptance Criteria) gotowe do opublikowania.
3. *Opcjonalnie* (efekt WOW): wzbogacenie o wiedze domenowa z **NotebookLM** (SWOK/inne).

## Architektura (ADK)

```
SpecGeneratorAgent (SequentialAgent)
  1. TicketFetcherAgent       - Comarch MCP (Jira) -> ticket.description
  2. ContextGatherer (Parallel)
        - wiki_context_agent    - Confluence Wiki via MCP
        - code_context_agent    - GitLab MCP (szukanie podobnych zmian)
        - notebooklm_agent_tool - AGENT-AS-TOOL (opcjonalny, on-demand)
  3. HldWriterAgent           - pisze HLD (template z prompts/hld_pl.md)
  4. CritiqueLoop (LoopAgent, max_iterations=3..5)
        - critic_agent          - wskazuje braki/niespojnosci
        - reviser_agent         - poprawia HLD
        - escalation_check      - jesli "LGTM" -> escalate, exit loop
  5. EpicDecomposerAgent      - HLD -> [Epic(title, AC, priority, labels)]
  6. HumanApprovalGate        - HITL: pauza, web UI pokazuje preview
  7. JiraPublisherAgent       - publikuje zatwierdzone epiki via Comarch MCP
```

### Uzasadnienie kluczowych decyzji
- **SequentialAgent na top** — deterministyczny flow, jedno wejscie/jedno wyjscie.
- **ParallelAgent w kroku 2** — niezalezne zrodla kontekstu odpalane rownolegle (czas!).
- **NotebookLM jako "agent as tool"** — LLM decyduje czy odpytac (koszt + czas), nie zawsze potrzebne.
- **LoopAgent z escalation** — samokrytyka, max 3-5 iteracji (konfigurowalne), wyjscie gdy critic mowi "LGTM" (`actions.escalate = True`).
- **HumanApprovalGate przed Jira** — nigdy nie publikujemy bez akceptacji czlowieka (web UI).

## Wymagania konfiguracyjne (ENV)

```
# Gemini
GOOGLE_CLOUD_PROJECT=adk-training-pz
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=1
SPEC_GEN_LLM_MODEL=gemini-2.5-pro        # mocniejszy model do projektowania

# Comarch MCP (UWAGA: patrz SECURITY.md — tokeny w Secret Manager!)
COMARCH_MCP_JIRA_URL=https://tapir.krakow.comarch/jira
COMARCH_MCP_JIRA_TOKEN=...                # PAT (rotate!)
COMARCH_MCP_WIKI_URL=https://tapir.krakow.comarch/wiki
COMARCH_MCP_WIKI_TOKEN=...
COMARCH_MCP_GITLAB_URL=https://git.swozyk.krakow.comarch
COMARCH_MCP_GITLAB_TOKEN=...

# NotebookLM (opcjonalne)
NOTEBOOKLM_ENABLED=0                      # 1 aby wlaczyc
NOTEBOOKLM_NOTEBOOK_ID=...

# Critique loop
SPEC_GEN_MAX_CRITIQUE_ITERATIONS=3        # 3..5
```

## Struktura plikow

```
module_22_spec_generator/
  agents/
    spec_generator.py           # factory _build_spec_generator()
    ticket_fetcher.py
    context_parallel.py         # ParallelAgent wrapper
    hld_writer.py
    critique_loop.py            # LoopAgent + critic/reviser
    epic_decomposer.py
    jira_publisher.py
  tools/
    comarch_mcp.py              # MCPToolset -> Jira/Wiki/GitLab
    notebooklm_tool.py          # AgentTool (agent-as-tool)
  prompts/
    ticket_fetcher_pl.md
    hld_pl.md
    critic_pl.md
    reviser_pl.md
    epic_decomposer_pl.md
  web/
    app.py                      # FastAPI UI do HITL
    templates/
  tests/
    test_critique_loop.py       # offline (FakeLlm)
    test_epic_decomposer.py
    live/
      test_spec_gen_e2e.py      # live, gated RUN_LIVE_TESTS=1
```

## Status implementacji

- [x] Struktura katalogow, prompts PL, config z ENV
- [x] Wszystkie 7 buildery agentow + `parse_epics_json` (odporny na markdown fence `{"epics": [...]}`)
- [x] `EscalationChecker(BaseAgent)` — LGTM -> `actions.escalate=True` -> wyjscie z LoopAgent
- [x] Buildery akceptuja `model=` override (wstrzykniecie `FakeLlm` w testach)
- [x] **33 testy offline** (FakeLlm, parser, web, struktura)
- [x] **E2E test offline** — pelny SequentialAgent + ParallelAgent + LoopAgent z 6 FakeLlm
- [x] **Live test** z realnym Gemini 2.5 Pro (gated `RUN_LIVE_TESTS=1` + `GOOGLE_CLOUD_PROJECT`)
- [x] **Ewaluacja via ADK `AgentEvaluator`** — działa (2:34 live), `root_agent = epic_decomposer` (pojedynczy LlmAgent, bo `LocalEvalService` nie obsługuje multi-stage SequentialAgent — patrz [CRITICAL_REVIEW_2026_04_17.md § Issue 12](../CRITICAL_REVIEW_2026_04_17.md)).
- [x] **Web UI (FastAPI)** — `/api/generate` uruchamia Runnera, feature-flag `SPEC_GEN_USE_REAL_PIPELINE=1`
- [ ] Integracja Comarch MCP — Jira/Wiki/GitLab (wymaga tokenow)
- [ ] Publikacja do Jira (jira_publisher + HITL approve w web/app.py)
- [ ] NotebookLM — realna integracja (obecnie stub z feature flag)
- [ ] Deploy Cloud Run + Secret Manager + Firestore dla `_SESSIONS`

## Testy

```powershell
# offline (domyslnie)
python -m pytest                                   # 33 passed, 2 deselected (live)

# live (koszt API, czas 2-4 min per test)
$env:RUN_LIVE_TESTS="1"; $env:GOOGLE_CLOUD_PROJECT="<twoj-projekt>"
python -m pytest -m live                           # 2 passed
# - test_spec_generator_live.py (pelen pipeline, ~3-4 min, asercje recznie)
# - test_agent_evaluator.py    (epic_decomposer via ADK AgentEvaluator, ~2-3 min)

# web UI w trybie realnym
$env:SPEC_GEN_USE_REAL_PIPELINE="1"
python -m web.app                                  # http://127.0.0.1:8766
```

## Ewaluacja via ADK `AgentEvaluator`

Oficjalny framework ewaluacji ADK ([docs](https://adk.dev/evaluate/)) pozwala testowac
pipeline deklaratywnie w plikach `*.test.json`, bez recznie pisanych asercji na `state`.

> ✅ **Status 17.04.2026: PASSING** (1 passed / 2:34 live, Gemini 2.5 Pro).
>
> **Design decision:** `agent_for_eval.agent.root_agent = epic_decomposer` (pojedynczy LlmAgent),
> nie pelen `SpecGeneratorAgent` (SequentialAgent). Powod: `LocalEvalService` wymaga 1:1 mapowania
> user turns <-> inference, a multi-stage SequentialAgent emituje N eventow `isFinalResponse=True`
> (po jednym per sub-agent z `output_key`) → `ValueError: Inferences should match conversations`.
>
> Wniosek: `AgentEvaluator` testuje **jeden** stage (epic_decomposer = najwazniejszy parser JSON),
> pelen pipeline pokryty przez `test_spec_generator_live.py` (live) i `test_spec_generator_e2e.py` (offline).
> Szczegoly: [../CRITICAL_REVIEW_2026_04_17.md § Issue 12](../CRITICAL_REVIEW_2026_04_17.md).

**Struktura:**
- [agent_for_eval/agent.py](agent_for_eval/agent.py) — eksportuje `root_agent`
  (konwencja ADK: `module_name` musi konczyc sie `.agent` albo zawierac atrybut `agent`).
  Ustalona konfiguracja: `enable_notebooklm=False`, `max_critique_iterations=1` (mniejszy koszt).
- [tests/eval/spec_gen_basic.test.json](tests/eval/spec_gen_basic.test.json) — schema `EvalSet`
  (`eval_cases[].conversation[].userContent` + `finalResponse`). Mozna dodawac kolejne pliki
  `*.test.json` do tego katalogu.
- [tests/eval/test_config.json](tests/eval/test_config.json) — progi metryk.
  Obecnie tylko `response_match_score: 0.05` (ROUGE-1, lokalne, bez LLM judge, bez kosztow).
- [tests/live/test_agent_evaluator.py](tests/live/test_agent_evaluator.py) — pytest wrapper
  wywolujacy `AgentEvaluator.evaluate(agent_module="agent_for_eval.agent", ...)`.

**Wymagania:** zainstaluj ADK z extrasami eval (pandas + LocalEvalService):
```powershell
pip install "google-adk[eval]"
```
Bez tego `AgentEvaluator.evaluate(...)` rzuca `ModuleNotFoundError: Eval module is not installed`.

**Dostepne metryki** (do dolozenia w `test_config.json` wedlug potrzeby):
- `response_match_score` — ROUGE-1, lokalne (wlaczone)
- `final_response_match_v2` — LLM-judged semantyczny match (dodatkowy koszt Gemini)
- `rubric_based_final_response_quality_v1` — LLM-judge na customowych rubrykach
  (np. "HLD ma sekcje 'Cel biznesowy'", "kazdy epik ma acceptance_criteria")
- `hallucinations_v1`, `safety_v1` — groundedness / safety
- `tool_trajectory_avg_score` — exact match sciezki wywolan narzedzi (u nas N/A,
  bo nasze podagenty uzywaja `output_key`, nie `FunctionTool`)

**User Simulation** (`ConversationScenario` + `conversation_plan`,
[blog](https://developers.googleblog.com/announcing-user-simulation-in-adk-evaluation/)):
dynamicznie generowane wypowiedzi uzytkownika. W M22 **nieuzywane** — pipeline jest
`SequentialAgent` (jednokierunkowy, nie multi-turn chat). Sensowne dla **M13 code-analyst**
(chat z uzytkownikiem) — zob. tamtejsze `tests/live/test_quality_eval.py` jako kandydat
do migracji.

## Roadmap realizacji

**Sprint 1 — OFFLINE CORE (done)**: SequentialAgent + LoopAgent + EpicDecomposer, FakeLlm tests, parser.  
**Sprint 2 — MCP Comarch**: ticket_fetcher + jira_publisher (sandbox projekt Jira).  
**Sprint 3 — HITL web UI**: preview + approve/reject/edit epikow przed publikacja.  
**Sprint 4 — NotebookLM**: realna integracja agent-as-tool.  
**Sprint 5 — Produkcja**: Cloud Run + Secret Manager + Firestore.

## Bezpieczenstwo
Zobacz `../../SECURITY.md`. **Tokeny Comarch nie moga trafic do kodu ani commita** — pre-commit hook w repo glownym blokuje typowe wzorce.

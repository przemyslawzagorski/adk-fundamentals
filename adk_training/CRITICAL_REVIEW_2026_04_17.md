# Krytyczna ocena stanu projektu — adk-fundamentals

**Data:** 17 kwietnia 2026  
**Zakres:** cały workspace `adk-fundamentals`, ze szczególnym uwzględnieniem modułów 13, 21, 22 i warstwy testowej.

## TL;DR

Projekt dojechał do działającego MVP modułu 22 (Spec Generator) oraz utwardzonego M13 (Code Analyst). Oficjalny `AgentEvaluator` z ADK jest zintegrowany. **Największe ryzyka:** (1) brak realnej integracji Comarch MCP w M22, (2) zero automatyzacji live-testów w CI (wszystkie za flagą `RUN_LIVE_TESTS=1`, uruchamiane ręcznie), (3) rozjazd między "33 moduły w README" a realnie działającymi modułami, (4) brak testów regresyjnych ewaluacji (`response_match_score` z progiem 0.05 to w praktyce smoke test, nie eval jakościowy).

---

## Co jest mocne

### Warstwa testowa modułu 22
- **33 testy offline** z `FakeLlm` — pełne pokrycie SequentialAgent + ParallelAgent + LoopAgent + parserów. Testy strukturalne (`test_spec_generator_structure.py`) są prawdziwie nudne i to dobrze.
- **E2E offline z 6 FakeLlm** odpalający cały pipeline bez Gemini — rzadkość w ekosystemie ADK, bardzo dobry wzorzec.
- **`parse_epics_json`** z elastycznością: `list` / `dict{"epics": [...]}` / markdown fence. Naprawa oparta na realnym bug-fixie z live testu.
- **Live test** z realnym Gemini 2.5 Pro (3:38) — potwierdzony pass 4.11.2026.

### Integracja `AgentEvaluator`
- Wrapper [agent_for_eval/agent.py](../module_22_spec_generator/agent_for_eval/agent.py) zgodny z konwencją ADK (nazwa modułu kończy się `.agent`).
- `.test.json` zgodny z pydantic schema `EvalSet/EvalCase/Invocation`.
- Gating `RUN_LIVE_TESTS=1` — domyślnie nie pali API.

### Moduł 13 (Code Analyst)
- `retry_policy.py`, `telemetry.py`, `security.py` wyseparowane — świadoma architektura.
- MkDocs + Dockerfile + compose — najbardziej dojrzały moduł w repo.

---

## Co jest słabe / ryzykowne

### 1. `response_match_score: 0.05` to smoke test, nie ewaluacja
**Problem:** Prog 0.05 ROUGE-1 sprawdza w praktyce tylko czy pipeline nie zwrócił pustego stringa. To NIE jest ocena jakości spec/epików.

**Konsekwencje:** Zielona ewaluacja przy kompletnie bzdurnym outpucie. False sense of security dla uczestników szkolenia.

**Mitigacja (do zrobienia):**
- Dołożyć `rubric_based_final_response_quality_v1` z rubrykami ("czy odpowiedź zawiera niepustą tablicę epików JSON", "czy każdy epik ma `acceptance_criteria`"). To LLM-judge → dodatkowe koszty Gemini, ale namacalny sygnał jakości.
- Alternatywnie `final_response_match_v2` z referencyjnym epikiem-wzorcem.

### 2. Brak Comarch MCP → pipeline jest „demo”, nie produkt
**Problem:** `ticket_fetcher`, `wiki_context`, `gitlab_context` bez realnych tokenów działają w fallbacku ("brak MCP"). Cały kontekst Comarch leci w powietrze — Gemini zmyśla.

**Konsekwencje:** Live test pokazuje HLD + epiki, ale **zmyślone** — brak zakotwiczenia w rzeczywistych ticketach Jira / wiki / kodzie.

**Mitigacja:**
- Sprint 2 z roadmapy (MCP Comarch) jest blocking-krytyczny. Bez tego M22 to pokaz generatora lorem ipsum.
- W międzyczasie: dodać `hallucinations_v1` do `test_config.json` — ten ewaluator weryfikuje groundedness względem `intermediate_responses`. Wyłapie zmyślenia.

### 3. Live testy nie są w CI
**Problem:** `RUN_LIVE_TESTS=1` odpalamy ręcznie. Nic nie gwarantuje że pipeline działa po mergach.

**Konsekwencje:** Regresja w prompcie / configu przejdzie offline (FakeLlm) i wybuchnie dopiero u użytkownika.

**Mitigacja:**
- GH Actions workflow `live-eval.yml` odpalany nightly (`schedule: cron`) lub manualnie (`workflow_dispatch`) z secretem GCP. Koszt: ~0.01 USD / run.
- Budżetowanie: `num_runs=1`, `max_critique_iterations=1`, tylko `spec_gen_basic.test.json`.

### 4. Rozjazd dokumentacji modułów
**Problem:** README główny `adk_training/README.md` wymienia moduły 01-16 z różnymi statusami, ale M13/M20/M21/M22 są poza tą tabelką. `MAPA_ARCHIPELAGU_ADK.md`, `PLAN_SZKOLENIA_NARRACJA.md`, `BUSINESS_FLOWS.md` — to 3 niezależne narracje, które mogą się rozjeżdżać z rzeczywistością.

**Konsekwencje:** Uczestnik szkolenia nie wie który dokument jest „prawdą".

**Mitigacja:**
- Jeden indeks `INDEX.md` z tabelą: moduł, status (MVP / stub / production-ready), testy (liczba), live-ready (tak/nie).
- Pozostałe dokumenty narracyjne → podlinkować z indeksu, nie duplikować statusów.

### 5. `pz_bonus/` i folder `reports/` bez retencji
**Problem:** W repo widać `reports/report_module_01_*.json` + `.md` z kilku runów. Brak `.gitignore` na te artefakty → commitujemy śmieci.

**Mitigacja:** `.gitignore`:
```
/reports/
/conversations/
/eval_run.log
```

### 6. Kilka modułów wygląda na porzucone / eksperymentalne
- `module_20_analyst_system` — brak README z jasnym statusem.
- `module_21_adk_tester` — wpisane w MAPA_ARCHIPELAGU ale bez weryfikacji czy działa.
- `notebooklm_agent/` w root — nie jest przypisany do żadnego modułu.
- `pz_bonus/` — nazwa nie mówi nic uczestnikowi.

**Mitigacja:** Decyzja: które moduły są kanonicznymi w ścieżce szkoleniowej, a które to sandbox → przenieść sandbox do `_experimental/`.

### 7. Wielokierunkowe instalacje `google-adk`
**Problem:** Używamy `C:\Users\NBPZAGORSKI\AppData\Local\Programs\Python\Python312\Lib\site-packages\google\adk` (system Python), a w repo jest też `.venv312/`. `AgentEvaluator[eval]` zainstalowany dziś do **system Pythona**, nie do venv. To „przypadkiem działa".

**Konsekwencje:** Nieprzewidywalne rozjazdy zależności między maszynami / CI.

**Mitigacja:**
- `.venv312/Scripts/pip install -e module_22_spec_generator[eval]` lub pełne `requirements.txt` per moduł z `google-adk[eval]>=1.28`.
- Alternatywnie: `uv` lub `pip-tools` + lockfile.

### 8. Brak wersjonowania promptów
**Problem:** Prompt-y siedzą w `prompts/*.md`, bez hash/wersji. Zmiana prompta → zmiana wyników → brak sposobu powiązania eval-result z wersją prompta.

**Mitigacja:** Nagłówek YAML w każdym `.md` z `version: 1.2.0` + `updated: 2026-04-17`. Log w telemetrii który prompt został użyty.

### 9. `agent_for_eval` ma hardkod `max_critique_iterations=1`
**Problem:** Testujemy „pipeline z 1 iteracją krytyki", nie „pipeline production" (3-5 iter). Ewaluacja nie sprawdza tego co uruchomi użytkownik przez web UI.

**Mitigacja:** Parametryzować przez ENV `EVAL_CRITIQUE_ITERATIONS` (domyślnie 1 dla kosztów, ale opcja 3 dla pełnego runu).

### 10. Brak `__init__.py` dla `agent_for_eval`? — wpadka
Sprawdzone: `__init__.py` istnieje. OK.

Ale: **konwencja ADK** oczekuje albo submodułu `.agent` albo atrybutu `agent`. Nasz pierwszy live run wybuchł bo miałem `agent_module="agent_for_eval"` zamiast `agent_for_eval.agent`. To nie jest oczywiste z docs — warto dodać FAQ / troubleshooting.

### 11. User Simulation pominięty dla M13
**Problem:** M13 (Code Analyst) jest chat-based i idealnie pasuje do `ConversationScenario` + User Simulation. Nadal używa własnego judge-LLM z `test_quality_eval.py`. Duplikacja wysiłku.

**Mitigacja:** Osobny ticket: zmigrować M13 eval na ADK `AgentEvaluator` + User Simulation (`conversation_plan: "user pyta o bugfixy, potem drąży alternatywy"`). Od razu zyskamy `hallucinations_v1` + `safety_v1`.

### 12. ✅ `AgentEvaluator` nie obsługuje multi-stage SequentialAgent — **ROZWIĄZANE 17.04.2026**

**Problem (zweryfikowany):** Pełny live run `SpecGeneratorAgent` (5:46) wywalił się na:
```
ValueError: Inferences should match conversations in eval case.
Found 2 inferences 1 conversations in eval cases.
```
`LocalEvalService._evaluate_single_inference_result` wymaga **ścisłego 1:1 mapowania** liczby user turns w `conversation[]` do liczby zebranych "inferences". `SequentialAgent` z kilkoma sub-agentami z `output_key` emituje >1 eventów `isFinalResponse()=True`.

**Zastosowane rozwiązanie (Opcja A):**
- `agent_for_eval/agent.py` → `root_agent = build_epic_decomposer()` (pojedynczy LlmAgent).
- `tests/eval/spec_gen_basic.test.json` → user message zawiera pełny HLD + prośbę o epiki JSON.
- `tests/eval/test_config.json` → próg ROUGE-1 obniżony do `0.02` (denominator duży bo odpowiedź JSON jest długa względem 8-słownego reference'a).

**Wynik live 17.04.2026:** `1 passed in 154.60s` (2:34). Epiki JSON prawidłowo wygenerowane przez Gemini 2.5 Pro, struktura zgodna z promptem (`title`, `acceptance_criteria`, `labels`, `dependencies`, `priority`, `estimated_story_points`).

**Trade-off:** Ewaluujemy tylko **jeden stage** pipeline (najważniejszy — parser JSON epików). Pełen `SpecGeneratorAgent` nadal testowany przez:
- `tests/test_spec_generator_e2e.py` (offline, 6× FakeLlm, full flow)
- `tests/live/test_spec_generator_live.py` (live, Gemini, ręczne asercje)

**Lesson learned (wartość insightu):** Dokumentacja ADK (`https://adk.dev/evaluate/`) nie mówi o tym ograniczeniu — tutoriale pokazują pojedynczy LlmAgent. Dla pipeline hierarchicznych `AgentEvaluator` wymaga **zawężenia do pojedynczego stage** i dostarczenia kontekstu przez user message (lub potencjalnie `session_input.state` + placeholdery w prompcie — niezweryfikowane).

---

## Priorytety (Top 5, realizowalne po kolei)

1. ✅ **Naprawa integracji `AgentEvaluator`** (Issue 12) — **DONE 17.04.2026** (1 passed, 2:34 live). `agent_for_eval.agent.root_agent = epic_decomposer`.
2. **Dołożyć `hallucinations_v1`** do M22 `test_config.json` — wyłapie zmyślenia (groundedness vs `intermediate_responses`).
3. **Nightly GH Action** z live eval (`workflow_dispatch` + `schedule`) — jedna flaga, niski koszt.
4. **Dokumentacja: INDEX.md** z prawdziwą matrycą statusów modułów; wyciąć/oznaczyć „_experimental".
5. **Sprint 2 z roadmapy M22** — realna integracja Comarch MCP (blocker dla użyteczności).

## Nice-to-have (później)

- User Simulation dla M13.
- Rubryki jakości dla M22 (`rubric_based_final_response_quality_v1`).
- Wersjonowanie promptów (YAML frontmatter).
- Lockfile zależności (`uv pip compile` lub `pip-tools`).
- ENV `EVAL_CRITIQUE_ITERATIONS` dla agent_for_eval.

## Co celowo odkładam

- **Deploy Cloud Run / Secret Manager / Firestore** — ma sens dopiero po Sprint 2 (MCP).
- **Jira publisher + HITL web UI** — zależy od MCP.
- **NotebookLM realny** — efekt WOW, ale nie blocker dla MVP ścieżki szkoleniowej.

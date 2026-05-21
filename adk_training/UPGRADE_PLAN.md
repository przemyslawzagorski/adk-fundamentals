# UPGRADE PLAN — Modernizacja Module 23 i 24 do ADK 2.0

> **Cel**: Migracja `module_23_auggie_integration` i `module_24_audit_ops`
> do standardu ADK 2.0 (Workflows / Graphs / Stateful Agents).
> Dokument opisuje konkretne kroki, mapy zmian i wzorce z Modułów 25-30.

---

## Podsumowanie modernizacji

| Moduł         | Stan obecny (ADK1)            | Stan docelowy (ADK2)                         | Wzorzec z      |
|---------------|-------------------------------|----------------------------------------------|----------------|
| Module 23     | Dispatcher + 9 flat tools     | Dynamic Graph (profiler → nodes → aggregator)| Module 27 + 30 |
| Module 24     | Linear async functions        | HITL Pipeline (plan → approve → exec → report)| Module 28 + 26 |

---

## Część 1: Upgrade Module 23 (AI Code Concierge)

### Obecna architektura (ADK1)

```
User → ai_code_concierge (LlmAgent)
          ↓ decyduje (LLM routing)
    [tools.py — 9 narzędzi zawsze załadowanych]:
      code_review_pr()      → auggie_run(str)   ← plain string return
      on_demand_audit()     → auggie_run(str)
      generate_implementation() → auggie_run(str)
      refactor_workflow()   → auggie_run(str)
      security_audit()      → auggie_run(str)
      analyze_codebase()    → auggie_run(str)
      ask_specialist()      → auggie_run(str)
      auggie_health()       → dict
      auggie_cost_report()  → dict
      auggie_telemetry()    → dict
```

**Problemy ADK1**:
- Wszystkie 9 tools zawsze w kontekście → długi prompt, wyższy koszt
- Wyniki jako `str` → brak structured state, trudna kompozycja
- Brak observability węzłów → debugowanie przez logi konsoli
- Brak retry per tool → jeden błąd = cały agent fails

### Docelowa architektura (ADK2)

```
User → project_intake (LlmAgent, output_key="intake_request")
         ↓
       DynamicOrchestratorAgent
         → code_review_agent     (jeśli diff/PR w request)
         → audit_agent           (jeśli audit request)
         → implementation_agent  (jeśli generacja kodu)
         → refactor_agent        (jeśli refactor request)
         → security_agent        (jeśli security scope)
         (tylko węzły potrzebne dla danego requestu)
         ↓
       concierge_aggregator (LlmAgent, output_key="final_response")
```

### Plan migracji Module 23

#### Krok 1: Structured return types dla tools
```python
# PRZED (tools.py):
def code_review_pr(diff: str, ...) -> str:
    return auggie_run(..., return_type=str)  # plain string

# PO (tools.py ADK2):
def code_review_pr(diff: str, ...) -> dict:
    return {
        "findings": [...],
        "severity": "high|medium|low|none",
        "suggestions": [...],
        "auggie_cost_usd": 0.04,
    }
```

#### Krok 2: Osobny LlmAgent per capability
```python
# Każde z 9 tools staje się OSOBNYM węzłem grafu:
code_review_node = LlmAgent(
    name="code_review_node",
    tools=[FunctionTool(func=code_review_pr)],
    output_key="code_review_result",
    instruction="...",
)
# Węzeł uruchamiany TYLKO gdy request dotyczy code review
```

#### Krok 3: Dynamic Orchestrator (Module 30 pattern)
```python
class CodeConciergeOrchestrator(BaseAgent):
    async def _run_async_impl(self, ctx):
        request = ctx.session.state.get("intake_request", {})
        nodes = []
        if request.get("has_diff"):
            nodes.append(code_review_node)
        if request.get("is_security"):
            nodes.append(security_node)
        # ... buduj graf na podstawie requestu
        for node in nodes:
            async for event in node.run_async(ctx):
                yield event
```

#### Krok 4: Migracja pliku po pliku

| Plik (Module 23)              | Akcja migracji                              |
|-------------------------------|---------------------------------------------|
| `agent.py`                    | Zastąp `LlmAgent` + `DynamicOrchestrator`   |
| `tools.py`                    | Zmień return type: `str` → `dict`           |
| `auggie_factory.py`           | Bez zmian (kompatybilna warstwa)            |
| `__init__.py`                 | Zaktualizuj eksporty (dodaj `root_agent`)   |

---

## Część 2: Upgrade Module 24 (AuditOps)

### Obecna architektura (ADK1)

```python
# pentest_agent.py — linear async functions:
async def auto_pentest(target_url, ack):
    runtime_guard(target_url, cfg, ack)  # guard clause
    recon = await passive_recon(target_url)
    plan  = await _call_planner(recon, skills)
    result = await run_scenario(plan, ...)
    report = _build_report(result)
    return report
```

**Problemy ADK1**:
- `runtime_guard()` jako guard clause → brak prawdziwego HITL (nie czeka na input)
- Liniowy flow → brak conditional routing (np. "jeśli HIGH severity → eskaluj")
- Brak session.state → wyniki nie persystowane między krokami
- Trudne do rozszerzenia → dodanie nowego kroku = modyfikacja funkcji

### Docelowa architektura (ADK2)

```
User → recon_agent (LlmAgent, output_key="recon_result")
         ↓
       planning_agent (LlmAgent, output_key="pentest_plan")
         ↓
       HumanApprovalAgent (BaseAgent/HITL)  ← Module 28 pattern
         ↓ APPROVE / REJECT
       ConditionalRouterAgent (BaseAgent)   ← Module 26 pattern
         ↓ APPROVE              ↓ REJECT
       execution_agent       abort_agent
         ↓
       SeverityRouterAgent                  ← Module 26 pattern
         ↓ CRITICAL              ↓ LOW/MED
       escalation_agent     report_agent
```

### Plan migracji Module 24

#### Krok 1: Przenieś `DisclaimerAck` → HITL węzeł
```python
# PRZED (safety.py):
def runtime_guard(target_url, cfg, ack):
    if not ack or not ack.confirmed:
        raise RuntimeError("Disclaimer must be acknowledged")

# PO (agent.py ADK2) — Module 28 pattern:
HumanApprovalAgent()  # Węzeł grafu który CZEKA na decyzję
# Zaleta: audit log, timeout, multi-level approval, Slack integration
```

#### Krok 2: Zbuduj SequentialAgent pipeline
```python
root_agent = SequentialAgent(
    name="audit_ops_v2",
    sub_agents=[
        ReconAgent(),              # passive_recon() jako węzeł
        PlanningAgent(),           # _call_planner() jako węzeł
        HumanApprovalAgent(),      # HITL zamiast runtime_guard()
        ConditionalRouterAgent(),  # APPROVE → exec, REJECT → abort
        ReportingAgent(),          # _build_report() jako węzeł
    ]
)
```

#### Krok 3: Każda faza jako `output_key` w state
```python
# Zamiast return values przekazywanych przez parametry:
recon_agent      → output_key="recon_result"
planning_agent   → output_key="pentest_plan"
execution_agent  → output_key="execution_result"
# Każdy węzeł czyta z {poprzedni_klucz} w instruction
```

#### Krok 4: Severity-based conditional routing (Module 26)
```python
class SeverityRouterAgent(BaseAgent):
    async def _run_async_impl(self, ctx):
        result = ctx.session.state.get("execution_result", {})
        severity = result.get("max_severity", "low")
        if severity == "critical":
            async for e in self.escalation_agent.run_async(ctx): yield e
        else:
            async for e in self.report_agent.run_async(ctx): yield e
```

#### Krok 5: Migracja pliku po pliku

| Plik (Module 24)              | Akcja migracji                              |
|-------------------------------|---------------------------------------------|
| `pentest_agent.py`            | Zastąp functions → `SequentialAgent` nodes  |
| `safety.py`                   | `runtime_guard()` → `HumanApprovalAgent`    |
| `playwright_runner.py`        | Bez zmian (wywołanie jako `FunctionTool`)   |
| `recon.py`                    | Bez zmian (wywołanie jako `FunctionTool`)   |
| `config.py`                   | Dodaj pola dla ADK2 state management        |
| `__init__.py`                 | Zaktualizuj eksport `root_agent`            |

---

## Matryca wzorców: Moduły 25-30 vs. docelowe zmiany

| Wzorzec ADK2            | Moduł źródłowy | Zastosowanie w M23      | Zastosowanie w M24      |
|-------------------------|----------------|-------------------------|-------------------------|
| SequentialAgent pipeline| Module 25      | Intake→Nodes→Aggregator | Recon→Plan→Exec→Report  |
| Conditional routing     | Module 26      | Routing per request type| Approve/Reject + Severity|
| output_key + state      | Module 27      | Tools: str→dict         | Każda faza w state      |
| HITL checkpoint         | Module 28      | (opcjonalne high-cost)  | Zastępuje runtime_guard |
| Parallel specialists    | Module 29      | Równoległa analiza kodu | (nie dotyczy)           |
| Dynamic graph           | Module 30      | Węzły per request type  | (nie dotyczy)           |

---

## Kolejność migracji (zalecana)

```
Tydzień 1: Module 27 — Structured State
  ✓ Zmień return types w tools.py (str → dict)
  ✓ Dodaj output_key do istniejących agentów
  ✓ Sprawdź że testy przechodzą

Tydzień 2: Module 26 — Conditional Routing
  ✓ Zbuduj ConditionalRouterAgent dla Module 24
  ✓ Zastąp if/else w pentest_agent.py routerami

Tydzień 3: Module 28 — HITL
  ✓ Zastąp runtime_guard() → HumanApprovalAgent
  ✓ Przetestuj ścieżkę APPROVE i REJECT

Tydzień 4: Module 30 — Dynamic Graph (Module 23)
  ✓ Zbuduj CodeConciergeOrchestrator
  ✓ Zamień 9 flat tools na dynamiczne węzły grafu

Tydzień 5: Integracja i testy E2E
  ✓ Testy regresji (stare scenariusze nadal działają)
  ✓ Porównanie kosztów (przed/po)
  ✓ ADK Web UI observability check
```

---

## Kryteria sukcesu

```
[ ] Wszystkie istniejące testy przechodzą po migracji
[ ] Koszt tokenów <= koszt przed migracją (dynamizm powinien obniżać)
[ ] ADK Web UI pokazuje structured state po każdym węźle
[ ] HITL w Module 24 loguje każdą decyzję (kto, kiedy, dlaczego)
[ ] Każdy węzeł testowalny w izolacji (bez uruchamiania całego grafu)
[ ] Czas odpowiedzi <= 2x obecny (parallel agents dla Module 29)
```

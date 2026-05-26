# ARCHITECTURE — Module 30: ADK 2.0 Dynamic Graphs

> **Cel modułu**: Budowanie grafów agentów w czasie wykonania (runtime),
> gdzie liczba i rodzaj węzłów zależy od danych wejściowych i stanu sesji.
> Adaptacja struktury zamiast statycznych, "one-size-fits-all" pipeline'ów.

---

## Koncepcja: Statyczny vs. Dynamiczny Graf

```
STATYCZNY GRAF (Module 25-29):
  [A] → [B] → [C] → [D]
  Zawsze te same węzły, zawsze ta sama kolejność.
  Problem: Mały projekt płaci koszt wszystkich węzłów.

DYNAMICZNY GRAF (Module 30):
  [Profiler] → [Orchestrator] → [Aggregator]
                     ↓
                Buduje w runtime:
  SMALL/LOW  → [quality]
  MEDIUM     → [quality] → [security] → [dependencies]
  LARGE/CRIT → [quality] → [security] → [performance] → [dependencies]

  Zaleta: koszt proporcjonalny do złożoności projektu.
```

---

## Diagram przepływu

```
USER: "Przeanalizuj mój mały projekt Django (< 1k LOC, brak danych wrażliwych)"
              │
              ▼
    ┌─────────────────────┐
    │   project_profiler  │  output_key="project_profile"
    │   (LlmAgent)        │  → {size: "small", risk_level: "low", ...}
    └─────────┬───────────┘
              │
              ▼
    ┌─────────────────────────────────────────────────────┐
    │         DynamicOrchestratorAgent (BaseAgent)        │
    │                                                     │
    │  1. Odczyt project_profile ze state                 │
    │  2. build_agent_list("small", "low", [...])         │
    │     → [quality_analyzer]  ← tylko 1 węzeł!         │
    │  3. Uruchom węzły sekwencyjnie                      │
    │                                                     │
    │  state["dynamic_graph_info"] = {                    │
    │    "node_count": 1,                                 │
    │    "nodes": ["quality_analyzer"],                   │
    │    "built_at_runtime": true                         │
    │  }                                                  │
    └─────────┬───────────────────────────────────────────┘
              │
              ▼
    ┌─────────────────────┐
    │  dynamic_aggregator │  Czyta dostępne klucze ze state
    │  (LlmAgent)         │  (puste klucze pomija gracefully)
    └─────────────────────┘
```

---

## Agent Factory Pattern

```python
# Zamiast definiować 4 osobne agenty statycznie...
# GENERUJEMY węzły na podstawie parametrów:

def build_analysis_agent(focus: str, severity_threshold: str) -> LlmAgent:
    """Factory tworząca węzeł analizy o danym focus i progu severity."""
    return LlmAgent(
        name=f"{focus}_analyzer",
        instruction=FOCUS_TEMPLATES[focus].format(threshold=severity_threshold),
        output_key=f"{focus}_analysis",
        ...
    )

def build_agent_list(size, risk, integrations) -> list[LlmAgent]:
    """Logika biznesowa: które węzły uruchomić."""
    if risk == "critical" or size == "large":
        focuses = ["quality", "security", "performance", "dependencies"]
    elif risk == "high" or size == "medium":
        focuses = ["quality", "security", "dependencies"]
    else:
        focuses = ["quality"]
    return [build_analysis_agent(f, threshold) for f in focuses]
```

---

## Zaawansowane wzorce dynamizmu

### Pattern 1: Runtime sub_agents (ten moduł)
```python
class DynamicOrchestratorAgent(BaseAgent):
    async def _run_async_impl(self, ctx):
        agents = build_agent_list(...)  # logika biznesowa
        for agent in agents:
            async for event in agent.run_async(ctx):
                yield event
```

### Pattern 2: LoopAgent z dynamicznym warunkiem stopu
```python
# Zamiast fixed max_iterations — LLM decyduje kiedy skończyć
class AdaptiveLoopAgent(BaseAgent):
    async def _run_async_impl(self, ctx):
        while ctx.session.state.get("analysis_complete") != True:
            async for event in self.analysis_node.run_async(ctx):
                yield event
            # LLM w analysis_node ustawia analysis_complete = True gdy pewny
```

### Pattern 3: Warunkowe gałęzie (kombinacja z Module 26)
```python
# Dynamiczny graf + conditional routing
agents = build_agent_list(...)
if ctx.session.state.get("requires_hitl"):
    agents.insert(-1, HumanApprovalAgent())  # HITL między ostatnim a aggregatorem
```

### Pattern 4: Agent Discovery (zaawansowany)
```python
# Agenty "rejestrują się" w katalogu — orchestrator wybiera najlepsze
available_agents = await discover_agents(registry="https://agent-hub.internal/")
selected = rank_agents(available_agents, task_profile)
```

---

## Porównanie z Module 23 i 24

| Aspekt                   | Module 23 (ADK1)          | Module 24 (ADK1)         | Module 30 (ADK2)              |
|--------------------------|---------------------------|--------------------------|-------------------------------|
| Struktura                | 1 dispatcher + 9 tools    | linear async functions   | Profiler → Dynamic → Aggregat |
| Adaptacja do inputu      | Brak (zawsze wszystkie)   | Brak (fixed flow)        | Tak (1-4 węzły w zależności)  |
| Koszt tokenów            | Stały, niezależnie od rozm| Stały                    | Proporcjonalny do złożoności  |
| Testowalność węzłów      | Trudna (monolith)         | Możliwa (async fn)       | Każdy węzeł testowany osobno  |
| Czas wykonania           | Długi (wszystkie tools)   | Stały                    | Krótki dla małych projektów   |
| Debugowanie              | Trudne                    | Średnie                  | ADK Web UI → dynamic_graph_info|

---

## Strategia upgrade Module 23 → Dynamic Graph

```
OBECNY MODULE 23:
  ai_code_concierge (LlmAgent)
    tools: [code_review_pr, on_demand_audit, summarize_discussion, ...]  ← 9 tools zawsze

UPGRADE DO DYNAMIC GRAPH:
  project_profiler
    ↓
  DynamicOrchestratorAgent
    → code_review_agent  (jeśli diff w request)
    → audit_agent        (jeśli target_url w request)
    → discussion_agent   (jeśli thread_id w request)
    → (tylko te węzły które są potrzebne!)
    ↓
  aggregator
```

---

## TODO — zadania dla dewelopera

```
[ ] Uruchom z "małym projektem" i obserwuj dynamic_graph_info → 1 węzeł
[ ] Uruchom z "krytycznym projektem" i obserwuj → 4 węzły
[ ] Dodaj integrację: jeśli "auggie_sdk" w available_integrations → dodaj auggie_agent
[ ] Dodaj integrację: jeśli "playwright" w integrations → dodaj pentest_agent (Module 24)
[ ] Zaimplementuj Agent Discovery: czytaj dostępne węzły z pliku config.yaml
[ ] Dodaj cache: jeśli ten sam projekt był skanowany < 1h temu → incremental scan
[ ] Zmierz koszt tokenów: SMALL (1 węzeł) vs. LARGE (4 węzły) — czy savings są realne?
[ ] Napisz test parametryczny: build_agent_list() dla każdej kombinacji size+risk
[ ] Dodaj pattern: jeśli security_analysis.severity == "critical" → wstaw HITL węzeł
[ ] Zintegruj z A2A: każdy węzeł jako zewnętrzny mikroserwis (Module 29 pattern)
```

---

## Dokumentacja ADK 2.0

- [BaseAgent Custom Implementation](https://google.github.io/adk-docs/agents/custom-agents/)
- [Dynamic Agent Graphs](https://adk.dev/2.0/)
- [LoopAgent](https://google.github.io/adk-docs/agents/workflow-agents/loop-agents/)
- [Agent Factory Pattern](https://google.github.io/adk-docs/patterns/agent-factory/)

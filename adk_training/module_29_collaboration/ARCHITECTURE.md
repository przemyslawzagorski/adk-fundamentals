# ARCHITECTURE — Module 29: ADK 2.0 Collaborative Agents

> **Cel modułu**: Orchestracja współpracy wielu agentów w ramach jednego grafu.
> Jeden koordynator + wielu specjalistów = lepsza separacja odpowiedzialności.

---

## Architektura "Hub & Spoke" (Koordynator + Specjaliści)

```
USER: "Przeanalizuj bezpieczeństwo mojego projektu Django"
              │
              ▼
┌─────────────────────────────┐
│  security_suite_coordinator  │  ← "Brain": rozumie intencję, planuje
│  (LlmAgent, model=PRO)       │    output_key="coordinator_plan"
└──────────────┬──────────────┘
               │ Ustawia: specialist_task, project_context
               │
               ▼
┌──────────────────────────────────────────────────────────────┐
│              ParallelAgent (równoległa praca)                  │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────┐  │
│  │code_quality_spec.│ │security_specialist│ │dependency_sp.│  │
│  │(LlmAgent+Tool)   │ │(LlmAgent+Tool)   │ │(LlmAgent+Tool│  │
│  │analyze_code_qual │ │run_security_scan  │ │fetch_dep_info│  │
│  │output_key=       │ │output_key=        │ │output_key=   │  │
│  │code_quality_rpt  │ │security_report    │ │dep_report    │  │
│  └──────────────────┘ └──────────────────┘ └──────────────┘  │
└────────────────────────────────────────────────────────────── ┘
               │ (wszystkie 3 kończą równolegle)
               ▼
┌─────────────────────────────┐
│     results_aggregator       │  ← Czyta 3 output_keys ze state
│     (LlmAgent)               │    Generuje Executive Summary
│     output_key=aggregated    │
└─────────────────────────────┘
```

---

## Wzorce Collaboration w ADK 2.0

### Pattern 1: Hub & Spoke (ten moduł)
```python
# Koordynator z sub_agents jako "rąk"
coordinator = LlmAgent(
    sub_agents=[specialist_a, specialist_b, specialist_c]
)
# LLM koordynatora decyduje KTÓRY specialist wywołać i KIEDY
```

### Pattern 2: Pipeline z Handoffs (Module 25-style)
```python
# Każdy agent "przekazuje pałeczkę" następnemu przez output_key
SequentialAgent(sub_agents=[analyst, planner, executor, reporter])
```

### Pattern 3: Parallel Collaboration (ten moduł)
```python
# Specjaliści pracują JEDNOCZEŚNIE → oszczędność czasu
ParallelAgent(sub_agents=[security_spec, quality_spec, dependency_spec])
# czas = max(t_security, t_quality, t_dependency) zamiast sum
```

### Pattern 4: A2A Protocol (zaawansowany)
```python
# Specialist jako ZEWNĘTRZNY MIKROSERWIS — komunikacja przez A2A
from google.adk.a2a import A2AAgent
remote_security_agent = A2AAgent(endpoint="https://security-service/agent")
coordinator = LlmAgent(sub_agents=[remote_security_agent])
```

---

## Dlaczego Collaboration > One Big Agent?

| Cecha                    | Jeden duży LlmAgent          | Collaborative Agents           |
|--------------------------|------------------------------|--------------------------------|
| Długość kontekstu        | Jeden kontekst z WSZYSTKIM   | Każdy spec ma swój fokus       |
| Specjalizacja LLM        | Jeden model do wszystkiego   | Różne modele dla różnych zadań |
| Testowalność             | Testuj całość razem           | Testuj każdy spec. osobno      |
| Skalowanie               | Jeden duży agent = bottleneck | Spec-y mogą być A2A services  |
| Retry przy błędzie       | Restart całości               | Tylko failing specialist       |
| Koszt tokenów            | Długi prompt dla 1 modelu     | Krótkie prompty per specialist |

---

## Łączenie Module 23 + 24 w Collaboration

```
Module 23: ai_code_concierge (LlmAgent dispatcher)
              → 9 tools wszystko razem

Module 24: pentest_agent (async functions)
              → auto_pentest / guided_pentest

Module 29 (ADK 2.0 Collaboration):
              → security_suite_coordinator
                    → code_quality_specialist (Module 23 tools)
                    → security_specialist (Module 24 tools)
                    → dependency_specialist (OSV API)
              → results_aggregator
```

**Różnica**: w Module 29 każdy specialist może być **oddzielnym serwisem A2A**
hostowanym niezależnie — koordynator nie musi znać ich implementacji.

---

## Testowanie Collaborative Agents

```python
# test_collaboration.py — testuj każdego specialist osobno
import pytest
from unittest.mock import patch

@pytest.mark.asyncio
async def test_security_specialist_in_isolation():
    """Testujemy security_specialist bez koordynatora i innych specjalistów."""
    from adk_training.module_29_collaboration.agent import security_specialist

    ctx = MockInvocationContext(state={
        "specialist_task": "scan https://httpbin.org",
        "project_context": "Django REST API, produkcja"
    })

    with patch("adk_training.module_29_collaboration.agent.run_security_scan") as mock:
        mock.return_value = {"findings": [], "severity": "none"}
        # Test specialist w izolacji — bez uruchamiania koordynatora
        result = await run_agent(security_specialist, ctx)
        assert "security_report" in ctx.session.state
```

---

## TODO — zadania dla dewelopera

```
[ ] Uruchom: adk run adk_training/module_29_collaboration --message "Przeanalizuj projekt Django"
[ ] Obserwuj w ADK Web UI jak parallel_specialists pracują równolegle (zakładka Events)
[ ] Zintegruj code_quality_specialist z Module 23 auggie_factory.auggie_run()
[ ] Zintegruj security_specialist z Module 24 auto_pentest()
[ ] Dodaj 4. specialist: performance_specialist (profiling, N+1 queries)
[ ] Wyeksponuj security_specialist jako A2A service (adk serve)
[ ] Porównaj czas wykonania: parallel vs. sequential dla 3 specjalistów
[ ] Napisz test dla każdego specialist w izolacji (bez API calls)
[ ] Dodaj cross-cutting concern: jeśli security_specialist znajdzie CRITICAL → pomiń code_quality
[ ] Stwórz "specialist registry" — koordynator dynamicznie wybiera specjalistów
```

---

## Dokumentacja ADK 2.0

- [Multi-agent Systems](https://google.github.io/adk-docs/agents/multi-agents/)
- [Collaborative Agents (ADK 2.0)](https://adk.dev/2.0/)
- [A2A Protocol](https://google.github.io/adk-docs/a2a-protocol/)
- [Agent Routing](https://google.github.io/adk-docs/agents/agent-routing/)

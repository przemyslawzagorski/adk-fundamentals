# ARCHITECTURE — Module 26: ADK 2.0 Graph Routes

> **Cel modułu**: Implementacja deterministycznej logiki sterowania w grafie agentów.
> Zamiast "LLM decyduje dokąd iść" — **Python decyduje dokąd iść**.

---

## Kluczowa różnica: Routing przez LLM vs. Routing przez kod

### ADK1 — routing przez LLM (niedeterministyczny)

```python
# ADK1: agent coordinator z sub_agents — LLM decyduje który sub-agent wywołać
root_agent = LlmAgent(
    name="pentest_coordinator",
    sub_agents=[fast_scan, deep_scan],  # LLM wybiera na podstawie description
    instruction="Jeśli risk jest HIGH, użyj deep_scan, w przeciwnym razie fast_scan"
    # Problem: LLM może zignorować instrukcję, hallucynować, wybrać losowo
)
```

### ADK2 — routing przez kod (deterministyczny)

```python
# ADK2: CustomAgent z deterministyczną logiką
class AuditRouterAgent(BaseAgent):
    async def _run_async_impl(self, ctx):
        risk = ctx.session.state.get("risk_level", "MEDIUM")
        if risk == "HIGH":
            async for event in self.deep_scan_agent.run_async(ctx):
                yield event
        else:
            async for event in self.fast_scan_agent.run_async(ctx):
                yield event
```

**Wynik**: 100% przewidywalne, testowalne jednostkowo, bez zależności od LLM w punkcie routingu.

---

## Diagram grafu

```
                    ┌──────────────────┐
USER: "Scan https://target.com"        │
                    │  risk_assessment  │
                    │  (LlmAgent)       │
                    │  output_key=      │
                    │  risk_assessment  │
                    └────────┬─────────┘
                             │
                    session.state["risk_level"] = "HIGH" | "MEDIUM" | "LOW"
                    session.state["target_unreachable"] = True | False
                             │
                    ┌────────▼─────────┐
                    │  AuditRouterAgent │  ← BaseAgent z logiką Python
                    │  (Graph Router)   │
                    └────────┬─────────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
    risk==HIGH         risk==LOW/MED    unreachable==True
           │                 │                 │
    ┌──────▼──────┐  ┌───────▼──────┐  ┌──────▼──────────┐
    │ deep_scan   │  │ fast_scan    │  │ error_handler   │
    │ (LlmAgent)  │  │ (LlmAgent)  │  │ (LlmAgent)      │
    │ OWASP Top10 │  │ Basic checks│  │ Diagnostic rpt  │
    └──────┬──────┘  └──────┬───────┘  └──────┬──────────┘
           │                │                 │
           └────────────────┴─────────────────┘
                            │ output_key="scan_result"
                    ┌───────▼──────────┐
                    │  audit_reporter  │
                    │  (LlmAgent)      │
                    │  Finalny raport  │
                    └──────────────────┘
```

---

## Związek z Module 24 (AuditOps)

Module 24 implementuje `auto_pentest` i `guided_pentest` jako dwie osobne funkcje async.
W ADK 2.0, ta logika staje się **węzłami grafu**:

| Module 24 (ADK1-style)           | Module 26 (ADK2)                          |
|----------------------------------|-------------------------------------------|
| `if guided: _llm_translate_scenario()` | `GuidedTranslatorAgent` (węzeł grafu) |
| `auto_pentest()` vs `guided_pentest()` | `AuditRouterAgent` (deterministyczny) |
| `_execute_scenarios()` w pętli for     | `LoopAgent` + `playwright_runner` tool|
| `reporter.generate_report()`          | `audit_reporter` (LlmAgent węzeł)    |

**Korzyść**: każdy węzeł można przetestować z `MockInvocationContext` bez uruchamiania
całego pipeline'u. W Module 24 trzeba było mockować cały stack.

---

## Testowanie routera (bez LLM!)

```python
# test_audit_router.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from adk_training.module_26_graph_routes.agent import AuditRouterAgent

@pytest.mark.asyncio
@pytest.mark.parametrize("risk,expected_agent", [
    ("HIGH",   "deep_scan"),
    ("MEDIUM", "fast_scan"),
    ("LOW",    "fast_scan"),
])
async def test_router_selects_correct_path(risk, expected_agent):
    """Router NIGDY nie wywołuje LLM — można testować bez klucza API."""
    router = AuditRouterAgent()
    ctx = MagicMock()
    ctx.session.state = {"risk_level": risk, "target_url": "http://test.local"}

    called_agents = []
    # Monkey-patch sub-agents
    for sub in router.sub_agents:
        original_run = sub.run_async
        async def patched(c, name=sub.name):
            called_agents.append(name)
            return; yield  # empty async generator
        sub.run_async = patched

    async for _ in router._run_async_impl(ctx):
        pass

    assert expected_agent in called_agents, f"Expected {expected_agent}, got {called_agents}"
```

---

## TODO — zadania dla dewelopera

```
[ ] Uruchom: adk run adk_training/module_26_graph_routes --message "Scan https://httpbin.org"
[ ] W session.state ręcznie ustaw risk_level="HIGH" i obserwuj ścieżkę deep_scan
[ ] Napisz test_audit_router.py wg schematu powyżej (bez API key!)
[ ] Dodaj 4. gałąź: CRITICAL → natychmiastowy alert + blokada (nie wykonuj skanu)
[ ] Zintegruj playwright_runner z Module 24 jako tool w deep_scan_agent
[ ] Dodaj timing do każdego węzła (callback before_agent / after_agent)
[ ] Porównaj czytelność z Module 24 pentest_agent.py (auto/guided) — który jest łatwiejszy do maintainowania?
```

---

## Dokumentacja ADK 2.0

- [Custom Agents (BaseAgent)](https://google.github.io/adk-docs/agents/custom-agents/)
- [ADK 2.0 Graph Routes](https://adk.dev/2.0/)
- [Session State](https://google.github.io/adk-docs/components/sessions/)

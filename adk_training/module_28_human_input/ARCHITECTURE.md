# ARCHITECTURE — Module 28: ADK 2.0 Human Input (HITL)

> **Cel modułu**: Integracja mechanizmów Human-in-the-Loop wewnątrz workflow.
> Zatrzymanie pipeline'u, oczekiwanie na ludzką decyzję, kontynuacja lub przerwanie.

---

## Dlaczego HITL jest krytyczny w systemach produkcyjnych?

| Scenariusz                    | Bez HITL                              | Z HITL                              |
|-------------------------------|---------------------------------------|-------------------------------------|
| Deploy na produkcję           | Agent deployuje automatycznie         | Człowiek zatwierdza przed deployem  |
| Pentest na live system        | Może uszkodzić produkcję              | Wymagana jawna zgoda seniora        |
| Usunięcie danych (GDPR)       | Agent kasuje automatycznie            | Compliance wymaga zatwierdzenia     |
| Przelew bankowy               | Transakcja bez potwierdzenia          | 2FA + ludzkie zatwierdzenie         |
| LLM o niskiej pewności        | Zgaduje i działa                      | Eskaluje do człowieka               |

---

## Diagram przepływu HITL

```
USER: "Uruchom pentest na https://staging.myapp.com"
              │
              ▼
    ┌─────────────────────┐
    │   pentest_planner   │
    │   (LlmAgent)        │
    │   output_key=       │
    │   pentest_plan      │
    └──────────┬──────────┘
               │
               ▼
    ┌─────────────────────┐
    │  HumanApprovalAgent │  ◄── PUNKT ZATRZYMANIA
    │  (BaseAgent/HITL)   │      Pipeline CZEKA tutaj
    │                     │      do momentu decyzji
    │  Emituje:           │
    │  "human_input_req"  │
    └──────────┬──────────┘
               │
    session.state["human_decision"] = "APPROVE" | "REJECT"
               │
    ┌──────────▼──────────┐
    │   HITLRouterAgent   │  ← Deterministyczny routing
    │   (BaseAgent)       │    (nie LLM)
    └──────────┬──────────┘
               │
    ┌──────────┴──────────┐
    │                     │
    APPROVE               REJECT
    │                     │
    ▼                     ▼
┌──────────┐         ┌──────────────┐
│execution │         │ abort_agent  │
│_agent    │         │ (LlmAgent)   │
│(LlmAgent)│         │ Dokumentuje  │
└────┬─────┘         │ odrzucenie   │
     │               └──────┬───────┘
     └───────────┬──────────┘
                 ▼
         ┌───────────────┐
         │ final_reporter│
         │  (LlmAgent)   │
         └───────────────┘
```

---

## Mechanizmy HITL w ADK 2.0

### Mechanizm 1: Session State (prosty)
```python
# Pipeline sprawdza state["human_decision"] przed kontynuacją
decision = ctx.session.state.get("human_decision", "PENDING")
if decision == "APPROVE":
    # kontynuuj
elif decision == "REJECT":
    # przerwij
else:
    # zapisz prośbę i zakończ ten run (czekaj na wznowienie)
    ctx.session.state["waiting_for_human"] = True
```

### Mechanizm 2: ADK Interrupt Events (pełna implementacja)
```python
# W pełnej ADK 2.0 implementacji:
from google.adk.events import HumanInputRequiredEvent

async def _run_async_impl(self, ctx):
    yield HumanInputRequiredEvent(
        agent=self,
        message="Zatwierdź plan pentestów",
        options=["APPROVE", "REJECT"],
        context={"plan": ctx.session.state["pentest_plan"]},
    )
    # Runner WSTRZYMUJE się tutaj
    # Po odpowiedzi użytkownika, runner WZNAWIA i state jest zaktualizowany
```

### Mechanizm 3: Action Confirmations (tool level)
```python
# Tool pyta o potwierdzenie przed wykonaniem destrukcyjnej akcji
from google.adk.tools import confirmation_required

@confirmation_required(
    message="Czy na pewno chcesz uruchomić pentest?",
    risk_level="HIGH"
)
def run_pentest(target_url: str) -> str:
    # Wykonuje się TYLKO jeśli użytkownik potwierdził
    ...
```

---

## Związek z Module 24 (AuditOps)

Module 24 używa `DisclaimerAck` i `runtime_guard()` jako guard clause:
```python
# Module 24 safety.py
def runtime_guard(target_url, cfg, ack):
    if not ack or not ack.confirmed:
        raise RuntimeError("Disclaimer must be acknowledged")
```

Module 28 modernizuje to do ADK 2.0 HITL:
```python
# Module 28 — HITL jako węzeł grafu (nie guard clause)
HumanApprovalAgent()  # Zatrzymuje pipeline, czeka, kontynuuje/przerywa
# Korzyść: audit log, timeout handling, multi-level approval, eskalacja
```

---

## Strategie HITL dla różnych kontekstów

| Kontekst                  | Strategia                               | Timeout         |
|---------------------------|------------------------------------------|-----------------|
| Pentest live system       | Mandatory APPROVE przed execute          | 30 min → REJECT |
| Deploy staging             | Auto-approve jeśli testy zielone        | N/A             |
| Koszt > $50               | Alert + ludzkie zatwierdzenie            | 1h → REJECT     |
| LLM confidence < 70%      | Eskalacja, nie blokowanie               | 5 min → proceed |
| GDPR data deletion        | Dual approval (2 osoby)                  | 24h → escalate  |

---

## TODO — zadania dla dewelopera

```
[ ] Uruchom pipeline: adk run adk_training/module_28_human_input
[ ] Ustaw w ADK Web UI: session.state["human_decision"] = "APPROVE" i obserwuj kontynuację
[ ] Ustaw "REJECT" i sprawdź ścieżkę abort_agent
[ ] Zintegruj z Module 24: zastąp DisclaimerAck() przez HumanApprovalAgent węzeł
[ ] Dodaj timeout: jeśli >5min bez decyzji → auto-REJECT z powiadomiem
[ ] Zintegruj Slack webhook: HITL prośba jako wiadomość, odpowiedź przez /approve
[ ] Dodaj dual-approval: wymagane 2 osoby dla CRITICAL severity
[ ] Dodaj audit log: persist każdą decyzję w SQLite (kto, kiedy, co, dlaczego)
[ ] Przetestuj ścieżkę PENDING: czy pipeline poprawnie się zatrzymuje?
```

---

## Dokumentacja ADK 2.0

- [Action Confirmations](https://google.github.io/adk-docs/tools/function-tools/action-confirmations/)
- [Human Input](https://adk.dev/2.0/)
- [Resume Agents](https://google.github.io/adk-docs/running-agents/resume-agents/)

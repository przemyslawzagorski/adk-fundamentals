# Module 05: Human-in-the-Loop - Finalne rozwiązanie (USER-DRIVEN)

**Data aktualizacji:** 2026-03-01
**Wersja:** v2 - User-Driven Approval

## ✅ Co zostało naprawione

Przepisaliśmy przykład na **User-Driven Human-in-the-Loop** gdzie:
- ✅ User ma pełną kontrolę nad procesem
- ✅ User JAWNIE prosi o konsultację z Admirałem (keyword-based)
- ✅ User dostarcza uzasadnienie decyzji
- ✅ Admiral analizuje uzasadnienie i podejmuje decyzję
- ✅ Dodano `before_tool_callback` do walidacji parametrów

## 🎯 Jak to teraz działa

### Architektura:

```
Quartermaster Agent (root_agent)
  ├── Tools:
  │   ├── check_treasury_balance()
  │   ├── request_expenditure()
  │   └── admiral (Agent-as-Tool!) ← KLUCZOWE!
  │
  └── Callbacks:
      ├── before_agent_callback: initialize_treasury_state
      ├── before_model_callback: check_admiral_approval (wykonuje transakcję)
      ├── before_tool_callback: validate_tool_params (NOWY! walidacja)
      └── after_tool_callback: update_state_after_tool

Admiral Agent (as tool)
  ├── Instruction: "Review expenditure requests"
  └── Output Schema: AdmiralDecision (approved/rejected + reason)
```

### Przepływ (USER-DRIVEN):

1. **User:** "Potrzebuję 500 dublonów na armaty"

2. **before_tool_callback** waliduje parametry:
   - amount=500 ✅ (< 10000)
   - purpose="armaty" ✅ (nie puste, >= 3 znaki)

3. **Quartermaster** wywołuje `request_expenditure(500, "armaty")`
   - Tool zwraca: `{"status": "pending_approval"}`
   - `after_tool_callback` ustawia: `state["pending_amount"] = 500`

4. **Quartermaster:** "Ahoj! 500 dublonów to za dużo! Musisz zapytać Admirała.
   Powiedz 'zapytaj admirała' i uzasadnij dlaczego potrzebujemy tych dublonów."

5. **User:** "Zapytaj admirała - potrzebujemy armat bo zbliża się bitwa"

6. **Quartermaster** wykrywa keyword "zapytaj admirała" i wywołuje `admiral` tool

7. **Admiral Agent** (Agent-as-Tool):
   - Otrzymuje pełny context (conversation history, state)
   - Widzi uzasadnienie: "potrzebujemy armat bo zbliża się bitwa"
   - Decyduje: `{"decision": "approved", "reason": "Armaty konieczne dla obrony"}`

8. **`after_tool_callback`** ustawia: `state["admiral_approval"] = "approved"`

9. **`before_model_callback`** sprawdza:
   - `pending_amount = 500` ✅
   - `admiral_approval = "approved"` ✅
   - Wykonuje transakcję: `current_balance -= 500`
   - Czyści state: `pending_amount = 0`
   - Zwraca `None` → LLM może odpowiedzieć

10. **Quartermaster:** "Admirał zatwierdził! Armaty w drodze!"

## 🔑 Kluczowe elementy

### 1. Admiral jako Agent-as-Tool

```python
admiral = LlmAgent(
    name="admiral",
    instruction="Review expenditure requests and approve/reject",
    output_schema=AdmiralDecision  # Structured output!
)

admiral_tool = agent_tool.AgentTool(agent=admiral)
```

**Dlaczego to jest lepsze:**
- ✅ Admiral ma pełny context (widzi całą konwersację)
- ✅ Structured output (Pydantic) zapewnia poprawny format
- ✅ Łatwo zastąpić AI człowiekiem (przez UI)
- ✅ Wzorzec używany w produkcji

### 2. before_tool_callback - Walidacja (NOWY!)

```python
def validate_tool_params(tool_context, tool, args):
    if tool.name == "request_expenditure":
        amount = args.get("amount", 0)
        purpose = args.get("purpose", "").strip()

        # Walidacja 1: Max limit
        if amount > 10000:
            raise ValueError("Za dużo! Max 10000 dublonów!")

        # Walidacja 2: Purpose nie może być pusty
        if not purpose:
            raise ValueError("Musisz podać cel wydatku!")

        # Walidacja 3: Purpose min 3 znaki
        if len(purpose) < 3:
            raise ValueError("Cel wydatku za krótki!")
```

**Pokazuje:** Jak blokować wywołanie narzędzia przez `raise Exception`

### 3. before_model_callback - Wykonanie transakcji

```python
def check_admiral_approval(callback_context, llm_request):
    pending_amount = callback_context.state.get("pending_amount", 0)
    approval_status = callback_context.state.get("admiral_approval")

    # NIE blokuje LLM - pozwala agentowi działać
    # Tylko wykonuje transakcję gdy Admiral zatwierdził
    if approval_status == "approved":
        SHIP_TREASURY["current_balance"] -= pending_amount
        callback_context.state["pending_amount"] = 0
        return None  # Pozwól LLM odpowiedzieć
```

### 4. after_tool_callback - Aktualizacja state

```python
def update_state_after_tool(tool_context, tool, args, tool_response):
    if tool.name == "admiral":
        decision = tool_response.get("decision")
        tool_context.state["admiral_approval"] = decision
```

## 🧪 Testowanie

```bash
cd adk_training/module_05_human_in_loop
adk web
```

**Przykładowa konwersacja (USER-DRIVEN):**
```
User: Potrzebuję 500 dublonów na armaty

Quartermaster: Ahoj! 500 dublonów to za dużo!
Musisz zapytać Admirała. Powiedz 'zapytaj admirała'
i uzasadnij dlaczego potrzebujemy tych dublonów.

User: Zapytaj admirała - potrzebujemy armat bo zbliża się bitwa

Quartermaster: [Calls admiral tool]
Admirał zatwierdził! Armaty w drodze!
Pozostało: 4500 dublonów
```

**Testuj też walidację:**
```
User: Potrzebuję 15000 dublonów na rum
→ before_tool_callback: "Za dużo! Max 10000 dublonów!"

User: Potrzebuję 200 dublonów
→ before_tool_callback: "Musisz podać cel wydatku!"
```

## 🚀 W produkcji

Admiral Agent można zastąpić:

### Opcja 1: UI Approval (Gradio)
```python
def human_approval_ui(request_details):
    # Show approval UI
    # Wait for human click
    return {"decision": user_clicked_approve ? "approved" : "rejected"}
```

### Opcja 2: External Workflow
```python
def workflow_approval(request_details):
    # Send to Jira/ServiceNow
    # Poll for approval status
    return {"decision": workflow_status}
```

### Opcja 3: Hybrid
```python
# AI pre-approves small amounts
# Human approves large amounts
if amount > 1000:
    return human_approval_ui(request_details)
else:
    return admiral_agent.run(request_details)
```

## 📚 Porównanie z innymi podejściami

| Podejście | Przykład | Zalety | Wady |
|-----------|----------|--------|------|
| **Agent-as-Tool** | Ten moduł | ✅ Pełny context<br>✅ Structured output<br>✅ Produkcyjny wzorzec | Wymaga więcej kodu |
| **Keyword detection** | Pierwsza próba | Prosty | ❌ Agent myli prompty<br>❌ Nie produkcyjny |
| **Manual state edit** | Oryginalny | Pokazuje mechanikę | ❌ Wymaga API<br>❌ Nie user-friendly |

## ✅ Podsumowanie

To jest **prawdziwy wzorzec Human-in-the-Loop** używany w produkcji:
- Admiral Agent pełni rolę decision maker (może być AI lub człowiek)
- Agent-as-Tool zapewnia pełny context
- Structured output (Pydantic) zapewnia poprawny format
- Łatwo zastąpić AI prawdziwym człowiekiem przez UI

**Zobacz też:** `adkagents/03-adk-topologies/adk-topologies-07-human-in-the-loop/` - oryginalny przykład tego wzorca


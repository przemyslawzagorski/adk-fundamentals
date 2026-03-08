# Jak działa Human-in-the-Loop w tym przykładzie?

## Kto jest "Human"?

**Admiral Agent** pełni rolę człowieka! W tym przykładzie Admiral jest AI agentem, ale w prawdziwym systemie mógłby być:
- Prawdziwym człowiekiem (manager, analityk)
- Systemem zewnętrznym (approval workflow)
- UI gdzie człowiek klika "Approve" lub "Reject"

## Kluczowa różnica od poprzedniej wersji

❌ **Stara wersja:** Próbowała wykrywać keywords ("approve", "reject") w promptach użytkownika
✅ **Nowa wersja:** Używa **Admiral Agent as Tool** - dedykowany agent podejmuje decyzję

To jest **prawdziwy wzorzec Human-in-the-Loop** używany w produkcji!

## Przepływ działania

### 1. Mały wydatek (≤100 doubloons)
```
User: "I need 50 doubloons for rum"
  ↓
Tool: request_expenditure(50, "rum")
  ↓
Tool zwraca: {"status": "approved"}
  ↓
Agent: "Approved! Here's your 50 doubloons"
```

### 2. Duży wydatek (>100 doubloons) - NOWY WZORZEC

```
User: "I need 500 doubloons for cannons"
  ↓
Quartermaster wywołuje: request_expenditure(500, "cannons")
  ↓
Tool zwraca: {"status": "pending_approval", "amount": 500}
  ↓
after_tool_callback() ustawia: state["pending_amount"] = 500
  ↓
Quartermaster widzi status "pending_approval"
  ↓
Quartermaster wywołuje: admiral tool (Agent-as-Tool!)
  ↓
Admiral Agent otrzymuje context:
  - Conversation history (widzi request na 500 doubloons for cannons)
  - Current state (pending_amount=500)
  ↓
Admiral Agent analizuje i decyduje:
  - "Cannons are necessary for defense" → decision="approved"
  LUB
  - "Too expensive" → decision="rejected", reason="..."
  ↓
Admiral zwraca: {"decision": "approved", "reason": "..."}
  ↓
after_tool_callback() ustawia: state["admiral_approval"] = "approved"
  ↓
Quartermaster próbuje odpowiedzieć...
  ↓
before_model_callback() sprawdza state
  ↓
Widzi: pending_amount=500 AND admiral_approval="approved"
  ↓
Odejmuje od treasury: current_balance -= 500
  ↓
Czyści state: pending_amount=0, admiral_approval=None
  ↓
Pozwala LLM odpowiedzieć
  ↓
Quartermaster: "Aye! The Admiral approved! Cannons on the way!"
```

## Kluczowe mechanizmy

### 1. **Agent-as-Tool** - Admiral jako narzędzie

```python
from google.adk.tools import agent_tool

# Admiral jest osobnym agentem
admiral = LlmAgent(
    name="admiral",
    instruction="Review expenditure requests and approve/reject",
    output_schema=AdmiralDecision  # Structured output!
)

# Wrap jako tool
admiral_tool = agent_tool.AgentTool(agent=admiral)

# Quartermaster używa Admiral jako tool
quartermaster = LlmAgent(
    tools=[check_treasury_balance, request_expenditure, admiral_tool]
)
```

**Dlaczego to jest lepsze:**
- ✅ Admiral ma pełny context (conversation history, state)
- ✅ Admiral może być AI lub prawdziwym człowiekiem (przez UI)
- ✅ Structured output (Pydantic schema) zapewnia poprawny format
- ✅ Nie trzeba parsować keywords z promptów użytkownika

### 2. `before_model_callback` - Bramka przed LLM

```python
def check_admiral_approval(callback_context, llm_request):
    pending_amount = callback_context.state.get("pending_amount", 0)
    approval_status = callback_context.state.get("admiral_approval")

    # Sprawdza czy jest pending request
    if pending_amount > 100 and not approval_status:
        # BLOKUJE LLM - zwraca własną odpowiedź
        return LlmResponse(content="Awaiting Admiral's approval...")

    # Pozwala LLM działać normalnie
    return None
```

**Kluczowe:**
- Zwrócenie `LlmResponse` = BLOKUJE LLM, używa twojej odpowiedzi
- Zwrócenie `None` = pozwala LLM działać normalnie

### 3. `after_tool_callback` - Aktualizacja state

```python
def update_state_after_tool(tool_context, tool, args, tool_response):
    # Gdy Admiral podejmuje decyzję
    if tool.name == "admiral":
        decision = tool_response.get("decision")
        tool_context.state["admiral_approval"] = decision
```

State przechowuje informacje między kolejnymi wiadomościami w konwersacji.

## Dlaczego to jest dobry przykład?

✅ **Pokazuje mechanikę callbacks** - jak blokować LLM  
✅ **Pokazuje state management** - jak przechowywać status między turami  
✅ **Prosty w użyciu** - wystarczy wpisać prompt  
✅ **Realistyczny** - user jest prawdziwym "human" w pętli  

## W produkcji

W prawdziwym systemie zamiast promptów użyłbyś:
- Dedykowanego UI (Gradio, React)
- Systemu notyfikacji (email, Slack)
- Workflow engine (Temporal, Airflow)
- Agent-as-tool pattern (zobacz `adkagents/03-adk-topologies/adk-topologies-07-human-in-the-loop/`)

Ale mechanika (callbacks + state) pozostaje taka sama!


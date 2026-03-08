# Naprawione problemy w Module 05

## Problem 1: Oryginalny przykład

Oryginalny przykład wymagał ręcznej edycji state przez API, co było:
- ❌ Niejasne (brak instrukcji JAK to zrobić)
- ❌ Skomplikowane (wymaga REST API lub Python script)
- ❌ Nie pokazywało prawdziwego Human-in-the-Loop

## Problem 2: Pierwsza próba naprawy (keyword detection)

Próbowaliśmy wykrywać keywords ("approve", "reject") w promptach użytkownika, ale:
- ❌ Agent interpretował "approve" jako nowy request zamiast odpowiedź
- ❌ Nie było jasne kiedy user odpowiada na approval request
- ❌ Nie jest to wzorzec używany w produkcji

## Problem 3: Callback blokował wywołanie narzędzia admiral (NAPRAWIONE 2026-03-01)

`before_model_callback` blokował LLM zanim agent zdążył wywołać narzędzie `admiral`:
- ❌ Agent chciał wywołać `admiral` tool
- ❌ Ale callback zwracał LlmResponse i blokował LLM
- ❌ Agent nigdy nie mógł wywołać narzędzia admiral (Catch-22!)

**FIX v1:** Callback pozwalał LLM działać, agent automatycznie wywoływał admiral.

## Problem 4: Brak prawdziwego Human-in-the-Loop (NAPRAWIONE 2026-03-01)

Poprzednia wersja automatycznie wywoływała admiral tool:
- ❌ User nie miał kontroli nad procesem
- ❌ Wszystko działo się automatycznie
- ❌ Nie było prawdziwego "human in the loop"

**FIX v2 (FINALNE ROZWIĄZANIE - USER-DRIVEN):**
- ✅ Quartermaster INFORMUJE usera że potrzebna zgoda Admirała
- ✅ User JAWNIE prosi o konsultację: "zapytaj admirała - potrzebujemy armat bo bitwa"
- ✅ Quartermaster wykrywa keyword i WTEDY wywołuje admiral tool
- ✅ Admiral widzi uzasadnienie usera w historii konwersacji
- ✅ User ma pełną kontrolę nad procesem!

## Rozwiązanie: Agent-as-Tool Pattern

Używamy **Admiral Agent as Tool** - wzorzec z `adk-topologies-07-human-in-the-loop`.

### Zmiany w kodzie:

1. **Admiral Agent** - osobny agent który podejmuje decyzje:
   ```python
   admiral = LlmAgent(
       name="admiral",
       instruction="Review expenditure requests and approve/reject",
       output_schema=AdmiralDecision  # Structured output!
   )
   ```

2. **Admiral as Tool** - Admiral jest narzędziem dla Quartermaster:
   ```python
   admiral_tool = agent_tool.AgentTool(agent=admiral)
   quartermaster = LlmAgent(tools=[..., admiral_tool])
   ```

3. **Callbacks - PEŁNY ZESTAW:**
   - `before_agent_callback` - Inicjalizacja state przy starcie
   - `before_model_callback` - Wykonuje transakcję gdy Admiral zatwierdził
   - **`before_tool_callback`** - **NOWY!** Waliduje parametry przed wywołaniem narzędzia
   - `after_tool_callback` - Aktualizuje state po wywołaniu narzędzia

4. **`before_tool_callback` - Walidacja biznesowa:**
   ```python
   def validate_tool_params(tool_context, tool, args):
       if tool.name == "request_expenditure":
           amount = args.get("amount", 0)
           if amount > 10000:
               raise ValueError("Za dużo! Max 10000 dublonów!")
           if not args.get("purpose"):
               raise ValueError("Musisz podać cel wydatku!")
   ```
   **Pokazuje:** Jak blokować wywołanie narzędzia przez raise Exception

## Jak teraz działa (FINALNE ROZWIĄZANIE - USER-DRIVEN):

```
User: "Potrzebuję 500 dublonów na armaty"
  ↓
Quartermaster: Wywołuje request_expenditure(500, "armaty")
  ↓
Tool zwraca: {"status": "pending_approval"}
  ↓
after_tool_callback: State zaktualizowany: pending_amount=500
  ↓
Quartermaster: "Ahoj! Ta suma (500 dublonów) przekracza moje uprawnienia!
               Musisz zapytać Admirała o zgodę. Powiedz 'zapytaj admirała'
               i uzasadnij dlaczego potrzebujemy tych dublonów."
  ↓
User: "Zapytaj admirała - potrzebujemy armat bo zbliża się bitwa"
  ↓
Quartermaster: Wykrywa keyword "zapytaj admirała"
  → Wywołuje narzędzie admiral (Agent-as-Tool!)
  ↓
Admiral Agent analizuje:
  - Widzi CAŁĄ historię konwersacji (w tym uzasadnienie usera!)
  - Widzi: "potrzebujemy armat bo zbliża się bitwa"
  - Podejmuje decyzję na podstawie uzasadnienia
  ↓
Admiral zwraca: {"decision": "approved", "reason": "Armaty są konieczne dla obrony"}
  ↓
after_tool_callback: State zaktualizowany: admiral_approval="approved"
  ↓
before_model_callback: Wykrywa admiral_approval="approved"
  → Wykonuje transakcję (odejmuje 500 od balansu)
  → Pozwala LLM wygenerować odpowiedź
  ↓
Quartermaster: "Admirał zatwierdził! Armaty w drodze!"
```

**KLUCZOWA RÓŻNICA:**
- ❌ Stara wersja: Quartermaster AUTOMATYCZNIE wywoływał admiral
- ✅ Nowa wersja: User JAWNIE prosi o konsultację z Admirałem
- ✅ User ma pełną kontrolę (prawdziwy Human-in-the-Loop!)

## Testowanie:

```bash
cd adk_training/module_05_human_in_loop
adk web
```

**Konwersacja:**
1. `I need 500 doubloons for cannons`
2. Quartermaster automatycznie konsultuje się z Admiral
3. Admiral podejmuje decyzję (AI w tym przykładzie)
4. Quartermaster informuje o wyniku

## Kluczowe wnioski:

✅ **Admiral Agent** pełni rolę "human" (może być AI lub prawdziwy człowiek)
✅ **Agent-as-Tool** - wzorzec używany w produkcji
✅ **Structured output** - Pydantic schema zapewnia poprawny format
✅ **Pełny context** - Admiral widzi całą konwersację
✅ **Łatwo zastąpić AI człowiekiem** - wystarczy zmienić Admiral na UI approval

## W produkcji:

Admiral Agent można zastąpić:
- **UI approval** - Gradio interface gdzie człowiek klika "Approve"/"Reject"
- **External system** - integracja z workflow (Jira, ServiceNow)
- **Hybrid** - AI pre-approves, człowiek tylko dla dużych kwot


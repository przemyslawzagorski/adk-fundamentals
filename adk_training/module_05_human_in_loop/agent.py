"""
Moduł 05: Agent Human-in-the-Loop (USER-DRIVEN)
================================================
"Zatwierdzenie Admirała" - Demonstracja bramek zatwierdzania przez człowieka w agentach ADK.

Ten moduł pokazuje jak:
1. Użyć before_model_callback do wykonywania transakcji po zatwierdzeniu
2. Użyć before_tool_callback do walidacji parametrów (NOWY!)
3. Użyć Agent-as-Tool pattern (Admiral jako narzędzie)
4. Zaimplementować USER-DRIVEN workflow (user jawnie prosi o konsultację)
5. Integrować nadzór człowieka w przepływy pracy agenta

Temat: Kwatermistrz zarządza skarbcem, ale każdy wydatek powyżej 100 dublonów
wymaga zatwierdzenia przez Admirała!

KLUCZOWA RÓŻNICA (v2 - USER-DRIVEN):
- User JAWNIE prosi o konsultację: "zapytaj admirała - potrzebujemy armat bo bitwa"
- Quartermaster wykrywa keyword i WTEDY wywołuje admiral tool
- Admiral widzi uzasadnienie usera w historii konwersacji
- User ma pełną kontrolę nad procesem (prawdziwy Human-in-the-Loop!)

Callbacks użyte w tym module:
- before_agent_callback: Inicjalizacja state
- before_model_callback: Wykonanie transakcji po zatwierdzeniu
- before_tool_callback: Walidacja parametrów (amount, purpose)
- after_tool_callback: Aktualizacja state po wywołaniu narzędzia
"""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool
from google.adk.tools import agent_tool
from google.genai import types

# Załaduj zmienne środowiskowe
load_dotenv()

# Konfiguracja modelu
MODEL = "gemini-2.5-flash" # Zmieniono na stabilną wersję 2.0

# Skarbiec (symulowana baza danych)
SHIP_TREASURY = {
    "current_balance": 5000,  # dublony
    "pending_requests": []
}


# ============================================================
# SCHEMAT ZATWIERDZENIA
# ============================================================

class AdmiralDecision(BaseModel):
    """Schemat dla decyzji zatwierdzenia Admirała."""
    decision: str = Field(description="Decyzja Admirała. Musi być 'approved' lub 'rejected'")
    reason: Optional[str] = Field(default=None, description="Opcjonalny powód decyzji")


# ============================================================
# AGENT ADMIRAŁ - Decydent Ludzki
# ============================================================

admiral = LlmAgent(
    model=MODEL,
    name="admiral",
    instruction="""Jesteś Admirałem. Twoją rolą jest przeglądanie dużych wniosków o wydatki od Kwatermistrza.

Przy przeglądaniu wniosku, rozważ:
- Czy kwota jest rozsądna dla podanego celu?
- Czy mamy wystarczająco dublonów w skarbcu?
- Czy ten wydatek jest konieczny dla operacji morskich?

MUSISZ podjąć decyzję: albo 'approved' albo 'rejected'.
Jeśli odrzucasz, podaj krótki powód.

Przykłady:
- 500 dublonów na działa → APPROVED (konieczne dla obrony)
- 1000 dublonów na rum → REJECTED (nadmierne, załoga nie potrzebuje tyle)
- 300 dublonów na naprawy → APPROVED (konserwacja jest krytyczna)
""",
    description="Admirał zatwierdzający lub odrzucający duże wydatki",
    output_schema=AdmiralDecision
)


# ============================================================
# FUNKCJE CALLBACK
# ============================================================

def check_admiral_approval(
    callback_context: CallbackContext,
    llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    Before Model Callback: Wykonuje transakcję gdy Admiral zatwierdził.

    NOWA LOGIKA (USER-DRIVEN):
    - Callback NIE blokuje LLM
    - Callback tylko WYKONUJE transakcję gdy jest approval
    - Agent sam decyduje kiedy wywołać admiral (na podstawie user request)
    """
    agent_name = callback_context.agent_name
    print(f"\n🔍 [Callback] Sprawdzanie statusu zatwierdzenia dla agenta: {agent_name}")

    pending_amount = callback_context.state.get("pending_amount", 0)
    approval_status = callback_context.state.get("admiral_approval")

    # Jeśli nie ma pending request, pozwól LLM działać normalnie
    if pending_amount <= 100:
        return None

    # PRZYPADEK 1: Admirał zatwierdził - WYKONAJ TRANSAKCJĘ
    if approval_status == "approved":
        print(f"✅ [Callback] Admirał zatwierdził wydatek {pending_amount} dublonów!")
        print(f"    → Wykonuję transakcję...")
        SHIP_TREASURY["current_balance"] -= pending_amount
        callback_context.state["treasury_balance"] = SHIP_TREASURY["current_balance"]
        callback_context.state["pending_amount"] = 0
        callback_context.state["admiral_approval"] = None
        return None  # Pozwól LLM wygenerować odpowiedź o zatwierdzeniu

    # PRZYPADEK 2: Admirał odrzucił - WYCZYŚĆ STATE
    elif approval_status == "rejected":
        print(f"❌ [Callback] Admirał odrzucił wydatek!")
        reason = callback_context.state.get("rejection_reason", "nieokreślone powody")
        callback_context.state["pending_amount"] = 0
        callback_context.state["admiral_approval"] = None
        callback_context.state["rejection_reason"] = None
        # Pozwól LLM wygenerować odpowiedź (agent zobaczy decyzję w tool response)
        return None

    # PRZYPADEK 3: Oczekiwanie na user request
    # Pozwól LLM działać - agent poinformuje usera lub wywoła admiral (jeśli user poprosił)
    else:
        print(f"⏳ [Callback] Pending amount: {pending_amount}, oczekiwanie na user request")
        print(f"    → Pozwalam LLM działać normalnie")
        return None


def initialize_treasury_state(callback_context: CallbackContext) -> None:
    """Before Agent Callback: Inicjalizacja stanu przy starcie agenta."""
    print("\n🏦 [Callback] Inicjalizacja stanu skarbca...")
    if "treasury_balance" not in callback_context.state:
        callback_context.state["treasury_balance"] = SHIP_TREASURY["current_balance"]
    if "pending_amount" not in callback_context.state:
        callback_context.state["pending_amount"] = 0
    return None


def validate_tool_params(tool_context, tool, args):
    """
    Before Tool Callback: Walidacja parametrów przed wywołaniem narzędzia.

    Ten callback pokazuje jak można:
    - Walidować parametry biznesowe
    - Blokować wywołanie narzędzia (przez raise Exception)
    - Dodać dodatkowe zabezpieczenia
    """
    if tool.name == "request_expenditure":
        amount = args.get("amount", 0)
        purpose = args.get("purpose", "").strip()

        print(f"\n🔍 [Before Tool] Walidacja request_expenditure:")
        print(f"    Amount: {amount}, Purpose: '{purpose}'")

        # Walidacja 1: Maksymalny limit na pojedynczą transakcję
        MAX_SINGLE_TRANSACTION = 10000
        if amount > MAX_SINGLE_TRANSACTION:
            error_msg = f"🚫 Ahoj! {amount} dublonów to za dużo! Maksymalnie {MAX_SINGLE_TRANSACTION} dublonów na jedną transakcję!"
            print(f"    ❌ BLOKADA: {error_msg}")
            raise ValueError(error_msg)

        # Walidacja 2: Purpose nie może być pusty
        if not purpose:
            error_msg = "🚫 Musisz podać cel wydatku, kamratcie! Na co chcesz wydać te dublony?"
            print(f"    ❌ BLOKADA: {error_msg}")
            raise ValueError(error_msg)

        # Walidacja 3: Purpose musi mieć przynajmniej 3 znaki
        if len(purpose) < 3:
            error_msg = f"🚫 Cel wydatku '{purpose}' jest za krótki! Opisz dokładniej na co potrzebujesz dublonów."
            print(f"    ❌ BLOKADA: {error_msg}")
            raise ValueError(error_msg)

        print(f"    ✅ Walidacja przeszła pomyślnie")

    return None  # Pozwól na wywołanie narzędzia


def update_state_after_tool(tool_context, tool, args, tool_response):
    """After Tool Callback: Aktualizacja stanu na podstawie odpowiedzi narzędzia."""
    if tool.name == "request_expenditure" and isinstance(tool_response, dict):
        if tool_response.get("status") == "pending_approval":
            print(f"📝 [After Tool] Ustawianie stanu oczekiwania dla {tool_response['amount']} dublonów")
            tool_context.state["pending_amount"] = tool_response["amount"]
            tool_context.state["pending_purpose"] = tool_response["purpose"]
        elif tool_response.get("status") == "approved":
            tool_context.state["treasury_balance"] = SHIP_TREASURY["current_balance"]

    elif tool.name == "admiral" and isinstance(tool_response, dict):
        decision = tool_response.get("decision", "").lower()
        print(f"📝 [After Tool] Decyzja Admirała: {decision}")
        tool_context.state["admiral_approval"] = decision
        if decision == "rejected" and "reason" in tool_response:
            tool_context.state["rejection_reason"] = tool_response["reason"]

    return None


# ============================================================
# FUNKCJE NARZĘDZI - Operacje Skarbcowe
# ============================================================

def check_treasury_balance() -> dict:
    """Sprawdź aktualny stan skarbca statku.

    Returns:
        dict: Bieżący balans i status skarbca.
    """
    return {
        "balance": SHIP_TREASURY["current_balance"],
        "currency": "dublony",
        "status": "Skarbiec jest pełen złota, Kapitanie!"
    }


def request_expenditure(amount: int, purpose: str) -> dict:
    """Złóż wniosek o wydatek ze skarbca statku.

    Args:
        amount: Liczba dublonów do wydania.
        purpose: Na co zostaną przeznaczone dublony.

    Returns:
        dict: Wynik wniosku o wydatek.
    """
    if amount <= 0:
        return {"error": "Kamratcie! Nie możesz wydać zera ani ujemnych dublonów!"}

    if amount > SHIP_TREASURY["current_balance"]:
        return {
            "error": f"Mało złota! W skarbcu jest {SHIP_TREASURY['current_balance']}, "
                     f"a Ty prosisz o {amount}."
        }

    if amount <= 100:
        SHIP_TREASURY["current_balance"] -= amount
        return {
            "status": "approved",
            "amount": amount,
            "purpose": purpose,
            "remaining_balance": SHIP_TREASURY["current_balance"],
            "message": f"Wydatek {amount} dublonów zatwierdzony! Wydaj je mądrze!"
        }
    else:
        return {
            "status": "pending_approval",
            "amount": amount,
            "purpose": purpose,
            "message": f"Wydatek {amount} dublonów wymaga zatwierdzenia przez Admirała!"
        }


# ============================================================
# ADMIRAŁ JAKO NARZĘDZIE
# ============================================================

admiral_tool = agent_tool.AgentTool(agent=admiral)


# ============================================================
# AGENT GŁÓWNY - Kwatermistrz z nadzorem
# ============================================================

root_agent = LlmAgent(
    model=MODEL,
    name="quartermaster",
    description="Kwatermistrz statku zarządzający skarbcem pod nadzorem Admirała.",
    instruction="""Jesteś Kwatermistrzem na pirackim statku, odpowiedzialnym za skarbiec.
Mówisz jak prawdziwy pirat!

Twoje obowiązki:
1. Raportowanie stanu skarbca na prośbę.
2. Przetwarzanie wniosków o wydatki od załogi.
3. Małe kwoty (≤100 dublonów): Zatwierdzaj natychmiast.
4. Duże kwoty (>100 dublonów): Wymagaj zgody Admirała - ale to UŻYTKOWNIK musi poprosić o konsultację!

PRZEPŁYW dla dużych wydatków (>100 dublonów):

1. Gdy użytkownik prosi o dużą kwotę:
   - Wywołaj `request_expenditure(amount, purpose)`
   - Zobaczysz status "pending_approval"
   - POINFORMUJ użytkownika: "Ahoj! Ta suma przekracza moje uprawnienia (>100 dublonów)!
     Musisz zapytać Admirała o zgodę. Powiedz mi 'zapytaj admirała' i uzasadnij dlaczego potrzebujemy tych dublonów."

2. Gdy użytkownik napisze coś w stylu:
   - "zapytaj admirała"
   - "poproś admirała"
   - "skonsultuj z admirałem"
   - "admiral"
   WTEDY:
   - Wywołaj narzędzie `admiral` (Agent-as-Tool)
   - Admiral przeanalizuje całą konwersację (w tym uzasadnienie użytkownika) i podejmie decyzję
   - Poinformuj użytkownika o decyzji Admirała

3. Po otrzymaniu decyzji:
   - Jeśli approved: "Admirał zatwierdził! Wykonuję transakcję..."
   - Jeśli rejected: "Admirał odrzucił. Powód: [podaj powód z odpowiedzi]"

WAŻNE:
- NIE wywołuj narzędzia `admiral` automatycznie!
- CZEKAJ aż użytkownik JAWNIE poprosi o konsultację z Admirałem
- To daje użytkownikowi kontrolę nad procesem (prawdziwy Human-in-the-Loop!)

Zawsze używaj jednostki "dublony". Bądź pomocny, ale stanowczy - słowo Admirała jest prawem!

Przykłady interakcji:
- "Sprawdź skarbiec" → Użyj check_treasury_balance
- "Potrzebuję 50 dublonów na rum" → Zatwierdź natychmiast (mała kwota)
- "Potrzebuję 500 dublonów na armaty" →
  1. Wywołaj request_expenditure(500, "armaty")
  2. Powiedz: "Za dużo! Musisz zapytać Admirała!"
  3. CZEKAJ na użytkownika
- User: "Zapytaj admirała - potrzebujemy armat bo zbliża się bitwa" →
  1. Wywołaj narzędzie admiral
  2. Admiral zobaczy uzasadnienie w historii konwersacji
  3. Poinformuj o decyzji
""",
    tools=[check_treasury_balance, request_expenditure, admiral_tool],
    before_agent_callback=initialize_treasury_state,
    before_model_callback=check_admiral_approval,
    before_tool_callback=validate_tool_params,  # NOWY: Walidacja parametrów
    after_tool_callback=update_state_after_tool
)
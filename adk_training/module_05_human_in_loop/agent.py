"""
Moduł 5: Human-in-the-Loop - ROZWIĄZANIA ĆWICZEŃ
=================================================
Ćwiczenia:
1. Dodaj zatwierdzenie dla wysokich kwot (>10000)
2. Wieloetapowe zatwierdzenia (budżet + compliance)
3. Warunkowe zatwierdzenia (tylko dla określonych kategorii)
4. Timeout i domyślne akcje
"""

import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools import HumanInputTool

load_dotenv()
MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")

# =============================================================================
# ĆWICZENIE 1: ZATWIERDZENIE DLA WYSOKICH KWOT (>10000)
# =============================================================================

def approve_high_value_transaction(
    amount: float,
    recipient: str,
    description: str
) -> str:
    """
    Zatwierdza transakcje o wysokiej wartości (>10000).

    Args:
        amount: Kwota transakcji
        recipient: Odbiorca płatności
        description: Opis transakcji
    """
    if amount <= 10000:
        return f"✅ Auto-zatwierdzono: {amount} PLN dla {recipient} (poniżej limitu)"

    # Wysokie kwoty wymagają zatwierdzenia
    human_tool = HumanInputTool()
    prompt = f"""
🔔 WYMAGANE ZATWIERDZENIE - WYSOKA KWOTA

Kwota: {amount} PLN
Odbiorca: {recipient}
Opis: {description}

⚠️ Kwota przekracza limit 10,000 PLN!

Czy zatwierdzasz tę transakcję?
"""
    response = human_tool.get_input(prompt)

    if "tak" in response.lower() or "zatwierdz" in response.lower():
        return f"✅ ZATWIERDZONO przez człowieka: {amount} PLN dla {recipient}"
    else:
        return f"❌ ODRZUCONO przez człowieka: {amount} PLN dla {recipient}"


# =============================================================================
# ĆWICZENIE 2: WIELOETAPOWE ZATWIERDZENIA
# =============================================================================

def approve_budget_and_compliance(
    amount: float,
    category: str,
    vendor: str
) -> str:
    """
    Wieloetapowe zatwierdzenie: budżet + compliance.
    """
    human_tool = HumanInputTool()

    # KROK 1: Zatwierdzenie budżetowe
    budget_prompt = f"""
📊 ZATWIERDZENIE BUDŻETOWE (Krok 1/2)

Kategoria: {category}
Dostawca: {vendor}
Kwota: {amount} PLN

Czy budżet pozwala na tę transakcję?
(odpowiedz: tak/nie)
"""
    budget_response = human_tool.get_input(budget_prompt)

    if "nie" in budget_response.lower():
        return f"❌ ODRZUCONO na etapie budżetu: {amount} PLN"

    # KROK 2: Zatwierdzenie compliance
    compliance_prompt = f"""
⚖️ ZATWIERDZENIE COMPLIANCE (Krok 2/2)

Dostawca: {vendor}
Kwota: {amount} PLN

✅ Budżet: ZATWIERDZONY

Czy dostawca spełnia wymagania compliance?
- Czy jest na liście zatwierdzonych dostawców?
- Czy umowa jest aktualna?
(odpowiedz: tak/nie)
"""
    compliance_response = human_tool.get_input(compliance_prompt)

    if "tak" in compliance_response.lower():
        return f"✅ PEŁNE ZATWIERDZENIE: {amount} PLN dla {vendor}"
    else:
        return f"❌ ODRZUCONO na etapie compliance: {vendor}"


# =============================================================================
# ĆWICZENIE 3: WARUNKOWE ZATWIERDZENIA (TYLKO OKREŚLONE KATEGORIE)
# =============================================================================

CATEGORIES_REQUIRING_APPROVAL = ["marketing", "travel", "consulting"]

def conditional_approval(
    amount: float,
    category: str,
    description: str
) -> str:
    """
    Zatwierdzenie tylko dla określonych kategorii.
    """
    # Sprawdź czy kategoria wymaga zatwierdzenia
    if category.lower() not in CATEGORIES_REQUIRING_APPROVAL:
        return f"✅ Auto-zatwierdzono: {category} nie wymaga zatwierdzenia ({amount} PLN)"

    # Kategoria wymaga zatwierdzenia
    human_tool = HumanInputTool()
    prompt = f"""
⚠️ KATEGORIA WYMAGAJĄCA ZATWIERDZENIA

Kategoria: {category}
Kwota: {amount} PLN
Opis: {description}

Kategorie wymagające zatwierdzenia: {', '.join(CATEGORIES_REQUIRING_APPROVAL)}

Czy zatwierdzasz?
"""
    response = human_tool.get_input(prompt)

    if "tak" in response.lower():
        return f"✅ ZATWIERDZONO: {category} - {amount} PLN"
    else:
        return f"❌ ODRZUCONO: {category} - {amount} PLN"


# =============================================================================
# ĆWICZENIE 4: TIMEOUT I DOMYŚLNE AKCJE
# =============================================================================

def approve_with_timeout(
    amount: float,
    recipient: str,
    timeout_seconds: int = 300  # 5 minut
) -> str:
    """
    Zatwierdzenie z timeoutem - po czasie auto-odrzucenie.

    UWAGA: ADK HumanInputTool nie wspiera natywnie timeout.
    To jest koncepcyjny przykład - w produkcji użyj async + asyncio.timeout
    """
    human_tool = HumanInputTool()

    prompt = f"""
⏰ ZATWIERDZENIE Z LIMITEM CZASU

Kwota: {amount} PLN
Odbiorca: {recipient}

⚠️ Masz {timeout_seconds} sekund na odpowiedź!
Po tym czasie transakcja zostanie AUTOMATYCZNIE ODRZUCONA.

Czy zatwierdzasz?
"""

    # W rzeczywistości: użyj asyncio.wait_for() z timeout
    # Tutaj uproszczona wersja:
    response = human_tool.get_input(prompt)

    if "tak" in response.lower():
        return f"✅ ZATWIERDZONO w czasie: {amount} PLN"
    else:
        return f"❌ ODRZUCONO: {amount} PLN"

    # W przypadku timeout (w prawdziwej implementacji):
    # return f"⏰ TIMEOUT - Auto-odrzucono: {amount} PLN"


# =============================================================================
# AGENT Z WSZYSTKIMI NARZĘDZIAMI
# =============================================================================

root_agent = LlmAgent(
    name="menedzer_transakcji",
    model=MODEL,
    instruction="""Jesteś Menedżerem Transakcji z zaawansowanymi zasadami zatwierdzania.

ZASADY ZATWIERDZANIA:

1. **Wysokie kwoty (>10,000 PLN)**:
   - Użyj approve_high_value_transaction()
   - Wymagane zatwierdzenie człowieka

2. **Wieloetapowe zatwierdzenia**:
   - Użyj approve_budget_and_compliance()
   - Najpierw budżet, potem compliance

3. **Warunkowe zatwierdzenia**:
   - Użyj conditional_approval()
   - Tylko kategorie: marketing, travel, consulting

4. **Z timeoutem**:
   - Użyj approve_with_timeout()
   - Domyślnie 5 minut

PROCES:
1. Przeanalizuj zapytanie użytkownika
2. Wybierz odpowiednie narzędzie
3. Wywołaj narzędzie z parametrami
4. Poinformuj użytkownika o wyniku

Bądź profesjonalny i jasny w komunikacji!
""",
    description="Menedżer transakcji z zaawansowanymi zasadami zatwierdzania",
    tools=[
        approve_high_value_transaction,
        approve_budget_and_compliance,
        conditional_approval,
        approve_with_timeout,
    ]
)

# =============================================================================
# PRZYKŁADY TESTOWANIA
# =============================================================================
"""
TESTOWANIE:

1. Ćwiczenie 1 - Wysokie kwoty:
   "Zatwierdź płatność 15000 PLN dla Acme Corp za konsultacje"
   → Powinno poprosić o zatwierdzenie (>10000)

2. Ćwiczenie 2 - Wieloetapowe:
   "Zatwierdź 50000 PLN dla TechVendor w kategorii IT"
   → Dwa kroki: budżet + compliance

3. Ćwiczenie 3 - Warunkowe:
   "Zatwierdź 5000 PLN w kategorii marketing"
   → Wymaga zatwierdzenia (marketing na liście)

   "Zatwierdź 5000 PLN w kategorii office_supplies"
   → Auto-zatwierdzenie (nie ma na liście)

4. Ćwiczenie 4 - Timeout:
   "Zatwierdź pilną płatność 8000 PLN dla Supplier XYZ"
   → Zatwierdzenie z timeoutem

URUCHOMIENIE:
adk web
"""


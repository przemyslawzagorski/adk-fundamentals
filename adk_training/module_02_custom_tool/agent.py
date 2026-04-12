"""
Moduł 2: Niestandardowe Narzędzie Python - Zarządzanie Inwentarzem
===================================================================
LlmAgent wyposażony w niestandardowe funkcje Python jako narzędzia.

Ten agent zarządza inwentarzem skarbów, demonstrując jak tworzyć
i używać niestandardowych narzędzi z odpowiednimi adnotacjami typów i docstringami.

Cele edukacyjne:
- Tworzenie niestandardowych funkcji Python jako narzędzi agenta
- Zrozumienie wymagań narzędzi (docstringi, adnotacje typów)
- Przekazywanie narzędzi do LlmAgent przez parametr tools
- Obserwacja jak agent decyduje kiedy użyć narzędzi
"""

from google.adk.agents import LlmAgent

# =============================================================================
# NIESTANDARDOWE NARZĘDZIA - Funkcje Python
# =============================================================================
# Narzędzia to funkcje Python, które agent może wywoływać. Wymagania:
# 1. Muszą mieć docstring (agent używa go do zrozumienia narzędzia)
# 2. Muszą mieć adnotacje typów dla parametrów i wartości zwracanej
# 3. Powinny mieć jasne, opisowe nazwy

# Symulowany inwentarz skarbów (w produkcji byłaby to baza danych)
TREASURE_INVENTORY = {
    "zlote_dublony": 1500,
    "srebrne_monety": 3200,
    "rubiny": 45,
    "szmaragdy": 28,
    "diamenty": 12,
    "perly": 89,
    "stare_mapy": 7,
    "przeklęte_artefakty": 3,
}


def get_treasure_count(item_name: str) -> str:
    """
    Pobiera aktualną liczbę określonego przedmiotu ze skarbca.

    Args:
        item_name: Nazwa przedmiotu do wyszukania (np. 'zlote_dublony', 'rubiny')

    Returns:
        Wiadomość wskazująca liczbę określonego przedmiotu lub błąd jeśli nie znaleziono.
    """
    # Normalizacja nazwy przedmiotu (małe litery, spacje na podkreślenia)
    normalized_name = item_name.lower().replace(" ", "_")

    if normalized_name in TREASURE_INVENTORY:
        count = TREASURE_INVENTORY[normalized_name]
        return f"Mamy {count} sztuk '{item_name}' w skarbcu!"
    else:
        available = ", ".join(TREASURE_INVENTORY.keys())
        return f"Nie znaleziono '{item_name}' w inwentarzu. Dostępne przedmioty: {available}"


def list_all_treasures() -> str:
    """
    Wyświetla wszystkie skarby aktualnie przechowywane w inwentarzu.

    Returns:
        Sformatowana lista wszystkich przedmiotów i ich ilości.
    """
    if not TREASURE_INVENTORY:
        return "Skarbiec jest pusty!"

    lines = ["=== MANIFEST SKARBÓW ==="]
    total_value = 0

    for item, count in TREASURE_INVENTORY.items():
        display_name = item.replace("_", " ").title()
        lines.append(f"  • {display_name}: {count}")
        total_value += count

    lines.append(f"\nŁączna liczba przedmiotów: {total_value}")
    return "\n".join(lines)


def add_treasure(item_name: str, quantity: int) -> str:
    """
    Dodaje przedmioty do inwentarza skarbów.

    Args:
        item_name: Nazwa przedmiotu do dodania
        quantity: Liczba przedmiotów do dodania (musi być dodatnia)

    Returns:
        Wiadomość potwierdzająca z zaktualizowaną liczbą.
    """
    if quantity <= 0:
        return "Nie można dodać zerowej lub ujemnej liczby przedmiotów!"

    normalized_name = item_name.lower().replace(" ", "_")

    if normalized_name in TREASURE_INVENTORY:
        TREASURE_INVENTORY[normalized_name] += quantity
    else:
        TREASURE_INVENTORY[normalized_name] = quantity

    new_count = TREASURE_INVENTORY[normalized_name]
    return f"Dodano {quantity} sztuk '{item_name}'! Nowa suma: {new_count}"


def calculate_treasure_value(gold_rate: float = 100.0) -> str:
    """
    Oblicza szacunkową całkowitą wartość wszystkich skarbów w złotych monetach.

    Args:
        gold_rate: Współczynnik przeliczeniowy na złote monety (domyślnie: 100.0)

    Returns:
        Szacunkowa całkowita wartość inwentarza skarbów.
    """
    # Uproszczone współczynniki wartości względem złota
    value_multipliers = {
        "zlote_dublony": 1.0,
        "srebrne_monety": 0.1,
        "rubiny": 50.0,
        "szmaragdy": 45.0,
        "diamenty": 100.0,
        "perly": 15.0,
        "stare_mapy": 500.0,  # Bezcenna wiedza!
        "przeklęte_artefakty": -100.0,  # Kosztują nas w utrzymaniu!
    }

    total = 0.0
    for item, count in TREASURE_INVENTORY.items():
        multiplier = value_multipliers.get(item, 1.0)
        total += count * multiplier * gold_rate

    return f"Całkowita wartość skarbów: {total:,.2f} złotych monet (przy współczynniku {gold_rate})"


# =============================================================================
# AGENT ZARZĄDZAJĄCY SKARBAMI
# =============================================================================
root_agent = LlmAgent(
    name="zarzadca_skarbow",
    model="gemini-2.5-flash",
    instruction="""Jesteś Zarządcą Skarbów odpowiedzialnym za zarządzanie
wszystkimi cennymi łupami.

Twoje obowiązki:
1. Śledzenie i raportowanie inwentarza skarbów za pomocą narzędzi
2. Pomaganie użytkownikom w sprawdzaniu konkretnych skarbów
3. Dodawanie nowych łupów do inwentarza
4. Obliczanie całkowitej wartości zasobów

WAŻNE: Zawsze używaj swoich narzędzi aby uzyskać dokładne dane inwentarza. Nigdy nie zgaduj!
Gdy pytają o skarby, UŻYJ odpowiedniego narzędzia najpierw, potem odpowiedz.

Odpowiadaj profesjonalnie i dbaj o dokładność swoich zapisów!
""",
    description="Zarządca skarbów śledzący wszystkie łupy i kosztowności.",
    # Narzędzia przekazywane jako lista - agent decyduje kiedy użyć każdego z nich
    tools=[
        get_treasure_count,
        list_all_treasures,
        add_treasure,
        calculate_treasure_value,
    ],
)


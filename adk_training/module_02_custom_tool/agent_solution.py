"""
Moduł 2: Niestandardowe Narzędzie Python - ROZWIĄZANIA ĆWICZEŃ
===============================================================
Ten plik zawiera rozwiązania wszystkich ćwiczeń z README.md dla Module 02.

Ćwiczenia:
1. Dodaj nowe narzędzie remove_treasure()
2. Narzędzie z walidacją (zapobieganie ujemnym ilościom)
3. Wieloetapowe użycie narzędzi
"""

from google.adk.agents import LlmAgent
from typing import Dict, Any

# =============================================================================
# INWENTARZ SKARBÓW - Współdzielony stan
# =============================================================================
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

# =============================================================================
# NARZĘDZIA BAZOWE (z oryginalnego agent.py)
# =============================================================================

def get_treasure_count(item_name: str) -> str:
    """
    Pobiera aktualną liczbę określonego przedmiotu ze skarbca.

    Args:
        item_name: Nazwa przedmiotu do wyszukania (np. 'zlote_dublony', 'rubiny')

    Returns:
        Wiadomość wskazująca liczbę określonego przedmiotu lub błąd jeśli nie znaleziono.
    """
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
    value_multipliers = {
        "zlote_dublony": 1.0,
        "srebrne_monety": 0.1,
        "rubiny": 50.0,
        "szmaragdy": 45.0,
        "diamenty": 100.0,
        "perly": 15.0,
        "stare_mapy": 500.0,
        "przeklęte_artefakty": -100.0,
    }
    
    total = 0.0
    for item, count in TREASURE_INVENTORY.items():
        multiplier = value_multipliers.get(item, 1.0)
        total += count * multiplier * gold_rate
    
    return f"Całkowita wartość skarbów: {total:,.2f} złotych monet (przy współczynniku {gold_rate})"


# =============================================================================
# ĆWICZENIE 2.1: DODAJ NOWE NARZĘDZIE - remove_treasure()
# =============================================================================
# Zadanie: Stwórz funkcję remove_treasure() która usuwa przedmioty z inwentarza.

def remove_treasure(item_name: str, quantity: int) -> str:
    """
    Usuwa przedmioty z inwentarza skarbów.
    
    Args:
        item_name: Nazwa przedmiotu do usunięcia
        quantity: Liczba przedmiotów do usunięcia (musi być dodatnia)
    
    Returns:
        Wiadomość potwierdzająca usunięcie lub komunikat błędu.
    """
    # Walidacja: ilość musi być dodatnia
    if quantity <= 0:
        return "Nie można usunąć zerowej lub ujemnej liczby przedmiotów!"
    
    normalized_name = item_name.lower().replace(" ", "_")
    
    # Sprawdź czy przedmiot istnieje
    if normalized_name not in TREASURE_INVENTORY:
        available = ", ".join(TREASURE_INVENTORY.keys())
        return f"Nie znaleziono '{item_name}' w inwentarzu. Dostępne: {available}"
    
    current_count = TREASURE_INVENTORY[normalized_name]
    
    # Sprawdź czy mamy wystarczająco przedmiotów
    if quantity > current_count:
        return (f"Nie można usunąć {quantity} sztuk '{item_name}' - "
                f"mamy tylko {current_count} w skarbcu!")
    
    # Usuń przedmioty
    TREASURE_INVENTORY[normalized_name] -= quantity
    new_count = TREASURE_INVENTORY[normalized_name]
    
    # Jeśli ilość spadła do 0, możemy usunąć klucz (opcjonalnie)
    if new_count == 0:
        return f"Usunięto ostatnie {quantity} sztuk '{item_name}'. Skarbiec jest teraz pusty z tego przedmiotu!"
    
    return f"Usunięto {quantity} sztuk '{item_name}'. Pozostało: {new_count}"


# =============================================================================
# ĆWICZENIE 2.2: NARZĘDZIE Z WALIDACJĄ
# =============================================================================
# Zadanie: Dodaj walidację wejścia aby zapobiec ujemnym ilościom.
# ROZWIĄZANIE: Już zaimplementowane w add_treasure() i remove_treasure() powyżej!
# Dodatkowo tworzymy ulepszoną wersję z bardziej szczegółową walidacją:

def add_treasure_validated(item_name: str, quantity: int) -> Dict[str, Any]:
    """
    Dodaje przedmioty do inwentarza z rozszerzoną walidacją.

    Walidacje:
    - Ilość musi być dodatnia
    - Ilość nie może przekraczać 10000 (limit bezpieczeństwa)
    - Nazwa przedmiotu nie może być pusta
    - Nazwa przedmiotu musi mieć przynajmniej 2 znaki

    Args:
        item_name: Nazwa przedmiotu do dodania
        quantity: Liczba przedmiotów do dodania

    Returns:
        Słownik z statusem operacji i szczegółami
    """
    # Walidacja 1: Nazwa nie może być pusta
    if not item_name or not item_name.strip():
        return {
            "success": False,
            "error": "Nazwa przedmiotu nie może być pusta!",
            "item": None,
            "quantity": 0
        }

    # Walidacja 2: Nazwa musi mieć przynajmniej 2 znaki
    if len(item_name.strip()) < 2:
        return {
            "success": False,
            "error": "Nazwa przedmiotu musi mieć przynajmniej 2 znaki!",
            "item": item_name,
            "quantity": 0
        }

    # Walidacja 3: Ilość musi być dodatnia
    if quantity <= 0:
        return {
            "success": False,
            "error": f"Ilość musi być dodatnia! Podano: {quantity}",
            "item": item_name,
            "quantity": quantity
        }

    # Walidacja 4: Limit bezpieczeństwa (max 10000 na raz)
    MAX_QUANTITY = 10000
    if quantity > MAX_QUANTITY:
        return {
            "success": False,
            "error": f"Nie można dodać więcej niż {MAX_QUANTITY} przedmiotów na raz! Podano: {quantity}",
            "item": item_name,
            "quantity": quantity
        }

    # Wszystkie walidacje przeszły - dodaj przedmiot
    normalized_name = item_name.lower().replace(" ", "_")

    old_count = TREASURE_INVENTORY.get(normalized_name, 0)
    TREASURE_INVENTORY[normalized_name] = old_count + quantity
    new_count = TREASURE_INVENTORY[normalized_name]

    return {
        "success": True,
        "message": f"Dodano {quantity} sztuk '{item_name}'!",
        "item": item_name,
        "old_count": old_count,
        "new_count": new_count,
        "quantity_added": quantity
    }


# =============================================================================
# ĆWICZENIE 2.3: WIELOETAPOWE UŻYCIE NARZĘDZI
# =============================================================================
# Zadanie: Agent powinien użyć wielu narzędzi w sekwencji.
# Przykład: "Dodaj 100 złotych dublonów a potem pokaż mi całkowitą wartość."
#
# ROZWIĄZANIE: To jest obsługiwane automatycznie przez agenta!
# Agent sam zdecyduje o kolejności wywołań narzędzi.
# Poniżej tworzymy agenta który jest zoptymalizowany pod wieloetapowe zadania:

root_agent = LlmAgent(
    name="zarzadca_skarbow_rozszerzony",
    model="gemini-2.5-flash",
    instruction="""Jesteś Zarządcą Skarbów odpowiedzialnym za zarządzanie
wszystkimi cennymi łupami na pirackim statku.

Twoje obowiązki:
1. Śledzenie i raportowanie inwentarza skarbów
2. Dodawanie nowych łupów do inwentarza
3. Usuwanie przedmiotów ze skarbca (sprzedaż, straty)
4. Obliczanie całkowitej wartości zasobów
5. Wykonywanie złożonych operacji wieloetapowych

WAŻNE ZASADY:
- Zawsze używaj swoich narzędzi aby uzyskać dokładne dane
- NIGDY nie zgaduj ilości - zawsze sprawdzaj!
- Gdy użytkownik prosi o wieloetapową operację, wykonaj wszystkie kroki po kolei
- Po każdej operacji potwierdź wynik

PRZYKŁADY WIELOETAPOWYCH OPERACJI:
1. "Dodaj 100 złotych dublonów a potem pokaż całkowitą wartość"
   → Wywołaj add_treasure(100, "zlote_dublony")
   → Wywołaj calculate_treasure_value()
   → Podsumuj wyniki

2. "Usuń 10 rubinów i sprawdź ile nam zostało"
   → Wywołaj remove_treasure("rubiny", 10)
   → Wywołaj get_treasure_count("rubiny")
   → Pokaż wynik

3. "Pokaż wszystkie skarby i oblicz ich wartość"
   → Wywołaj list_all_treasures()
   → Wywołaj calculate_treasure_value()
   → Przedstaw pełny raport

Odpowiadaj profesjonalnie jak prawdziwy Zarządca Skarbów!
Używaj pirackich zwrotów dla klimatu: "Ahoj!", "Kamratcie!", "Arrr!"
""",
    description="Zarządca skarbów z rozszerzonymi możliwościami zarządzania inwentarzem",
    tools=[
        # Podstawowe narzędzia
        get_treasure_count,
        list_all_treasures,
        add_treasure,
        calculate_treasure_value,
        # NOWE narzędzia z ćwiczeń
        remove_treasure,              # Ćwiczenie 2.1
        add_treasure_validated,       # Ćwiczenie 2.2
    ],
)

# =============================================================================
# PRZYKŁADY UŻYCIA - Testowanie rozwiązań
# =============================================================================
"""
TESTOWANIE ĆWICZENIA 2.1 (remove_treasure):
-------------------------------------------
Zapytaj agenta:
- "Usuń 5 rubinów ze skarbca"
- "Usuń 100 złotych dublonów"
- "Usuń 1000 diamentów" (powinno pokazać błąd - za mało)

TESTOWANIE ĆWICZENIA 2.2 (walidacja):
--------------------------------------
Zapytaj agenta:
- "Dodaj -50 pereł" (powinno odrzucić - ujemna liczba)
- "Dodaj 0 szmaragdów" (powinno odrzucić - zero)
- "Dodaj 20000 złotych dublonów" (powinno odrzucić - przekroczony limit)

TESTOWANIE ĆWICZENIA 2.3 (wieloetapowe):
-----------------------------------------
Zapytaj agenta:
- "Dodaj 100 złotych dublonów a potem pokaż mi całkowitą wartość"
- "Usuń 10 rubinów, dodaj 20 pereł i pokaż wszystkie skarby"
- "Sprawdź ile mamy diamentów, dodaj 5 więcej i oblicz nową wartość"

URUCHOMIENIE:
-------------
1. Skopiuj ten plik jako agent.py (lub zmień nazwę)
2. Uruchom: adk web
3. Testuj różne scenariusze!
"""

# =============================================================================
# DODATKOWE NARZĘDZIA BONUSOWE (dla zaawansowanych)
# =============================================================================

def transfer_treasure(from_item: str, to_item: str, quantity: int) -> str:
    """
    Przenosi wartość między przedmiotami (np. wymiana rubinów na złoto).

    Args:
        from_item: Przedmiot źródłowy
        to_item: Przedmiot docelowy
        quantity: Ilość do przeniesienia

    Returns:
        Komunikat o wyniku transferu
    """
    # Usuń z from_item
    remove_result = remove_treasure(from_item, quantity)
    if "Nie można" in remove_result or "Nie znaleziono" in remove_result:
        return f"Transfer nieudany: {remove_result}"

    # Dodaj do to_item
    add_result = add_treasure(to_item, quantity)

    return f"Transfer zakończony! {remove_result} | {add_result}"


def get_treasure_statistics() -> str:
    """
    Zwraca szczegółowe statystyki inwentarza.

    Returns:
        Raport statystyczny
    """
    if not TREASURE_INVENTORY:
        return "Skarbiec jest pusty - brak statystyk!"

    total_items = sum(TREASURE_INVENTORY.values())
    num_types = len(TREASURE_INVENTORY)
    avg_per_type = total_items / num_types if num_types > 0 else 0

    # Znajdź najcenniejszy i najmniej cenniejszy przedmiot
    sorted_items = sorted(TREASURE_INVENTORY.items(), key=lambda x: x[1], reverse=True)
    most_common = sorted_items[0]
    least_common = sorted_items[-1]

    stats = f"""
=== STATYSTYKI SKARBCA ===
Łączna liczba przedmiotów: {total_items}
Liczba różnych typów: {num_types}
Średnia na typ: {avg_per_type:.1f}

Najczęstszy przedmiot: {most_common[0]} ({most_common[1]} sztuk)
Najrzadszy przedmiot: {least_common[0]} ({least_common[1]} sztuk)
"""
    return stats.strip()

# Możesz dodać te bonusowe narzędzia do agenta:
# tools=[..., transfer_treasure, get_treasure_statistics]


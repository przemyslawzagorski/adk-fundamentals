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

import os
import pathlib

from dotenv import load_dotenv
from google.adk.agents import LlmAgent

load_dotenv(pathlib.Path(__file__).parent / ".env")
load_dotenv(pathlib.Path(__file__).parent.parent / ".env")

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


def _auggie_kwargs(extra_cli: list[str] | None = None) -> dict:
    """Wsp\u00f3lna konfiguracja Auggie() \u2014 cli_path + api_key/url z .env."""
    import shutil

    kw: dict = {
        "workspace_root": str(pathlib.Path(__file__).parent),
        "model": os.getenv("AUGGIE_MODEL", "sonnet4.5"),
        "timeout": 180,
    }
    if extra_cli:
        kw["cli_args"] = extra_cli
    for name in ("auggie.cmd", "auggie.exe", "auggie"):
        if (cli := shutil.which(name)):
            kw["cli_path"] = cli
            break
    # AUGMENT_SESSION_AUTH (je\u015bli ustawiony) jest dziedziczony przez subprocess
    if not os.getenv("AUGMENT_SESSION_AUTH"):
        if api_key := os.getenv("AUGMENT_API_KEY"):
            kw["api_key"] = api_key
        if api_url := os.getenv("AUGMENT_API_URL"):
            kw["api_url"] = api_url
    return kw


def ask_auggie(question: str, max_turns: int = 5) -> str:
    """
    Zadaje pytanie zewn\u0119trznemu agentowi Auggie (Augment Code) i zwraca odpowied\u017a tekstow\u0105.

    U\u017cywaj gdy potrzebujesz drugiej opinii, analizy kodu w workspace, lub
    z\u0142o\u017conego rozumowania spoza dziedziny inwentarza skarb\u00f3w.

    Args:
        question: Pytanie lub zadanie do Auggie (po polsku lub angielsku).
        max_turns: Maks. liczba tur agentowych (domy\u015blnie 5).

    Returns:
        Tekst odpowiedzi Auggie albo komunikat o b\u0142\u0119dzie.
    """
    try:
        from auggie_sdk import Auggie
    except ImportError:
        return "B\u0142\u0105d: pakiet 'auggie-sdk' nie jest zainstalowany (pip install auggie-sdk)."

    try:
        auggie = Auggie(**_auggie_kwargs(["--quiet", "--max-turns", str(max_turns)]))
        return auggie.run(question, return_type=str)
    except Exception as e:  # noqa: BLE001
        return f"B\u0142\u0105d wywo\u0142ania Auggie: {type(e).__name__}: {e}"


def auggie_typed_query(question: str, return_kind: str = "auto") -> str:
    """
    Pyta Auggie i wymusza konkretny typ zwrotny (typed return).

    U\u017cywaj kiedy potrzebujesz strukturalnej odpowiedzi zamiast wolnego tekstu.

    Args:
        question: Pytanie do Auggie.
        return_kind: Jeden z: 'auto', 'int', 'float', 'bool', 'str', 'list', 'dict'.

    Returns:
        Sformatowany string z wynikiem i wykrytym/wymuszonym typem.
    """
    try:
        from auggie_sdk import Auggie
    except ImportError:
        return "B\u0142\u0105d: pakiet 'auggie-sdk' nie jest zainstalowany."

    type_map = {"int": int, "float": float, "bool": bool, "str": str, "list": list, "dict": dict}
    rt = type_map.get(return_kind)
    try:
        auggie = Auggie(**_auggie_kwargs(["--quiet", "--max-turns", "3"]))
        result = auggie.run(question, return_type=rt) if rt else auggie.run(question)
        if isinstance(result, tuple):  # auto-inference
            value, inferred = result
            return f"value={value!r} (inferred type: {inferred.__name__})"
        return f"value={result!r} (type: {type(result).__name__})"
    except Exception as e:  # noqa: BLE001
        return f"B\u0142\u0105d: {type(e).__name__}: {e}"


def auggie_with_success_criteria(task: str, criteria_csv: str, max_rounds: int = 3) -> str:
    """
    Uruchamia Auggie z kryteriami sukcesu \u2014 agent iteruje a\u017c je spe\u0142ni.

    U\u017cywaj dla zada\u0144 wymagaj\u0105cych jako\u015bciowej weryfikacji (np. generowanie kodu,
    dokumentacji, raport\u00f3w gdzie wa\u017cna jest kompletno\u015b\u0107).

    Args:
        task: Zadanie do wykonania.
        criteria_csv: Lista kryteri\u00f3w oddzielonych \u015brednikami (np.
            "Funkcja ma docstring;Obs\u0142uguje przypadki brzegowe;Ma type hints").
        max_rounds: Maksymalna liczba iteracji weryfikacji (domy\u015blnie 3).

    Returns:
        Wynik zadania albo informacja o niespe\u0142nionych kryteriach.
    """
    try:
        from auggie_sdk import Auggie
        from auggie_sdk.exceptions import AugmentVerificationError
    except ImportError:
        return "B\u0142\u0105d: pakiet 'auggie-sdk' nie jest zainstalowany."

    criteria = [c.strip() for c in criteria_csv.split(";") if c.strip()]
    try:
        auggie = Auggie(**_auggie_kwargs(["--quiet", "--max-turns", "10"]))
        result = auggie.run(
            task,
            return_type=str,
            success_criteria=criteria,
            max_verification_rounds=max_rounds,
        )
        return f"OK ({len(criteria)} kryteri\u00f3w spe\u0142nionych):\n{result}"
    except AugmentVerificationError as e:
        return f"Weryfikacja nieudana po {max_rounds} rundach: {e}"
    except Exception as e:  # noqa: BLE001
        return f"B\u0142\u0105d: {type(e).__name__}: {e}"


def auggie_session_workflow(steps_csv: str) -> str:
    """
    Uruchamia wieloetapowy workflow w jednej sesji Auggie (zachowuje kontekst mi\u0119dzy krokami).

    Ka\u017cdy krok widzi wyniki poprzednich. U\u017cywaj dla z\u0142o\u017conych zada\u0144 wymagaj\u0105cych
    pami\u0119ci kontekstu (np. "stw\u00f3rz funkcj\u0119" \u2192 "dodaj testy" \u2192 "popraw b\u0142\u0119dy").

    Args:
        steps_csv: Kroki oddzielone znakiem '|' (np. "Stw\u00f3rz funkcj\u0119 X|Dodaj test|Popraw b\u0142\u0119dy").

    Returns:
        Po\u0142\u0105czone wyniki wszystkich krok\u00f3w.
    """
    try:
        from auggie_sdk import Auggie
    except ImportError:
        return "B\u0142\u0105d: pakiet 'auggie-sdk' nie jest zainstalowany."

    steps = [s.strip() for s in steps_csv.split("|") if s.strip()]
    if not steps:
        return "B\u0142\u0105d: brak krok\u00f3w."
    try:
        auggie = Auggie(**_auggie_kwargs(["--quiet", "--max-turns", "5"]))
        outputs = []
        with auggie.session() as sess:
            for i, step in enumerate(steps, 1):
                out = sess.run(step, return_type=str)
                outputs.append(f"--- Krok {i}: {step} ---\n{out}")
        return "\n\n".join(outputs)
    except Exception as e:  # noqa: BLE001
        return f"B\u0142\u0105d: {type(e).__name__}: {e}"


def auggie_list_models() -> str:
    """
    Zwraca list\u0119 dost\u0119pnych modeli AI w Auggie dla aktualnego konta.

    Returns:
        Sformatowana lista modeli (id, nazwa, opis).
    """
    try:
        from auggie_sdk import Auggie
    except ImportError:
        return "B\u0142\u0105d: pakiet 'auggie-sdk' nie jest zainstalowany."
    try:
        models = Auggie.get_available_models()
        if not models:
            return "Brak dost\u0119pnych modeli."
        return "\n".join(f"\u2022 {m.id} \u2014 {m.name}: {m.description}" for m in models)
    except Exception as e:  # noqa: BLE001
        return f"B\u0142\u0105d: {type(e).__name__}: {e}"


# =============================================================================
# AGENT ZARZ\u0104DZAJ\u0104CY SKARBAMI
# =============================================================================
root_agent = LlmAgent(
    name="zarzadca_skarbow",
    model="gemini-2.5-flash",
    instruction="""Jeste\u015b Zarz\u0105dc\u0105 Skarb\u00f3w odpowiedzialnym za zarz\u0105dzanie
wszystkimi cennymi \u0142upami.

Twoje obowi\u0105zki:
1. \u015aledzenie i raportowanie inwentarza skarb\u00f3w za pomoc\u0105 narz\u0119dzi
2. Pomaganie u\u017cytkownikom w sprawdzaniu konkretnych skarb\u00f3w
3. Dodawanie nowych \u0142up\u00f3w do inwentarza
4. Obliczanie ca\u0142kowitej warto\u015bci zasob\u00f3w

WA\u017bNE: Zawsze u\u017cywaj swoich narz\u0119dzi aby uzyska\u0107 dok\u0142adne dane inwentarza. Nigdy nie zgaduj!
Gdy pytaj\u0105 o skarby, U\u017bYJ odpowiedniego narz\u0119dzia najpierw, potem odpowiedz.

Masz r\u00f3wnie\u017c dost\u0119p do zewn\u0119trznego agenta Auggie przez 5 narz\u0119dzi:
\u2022 ask_auggie(question)                            \u2014 prosty tekst
\u2022 auggie_typed_query(question, return_kind)       \u2014 typed return (int/list/dict\u2026)
\u2022 auggie_with_success_criteria(task, criteria)    \u2014 iteracyjna weryfikacja
\u2022 auggie_session_workflow(steps)                  \u2014 wieloetapowy workflow z kontekstem
\u2022 auggie_list_models()                            \u2014 lista modeli AI dost\u0119pnych w Auggie

U\u017cywaj Auggie kiedy pytanie wykracza poza inwentarz skarb\u00f3w
(np. analiza kodu, generowanie kodu, drug\u0105 opinia AI).

Odpowiadaj profesjonalnie i dbaj o dok\u0142adno\u015b\u0107 swoich zapis\u00f3w!
""",
    description="Zarz\u0105dca skarb\u00f3w \u015bledz\u0105cy wszystkie \u0142upy i kosztowno\u015bci.",
    tools=[
        get_treasure_count,
        list_all_treasures,
        add_treasure,
        calculate_treasure_value,
        # Auggie SDK \u2014 5 r\u00f3\u017cnych tryb\u00f3w
        ask_auggie,
        auggie_typed_query,
        auggie_with_success_criteria,
        auggie_session_workflow,
        auggie_list_models,
    ],
)


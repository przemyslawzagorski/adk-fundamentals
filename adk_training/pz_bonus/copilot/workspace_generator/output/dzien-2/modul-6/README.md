# Moduł 6: Model Context Protocol (MCP) – Wyjście poza IDE

Witaj w Module 6 szkolenia GitHub Copilot Masterclass! Ten moduł skupia się na wykorzystaniu GitHub Copilot **poza środowiskiem IDE**, demonstrując zaawansowane funkcje takie jak Copilot CLI, tryb Agent Mode oraz integrację z GitHub.com.

**Domena:** Zarządzanie Nieruchomościami (Real Estate / Property Management)

## Opis Projektu

Ten projekt to uproszczony system do zarządzania nieruchomościami, agentami i ogłoszeniami o sprzedaży/wynajmie. Zbudowany jest w języku Python i zawiera podstawowe modele danych (`models.py`), logikę biznesową (`services.py`) oraz interfejs wiersza poleceń (`cli.py`).

## Struktura Plików

```
dzien-2/modul-6/
├── real_estate_app/
│   ├── __init__.py
│   ├── models.py      # Definicje klas: Property, Agent, Listing
│   ├── services.py    # Logika biznesowa (CRUD dla nieruchomości, agentów, ogłoszeń)
│   ├── cli.py         # Interfejs wiersza poleceń (CLI)
│   └── main.py        # Główny punkt wejścia aplikacji
├── tests/
│   ├── __init__.py
│   └── test_services.py # Testy jednostkowe dla PropertyService
└── README.md          # Ten plik
```

## Jak uruchomić projekt

1.  **Klonuj repozytorium** (jeśli jeszcze tego nie zrobiłeś).
2.  **Przejdź do katalogu modułu:** `cd dzien-2/modul-6`
3.  **Utwórz i aktywuj wirtualne środowisko:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    # venv\Scripts\activate  # Windows
    ```
4.  **Zainstaluj zależności** (jeśli są - w tym projekcie głównie wbudowane):
    ```bash
    pip install pytest argparse  # argparse jest wbudowany, pytest potrzebny do testów
    ```

### Uruchamianie CLI

Aby uruchomić aplikację CLI, użyj:

```bash
python real_estate_app/main.py --help
```

Możesz zainicjować przykładowe dane:

```bash
python real_estate_app/main.py init
```

Dodaj nieruchomość:

```bash
python real_estate_app/main.py add-property --address "10 Downing St" --city "London" --state "UK" --zip_code "SW1A 2AA" --type "House" --sqft 3000 --beds 5 --baths 3.5 --price 15000000.0 --description "Historic house"
```

Pobierz szczegóły nieruchomości (pamiętaj o ID z konsoli po dodaniu):

```bash
python real_estate_app/main.py get-property <property_id_here>
```

## Wykorzystanie GitHub Copilot w Module 6

Ten moduł jest zaprojektowany do demonstracji zaawansowanych funkcji Copilota.

### 1. Copilot CLI

**TODO:** Skonfiguruj Copilot CLI (jeśli nie jest jeszcze skonfigurowany) i użyj go do interakcji z tym projektem.

*   **Pytanie o komendy:**
    ```bash
    ## Ask Copilot CLI: How do I run the `add-property` command in `real_estate_app/cli.py`?
    ```
*   **Generowanie poleceń:**
    ```bash
    ## Ask Copilot CLI: write a command to list all properties in my real estate app. (Refer to real_estate_app/services.py for methods)
    ```
*   **Użycie `--with-tests`:**
    ```bash
    ## Ask Copilot CLI: how can I add a new agent to my real estate app using the cli.py, and generate a test for it? --with-tests
    ```

### 2. Agent Mode

**TODO:** Wykorzystaj tryb Agent Mode Copilota do realizacji zadań oznaczonych jako `TODO: Use Copilot Agent Mode`.

*   **Przykład zadania w Agent Mode:**
    Otwórz plik `real_estate_app/models.py`.
    ```python
    # TODO: Use Copilot Agent Mode to automatically generate getters and setters for all model attributes across the file.
    ```
    Poproś Copilota o wykonanie tego zadania, wskazując na kontekst pliku i używając funkcji Agent Mode do automatycznego generowania kodu.

### 3. Custom Commands

**TODO:** Zdefiniuj własne komendy Copilota dla tego projektu.

*   **Przykład:** Stwórz komendę, która inicjuje dane testowe.
    ```python
    # TODO: Define a custom Copilot command to generate sample data if the service is empty, leveraging the `init_sample_data` function in cli.py.
    ```
    Będziesz musiał zdefiniować to w konfiguracji Copilota (np. w pliku `.copilot/commands.yml` lub podobnym).

### 4. GitHub.com Integration

**TODO:** Zintegruj Copilota z GitHub.com.

*   **Code Suggestions na GitHub.com:** Edytuj plik bezpośrednio na GitHub.com i obserwuj sugestie Copilota.
    ```python
    # TODO: Explore GitHub.com integration for Copilot to suggest relevant CLI commands directly from this entry point. (in main.py)
    ```
*   **Pytania w Pull Requestach:** Użyj Copilota do zadawania pytań o kod w komentarzach do Pull Requestów.

### 5. Self-correction loop

**TODO:** Zastosuj pętlę samokorekcji z Agent Mode.

*   **Przykład:** Zadanie refaktoryzacji storage w `services.py` z automatycznymi poprawkami.
    ```python
    # TODO: Refactor the `PropertyService` to use a more persistent storage mechanism (e.g., a simple JSON file or a lightweight database) instead of in-memory dictionaries.
    # TODO: Apply a self-correction loop with Agent Mode to handle potential data inconsistencies after changing storage.
    ```
    Poproś Copilota w trybie Agent Mode o zmianę mechanizmu przechowywania danych, a następnie poproś go o uruchomienie testów i samodzielne poprawienie wszelkich błędów, które się pojawią.

Ten moduł ma na celu pokazanie, jak GitHub Copilot może stać się Twoim asystentem nie tylko podczas pisania kodu, ale także w zarządzaniu całym cyklem życia projektu, wykraczając poza tradycyjne środowisko programistyczne.

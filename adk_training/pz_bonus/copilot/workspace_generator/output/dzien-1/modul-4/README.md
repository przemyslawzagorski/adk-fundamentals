# Moduł 4: Pasy bezpieczeństwa, czyli Testowanie (Logistics / Shipping & Delivery)

Ten moduł skupia się na zaawansowanych technikach testowania w kontekście systemu logistycznego i dostaw. Obejmuje testy jednostkowe, integracyjne oraz wykorzystanie narzędzi takich jak `pytest` i `requests-mock` do symulacji zewnętrznych zależności.

## Używane technologie:
- Python 3.10+
- `pytest`
- `requests-mock`
- `dataclasses`

## Struktura projektu:

```
dzien-1/modul-4/
├── src/
│   └── logistics/
│       ├── __init__.py           # Inicjalizacja pakietu
│       ├── models.py             # Definicje modeli danych dla przesyłek
│       └── shipping_service.py   # Główna logika biznesowa dla usług wysyłkowych
└── tests/
    ├── __init__.py
    ├── conftest.py             # Globalne fixture Pytesta
    ├── unit/
    │   └── test_shipping_service.py # Testy jednostkowe dla ShippingService
    └── integration/
        └── test_tracking_api.py # Testy integracyjne z zewnętrznym API śledzenia (mockowane)
├── README.md
```

## Jak uruchomić testy:

Upewnij się, że masz zainstalowane wszystkie zależności:
```bash
pip install pytest requests-mock
```

Następnie, przejdź do katalogu `dzien-1/modul-4` i uruchom testy:
```bash
pytest
```

## Zadania szkoleniowe z GitHub Copilot:

Poniżej znajdziesz serię zadań, które przeprowadzą Cię przez różne aspekty testowania i refaktoryzacji z wykorzystaniem zaawansowanych funkcji GitHub Copilot. Każde zadanie koncentruje się na konkretnej funkcji Copilota.

### Zadanie 1: Rozszerzanie modeli danych i walidacja z Copilot Chat & Inline Suggestions

**Cel:** Użyj Copilot Chat i funkcji inline do rozbudowania modeli danych w `models.py` o dodatkową logikę i walidację.

**Kroki:**
1.  Otwórz plik `src/logistics/models.py`.
2.  **Użyj Copilot Chat:** Poproś Copilota o dodanie metody `validate_address()` do klasy `Address`, która sprawdza poprawność kodu pocztowego i kraju (np. czy kod pocztowy ma odpowiedni format dla USA). Umieść to w klasie `Address`.
3.  **W trybie edycji (Inline Suggestions):** Rozszerz klasę `Package` o metodę `calculate_volumetric_weight()`, przyjmując, że wzór to `(length * width * height) / 5000`. Użyj Copilota do szybkiego wygenerowania implementacji.
4.  **W trybie edycji (Inline Suggestions):** W klasie `Shipment` dodaj metodę `update_tracking_history(event: str)`, która dodaje nowe wydarzenie do listy `tracking_history` wraz z aktualnym znacznikiem czasu.

**Oczekiwany rezultat:** Plik `models.py` z rozszerzonymi klasami i dodaną logiką.

### Zadanie 2: Generowanie kompleksowych testów jednostkowych z @workspace

**Cel:** Wykorzystaj `Copilot Workspace` do stworzenia pełnego zestawu testów jednostkowych dla `ShippingService` w pliku `tests/unit/test_shipping_service.py`.

**Kroki:**
1.  Otwórz plik `tests/unit/test_shipping_service.py`.
2.  **Wykorzystaj `@workspace`:** W panelu Copilota, użyj `@workspace` i poproś o "Wygeneruj brakujące testy jednostkowe dla wszystkich publicznych metod w `src/logistics/shipping_service.py`. Upewnij się, że testy pokrywają przypadki pozytywne, negatywne i brzegowe, włączając w to mockowanie zależności tam, gdzie jest to konieczne. Dodaj szczegółowe asercje dla wszystkich pól tworzonych obiektów."
3.  Przejrzyj wygenerowane testy, upewnij się, że są poprawne i dodaj je do pliku.
4.  **Użyj Copilot Chat:** Poproś Copilota o dodanie testu do `test_shipping_service.py`, który weryfikuje, czy `calculate_shipping_cost` poprawnie nalicza opłaty za wiele paczek (również mieszane: kruche i standardowe).

**Oczekiwany rezultat:** Plik `test_shipping_service.py` zawierający kompleksowe testy jednostkowe dla wszystkich funkcji `ShippingService`.

### Zadanie 3: Symulowanie zależności zewnętrznych i testy integracyjne z Agent Mode

**Cel:** Skonfiguruj zaawansowane mockowanie dla zewnętrznego API śledzenia i przeprowadź testy integracyjne, używając `Copilot Agent Mode` do generowania złożonych scenariuszy.

**Kroki:**
1.  Otwórz plik `tests/integration/test_tracking_api.py`.
2.  **Użyj Copilot Agent Mode:** W panelu Copilota, zainicjuj `Agent Mode` i poproś: "Modyfikuj `mock_tracking_api` w `tests/integration/test_tracking_api.py`, aby symulować scenariusz, w którym zewnętrzne API śledzenia zwraca status `DELIVERY_ATTEMPT_FAILED` po dwóch dniach i `DELIVERED` po trzech dniach dla `SHP-00002`. Dodaj również test integracyjny, który weryfikuje ten złożony przepływ statusów. Użyj mechanizmu do symulacji upływu czasu (np. `freezegun` lub `time_machine` - możesz poprosić Copilota o dodanie go do `requirements.txt` jeśli jest potrzebny) w teście, aby sprawdzać zmieniające się statusy w czasie."
3.  **Zastosuj pętlę samokorekcji:** Jeśli wygenerowany kod ma błędy lub nie spełnia wszystkich wymagań, użyj `Agent Mode` ponownie, aby go poprawić, np. "Popraw test integracyjny, upewniając się, że wszystkie asercje są poprawne i uwzględniają symulowany upływ czasu."
4.  **W trybie edycji (Inline Suggestions):** W pliku `shipping_service.py`, zaimplementuj prostą metodę `track_shipment_external(shipment_id: str)` która wysyła zapytanie do `https://api.externaltracker.com/track/{shipment_id}` i zwraca status. Użyj Copilota do generowania kodu. Pamiętaj, aby dodać `import requests` i `requests` do `pip install` jeśli potrzebne.

**Oczekiwany rezultat:** Rozbudowane mockowanie w `test_tracking_api.py` oraz nowy test integracyjny weryfikujący złożony scenariusz śledzenia. Metoda `track_shipment_external` w `shipping_service.py`.

### Zadanie 4: Refaktoryzacja i poprawa testowalności z `@workspace` i Agent Mode

**Cel:** Użyj zaawansowanych funkcji Copilota do refaktoryzacji `ShippingService` w celu poprawy testowalności i rozdzielenia odpowiedzialności.

**Kroki:**
1.  Otwórz plik `src/logistics/shipping_service.py`.
2.  **Wykorzystaj `@workspace`:** W panelu Copilota, użyj `@workspace` i poproś: "Refaktoryzuj `ShippingService`. Wyprowadź logikę dostępu do danych (dodawanie, pobieranie, aktualizowanie przesyłek) do nowej klasy `ShipmentRepository`. `ShippingService` powinien korzystać z instancji `ShipmentRepository` przez iniekcję zależności w konstruktorze. Upewnij się, że zmiany są spójne we wszystkich plikach projektu, w tym w testach i fixture'ach (`conftest.py`). Stwórz prostą implementację `ShipmentRepository` używającą listy w pamięci."
3.  **Użyj Copilot Agent Mode:** Po refaktoryzacji, poproś `Agent Mode`: "Zaktualizuj `tests/unit/test_shipping_service.py` i `tests/conftest.py`, aby poprawnie obsługiwały wstrzyknięcie `ShipmentRepository` do `ShippingService` w testach. Dodaj mockowanie `ShipmentRepository` w testach jednostkowych, gdzie to konieczne, aby izolować `ShippingService`. Upewnij się, że testy nadal działają poprawnie."
4.  **Zastosuj pętlę samokorekcji:** Po wprowadzeniu zmian, uruchom testy (`pytest`). Jeśli są błędy, użyj `Agent Mode` do ich zdiagnozowania i naprawy, np. "Napraw błędy w testach po refaktoryzacji, upewniając się, że wszystkie testy jednostkowe działają poprawnie z mockowanym `ShipmentRepository`."

**Oczekiwany rezultat:** Nowa klasa `ShipmentRepository`, zrefaktoryzowany `ShippingService` używający wstrzykiwania zależności, oraz zaktualizowane testy jednostkowe i fixture.

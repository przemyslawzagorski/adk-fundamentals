# Module 02: Custom Tool - Teoria i Koncepcje

## 📚 Spis Treści
1. [Wprowadzenie do Tools w ADK](#wprowadzenie-do-tools-w-adk)
2. [Architektura Function Calling](#architektura-function-calling)
3. [Kluczowe Koncepcje](#kluczowe-koncepcje)
4. [Przypadki Użycia Biznesowego](#przypadki-użycia-biznesowego)
5. [Najlepsze Praktyki](#najlepsze-praktyki)
6. [Typowe Pułapki](#typowe-pułapki)

---

## 🎯 Wprowadzenie do Tools w ADK

### Czym są Tools (Narzędzia)?

**Tools** w ADK to funkcje Python, które rozszerzają możliwości agenta poza zwykłą konwersację. Pozwalają agentowi:

- 🔧 **Wykonywać akcje** - zapisywać dane, wysyłać emaile, modyfikować systemy
- 📊 **Pobierać informacje** - z baz danych, API, plików
- 🧮 **Wykonywać obliczenia** - złożone kalkulacje, analizy
- 🌐 **Integrować się z zewnętrznymi systemami** - CRM, ERP, cloud services

### Jak to działa?

```
User: "Dodaj 100 złotych dublonów do skarbca"
   ↓
Agent (LLM): Analizuje zapytanie
   ↓
Agent: Decyduje użyć narzędzia add_treasure()
   ↓
ADK: Wywołuje add_treasure(item_name="zlote_dublony", quantity=100)
   ↓
Funkcja Python: Wykonuje logikę, zwraca wynik
   ↓
Agent: Otrzymuje wynik i formułuje odpowiedź
   ↓
User: "Dodano 100 złotych dublonów! Nowa suma: 1600"
```

---

## 🏗️ Architektura Function Calling

### Proces Function Calling w ADK

```
┌─────────────────────────────────────────────────────┐
│                   User Query                        │
└──────────────────────┬──────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│              LlmAgent (Gemini Model)                │
│  1. Analizuje zapytanie                             │
│  2. Sprawdza dostępne tools                         │
│  3. Decyduje czy użyć tool                          │
└──────────────────────┬──────────────────────────────┘
                       ↓
         ┌─────────────┴─────────────┐
         │   Czy użyć tool?          │
         └─────────────┬─────────────┘
                       ↓
         ┌─────────────┴─────────────┐
         │ TAK                   NIE │
         ↓                           ↓
┌────────────────────┐    ┌──────────────────┐
│  Tool Execution    │    │  Direct Response │
│  1. Wybór tool     │    │  (bez tool)      │
│  2. Parametry      │    └──────────────────┘
│  3. Wywołanie      │
│  4. Wynik          │
└────────┬───────────┘
         ↓
┌─────────────────────────────────────────────────────┐
│         Agent formułuje finalną odpowiedź           │
│         (używając wyniku z tool)                    │
└─────────────────────────────────────────────────────┘
```

### Wymagania dla funkcji Tool

Aby funkcja Python mogła być użyta jako tool w ADK, MUSI spełniać:

1. **Type Annotations** - wszystkie parametry i return type
2. **Docstring** - opis funkcji i parametrów
3. **Jasna nazwa** - opisowa, zrozumiała dla LLM

**Przykład poprawnego tool:**

```python
def search_products(category: str, max_price: float) -> list[dict]:
    """
    Wyszukuje produkty w danej kategorii do określonej ceny.
    
    Args:
        category: Kategoria produktów (np. 'elektronika', 'książki')
        max_price: Maksymalna cena w PLN
    
    Returns:
        Lista słowników z produktami spełniającymi kryteria
    """
    # Implementacja...
    return results
```

---

## 🔑 Kluczowe Koncepcje

### 1. **Docstring jako Dokumentacja dla LLM**

LLM **czyta docstring** aby zrozumieć:
- Co robi funkcja
- Kiedy jej użyć
- Jakie parametry przyjmuje
- Co zwraca

**Dobry docstring:**
```python
def send_email(to: str, subject: str, body: str) -> dict:
    """
    Wysyła email do określonego odbiorcy.
    
    Użyj tej funkcji gdy użytkownik chce wysłać wiadomość email.
    
    Args:
        to: Adres email odbiorcy (format: user@example.com)
        subject: Temat wiadomości (max 100 znaków)
        body: Treść wiadomości (może zawierać HTML)
    
    Returns:
        Słownik z kluczami:
        - success: bool - czy wysłano pomyślnie
        - message_id: str - ID wiadomości
        - error: str - komunikat błędu (jeśli wystąpił)
    
    Examples:
        send_email("jan@example.com", "Spotkanie", "Spotkanie o 15:00")
    """
```

**Zły docstring:**
```python
def send_email(to: str, subject: str, body: str) -> dict:
    """Sends email."""  # ❌ Za mało informacji!
```

### 2. **Type Annotations - Klucz do Sukcesu**

Type annotations pomagają LLM zrozumieć:
- Jakiego typu danych oczekuje funkcja
- Co zwraca funkcja

**Wspierane typy:**
- `str`, `int`, `float`, `bool`
- `list`, `dict`, `tuple`
- `Optional[T]` - opcjonalny parametr
- `Union[T1, T2]` - jeden z typów
- `list[dict]` - lista słowników
- Pydantic `BaseModel` - strukturalne dane

**Przykład z Pydantic:**
```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str = Field(description="Nazwa produktu")
    price: float = Field(description="Cena w PLN")
    in_stock: bool = Field(description="Czy dostępny")

def get_product(product_id: int) -> Product:
    """Pobiera szczegóły produktu po ID."""
    # ...
```

### 3. **Walidacja Wejścia**

**Zawsze waliduj** parametry wejściowe!

**Dlaczego?**
- LLM może przekazać niepoprawne dane
- Użytkownik może podać błędne informacje
- Bezpieczeństwo i stabilność systemu

**Przykład walidacji:**
```python
def add_product(name: str, price: float, quantity: int) -> dict:
    """Dodaje produkt do inwentarza."""
    
    # Walidacja 1: Nazwa nie może być pusta
    if not name or not name.strip():
        return {"error": "Nazwa produktu nie może być pusta"}
    
    # Walidacja 2: Cena musi być dodatnia
    if price <= 0:
        return {"error": f"Cena musi być dodatnia, podano: {price}"}
    
    # Walidacja 3: Ilość musi być dodatnia
    if quantity <= 0:
        return {"error": f"Ilość musi być dodatnia, podano: {quantity}"}
    
    # Walidacja 4: Limit bezpieczeństwa
    if quantity > 10000:
        return {"error": "Nie można dodać więcej niż 10000 sztuk na raz"}
    
    # Wszystko OK - wykonaj operację
    # ...
```

### 4. **Zwracanie Strukturalnych Wyników**

**Lepiej zwracać słowniki** niż proste stringi:

**Źle:**
```python
def add_product(name: str, quantity: int) -> str:
    return f"Dodano {quantity} sztuk {name}"  # ❌ Trudne do parsowania
```

**Dobrze:**
```python
def add_product(name: str, quantity: int) -> dict:
    return {
        "success": True,
        "product": name,
        "quantity_added": quantity,
        "new_total": 150,
        "message": f"Dodano {quantity} sztuk {name}"
    }  # ✅ Strukturalne, łatwe do użycia
```

---

## 💼 Przypadki Użycia Biznesowego

### 1. **E-commerce: Zarządzanie Produktami**

**Scenariusz:** Sklep internetowy potrzebuje agenta do zarządzania inwentarzem.

**Implementacja:**
```python
# Narzędzia dla e-commerce
def search_products(query: str, category: str = None) -> list[dict]:
    """Wyszukuje produkty w katalogu."""
    # Połączenie z bazą danych
    # ...

def update_stock(product_id: int, quantity: int) -> dict:
    """Aktualizuje stan magazynowy produktu."""
    # Walidacja i aktualizacja
    # ...

def create_order(customer_id: int, products: list[dict]) -> dict:
    """Tworzy nowe zamówienie."""
    # Logika zamówienia
    # ...

# Agent
inventory_agent = LlmAgent(
    name="inventory_manager",
    model="gemini-2.5-flash",
    instruction="""Jesteś menedżerem inwentarza sklepu TechShop.
    
    Pomagasz w:
    - Wyszukiwaniu produktów
    - Aktualizacji stanów magazynowych
    - Tworzeniu zamówień
    
    Zawsze waliduj dane przed wykonaniem operacji!
    """,
    tools=[search_products, update_stock, create_order]
)
```

**Korzyści biznesowe:**
- ⏱️ Szybsze zarządzanie inwentarzem (sekundy vs minuty)
- 📉 Mniej błędów ludzkich
- 🤖 Automatyzacja rutynowych zadań
- 📊 Lepsze śledzenie operacji

### 2. **CRM: Zarządzanie Klientami**

**Scenariusz:** Firma potrzebuje agenta do zarządzania danymi klientów w CRM.

**Implementacja:**
```python
def get_customer(customer_id: int) -> dict:
    """Pobiera dane klienta z CRM."""
    # Zapytanie do CRM API
    # ...

def update_customer_notes(customer_id: int, note: str) -> dict:
    """Dodaje notatkę do profilu klienta."""
    # Aktualizacja w CRM
    # ...

def create_task(customer_id: int, task_type: str, description: str) -> dict:
    """Tworzy zadanie związane z klientem."""
    # Tworzenie task w CRM
    # ...

crm_agent = LlmAgent(
    name="crm_assistant",
    model="gemini-2.5-flash",
    instruction="""Jesteś asystentem CRM dla zespołu sprzedaży.

    Pomagasz w:
    - Wyszukiwaniu informacji o klientach
    - Dodawaniu notatek do profili
    - Tworzeniu zadań follow-up

    Zawsze zachowuj poufność danych klientów!
    """,
    tools=[get_customer, update_customer_notes, create_task]
)
```

**Korzyści biznesowe:**
- 📈 Lepsza obsługa klientów (szybszy dostęp do danych)
- 📝 Automatyczne dokumentowanie interakcji
- 🎯 Mniej pominiętych follow-upów
- 💰 Wyższy conversion rate

### 3. **Finanse: Raportowanie i Analiza**

**Scenariusz:** Dział finansowy potrzebuje agenta do generowania raportów.

**Implementacja:**
```python
def get_revenue_report(start_date: str, end_date: str) -> dict:
    """Generuje raport przychodów za okres."""
    # Zapytanie do systemu finansowego
    # ...

def calculate_expenses(category: str, month: str) -> dict:
    """Oblicza wydatki w kategorii za miesiąc."""
    # Analiza wydatków
    # ...

def generate_invoice(customer_id: int, items: list[dict]) -> dict:
    """Generuje fakturę dla klienta."""
    # Tworzenie faktury
    # ...

finance_agent = LlmAgent(
    name="finance_assistant",
    model="gemini-2.5-flash",
    instruction="""Jesteś asystentem finansowym.

    Pomagasz w:
    - Generowaniu raportów przychodów i wydatków
    - Analizie finansowej
    - Tworzeniu faktur

    Wszystkie kwoty podawaj w PLN z dokładnością do 2 miejsc po przecinku.
    """,
    tools=[get_revenue_report, calculate_expenses, generate_invoice]
)
```

**Korzyści biznesowe:**
- 📊 Szybsze generowanie raportów (minuty vs godziny)
- 🎯 Mniej błędów w obliczeniach
- 💼 Więcej czasu na analizę strategiczną
- 📈 Lepsze decyzje biznesowe (szybszy dostęp do danych)

---

## ✅ Najlepsze Praktyki

### 1. **Projektowanie Tools**

**DO:**
- ✅ **Jedna funkcja = jedno zadanie** (Single Responsibility)
- ✅ **Jasne, opisowe nazwy** (`get_customer` zamiast `gc`)
- ✅ **Szczegółowe docstringi** z przykładami
- ✅ **Walidacja wszystkich parametrów**
- ✅ **Zwracanie strukturalnych wyników** (dict zamiast str)
- ✅ **Obsługa błędów** (try/except, komunikaty)

**NIE:**
- ❌ Nie twórz "super-funkcji" robiących wszystko
- ❌ Nie używaj skrótowych nazw
- ❌ Nie pomijaj docstringów
- ❌ Nie zakładaj że dane są poprawne
- ❌ Nie rzucaj wyjątków bez obsługi

### 2. **Nazewnictwo Funkcji**

**Dobre nazwy:**
```python
get_customer()          # Jasne - pobiera klienta
create_order()          # Jasne - tworzy zamówienie
calculate_total()       # Jasne - oblicza sumę
send_notification()     # Jasne - wysyła powiadomienie
```

**Złe nazwy:**
```python
do_stuff()             # ❌ Co robi?
process()              # ❌ Co przetwarza?
handle()               # ❌ Co obsługuje?
x()                    # ❌ Kompletnie niejasne
```

### 3. **Struktura Zwracanych Danych**

**Wzorzec sukces/błąd:**
```python
def create_order(customer_id: int, items: list) -> dict:
    """Tworzy zamówienie."""

    # Walidacja
    if not items:
        return {
            "success": False,
            "error": "Lista produktów nie może być pusta",
            "order_id": None
        }

    # Operacja
    try:
        order_id = database.create_order(customer_id, items)
        return {
            "success": True,
            "order_id": order_id,
            "message": f"Zamówienie {order_id} utworzone pomyślnie",
            "items_count": len(items)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "order_id": None
        }
```

### 4. **Testowanie Tools**

**Zawsze testuj:**
- ✅ Poprawne dane wejściowe
- ✅ Niepoprawne dane (walidacja)
- ✅ Przypadki brzegowe (0, None, puste stringi)
- ✅ Błędy zewnętrznych systemów (API down, baza niedostępna)

**Przykład testów:**
```python
def test_add_product():
    # Test 1: Poprawne dane
    result = add_product("Laptop", 2999.99, 10)
    assert result["success"] == True

    # Test 2: Ujemna cena
    result = add_product("Laptop", -100, 10)
    assert result["success"] == False
    assert "cena" in result["error"].lower()

    # Test 3: Pusta nazwa
    result = add_product("", 100, 10)
    assert result["success"] == False

    # Test 4: Limit przekroczony
    result = add_product("Laptop", 100, 99999)
    assert result["success"] == False
```

### 5. **Bezpieczeństwo**

**Zasady bezpieczeństwa:**
- 🔒 **Nigdy nie wykonuj SQL injection-prone queries**
- 🔒 **Waliduj wszystkie dane wejściowe**
- 🔒 **Nie zwracaj wrażliwych danych** (hasła, tokeny)
- 🔒 **Loguj operacje** (audit trail)
- 🔒 **Używaj uprawnień** (nie dawaj agentowi admin access)

**Przykład bezpiecznego query:**
```python
# ❌ ŹLE - SQL Injection!
def get_user(username: str) -> dict:
    query = f"SELECT * FROM users WHERE username = '{username}'"
    # Użytkownik może podać: "admin' OR '1'='1"

# ✅ DOBRZE - Parametryzowane query
def get_user(username: str) -> dict:
    query = "SELECT * FROM users WHERE username = ?"
    result = database.execute(query, (username,))
```

---

## ⚠️ Typowe Pułapki

### 1. **Brak Walidacji**

**Problem:**
```python
def add_product(name: str, price: float) -> str:
    products[name] = price  # ❌ Co jeśli price = -100?
    return f"Dodano {name}"
```

**Rozwiązanie:**
```python
def add_product(name: str, price: float) -> dict:
    if price <= 0:
        return {"error": "Cena musi być dodatnia"}
    if not name.strip():
        return {"error": "Nazwa nie może być pusta"}

    products[name] = price
    return {"success": True, "product": name, "price": price}
```

### 2. **Zbyt Ogólne Docstringi**

**Problem:**
```python
def process_data(data: dict) -> dict:
    """Processes data."""  # ❌ LLM nie wie kiedy użyć!
```

**Rozwiązanie:**
```python
def process_order(order_data: dict) -> dict:
    """
    Przetwarza zamówienie klienta i tworzy wpis w systemie.

    Użyj tej funkcji gdy klient składa zamówienie lub gdy
    potrzebujesz utworzyć nowe zamówienie w systemie.

    Args:
        order_data: Słownik z kluczami:
            - customer_id: int - ID klienta
            - items: list[dict] - Lista produktów
            - shipping_address: str - Adres dostawy

    Returns:
        Słownik z wynikiem operacji i ID zamówienia
    """
```

### 3. **Brak Obsługi Błędów**

**Problem:**
```python
def get_customer(customer_id: int) -> dict:
    return database.query(customer_id)  # ❌ Co jeśli baza nie działa?
```

**Rozwiązanie:**
```python
def get_customer(customer_id: int) -> dict:
    try:
        customer = database.query(customer_id)
        if not customer:
            return {"error": f"Klient {customer_id} nie istnieje"}
        return {"success": True, "customer": customer}
    except DatabaseError as e:
        return {"error": f"Błąd bazy danych: {str(e)}"}
    except Exception as e:
        return {"error": f"Nieoczekiwany błąd: {str(e)}"}
```

### 4. **Zbyt Wiele Parametrów**

**Problem:**
```python
def create_user(name, email, phone, address, city, zip, country, age, gender):
    # ❌ LLM może się pomylić w kolejności!
```

**Rozwiązanie:**
```python
from pydantic import BaseModel

class UserData(BaseModel):
    name: str
    email: str
    phone: str
    address: str
    city: str
    zip_code: str
    country: str
    age: int
    gender: str

def create_user(user_data: UserData) -> dict:
    # ✅ Strukturalne dane, łatwiejsze dla LLM
```

### 5. **Brak Logowania**

**Problem:** Nie wiesz co agent robi.

**Rozwiązanie:**
```python
import logging

def delete_product(product_id: int) -> dict:
    logging.info(f"Attempting to delete product {product_id}")

    try:
        result = database.delete(product_id)
        logging.info(f"Successfully deleted product {product_id}")
        return {"success": True}
    except Exception as e:
        logging.error(f"Failed to delete product {product_id}: {e}")
        return {"error": str(e)}
```

---

## 🔗 Odniesienia do Dokumentacji ADK

### Oficjalna Dokumentacja
- [Tools Overview](https://google.github.io/adk-docs/tools/)
- [Function Calling](https://ai.google.dev/gemini-api/docs/function-calling)
- [Custom Tools](https://google.github.io/adk-docs/tools/custom-tools/)

### Przykłady
- [Tool Examples](https://github.com/google/adk-examples/tree/main/tools)

---

## 📝 Podsumowanie

**Kluczowe wnioski z Module 02:**

1. **Tools rozszerzają możliwości agenta** - od konwersacji do akcji
2. **Docstringi są kluczowe** - LLM czyta je aby zrozumieć narzędzie
3. **Walidacja jest obowiązkowa** - nigdy nie ufaj danym wejściowym
4. **Strukturalne wyniki** - dict > str
5. **Testowanie i bezpieczeństwo** - zawsze priorytet

**Następne kroki:**
- Module 03: RAG - integracja z bazami wiedzy
- Module 04: Sequential Agents - orkiestracja wielu agentów
- Module 05: Human-in-the-Loop - zatwierdzanie przez człowieka

---

*"Właściwe narzędzie do właściwej pracy ułatwia życie programisty!"* 🔧


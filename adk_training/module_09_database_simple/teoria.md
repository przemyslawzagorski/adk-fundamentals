# Module 09: Database Simple - Teoria

## 🎯 Kluczowe Koncepcje

### Integracja Bazy Danych z ADK

ADK pozwala agentom **bezpośrednio** operować na bazach danych przez funkcje Python jako tools.

```python
def get_customer(customer_id: int) -> str:
    conn = sqlite3.connect("db.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
    row = cursor.fetchone()
    conn.close()
    return format_result(row)

agent = LlmAgent(
    tools=[get_customer]  # Agent może wywoływać SQL!
)
```

### CRUD Operations

| Operacja | SQL | Funkcja Python |
|----------|-----|----------------|
| **Create** | INSERT | `add_customer()` |
| **Read** | SELECT | `get_customer()`, `list_customers()` |
| **Update** | UPDATE | `update_customer()` |
| **Delete** | DELETE | `delete_customer()` |

---

## 💼 Przypadki Użycia Biznesowego

### 1. CRM - Zarządzanie Klientami

```python
# Agent CRM z pełnym CRUD
crm_agent = LlmAgent(
    instruction="Zarządzaj bazą klientów",
    tools=[
        add_customer,
        get_customer,
        update_customer,
        delete_customer,
        search_customers
    ]
)
```

**Korzyści:** Naturalny język zamiast SQL, automatyzacja, dostęp 24/7.

### 2. E-commerce - Zarządzanie Produktami

```python
def add_product(name: str, price: float, stock: int) -> str:
    # INSERT INTO products...

def update_stock(product_id: int, quantity: int) -> str:
    # UPDATE products SET stock = stock + quantity...

def search_products(query: str, max_price: float = None) -> str:
    # SELECT * FROM products WHERE name LIKE ? AND price <= ?...

inventory_agent = LlmAgent(
    tools=[add_product, update_stock, search_products]
)
```

### 3. HR - Baza Pracowników

```python
def add_employee(name: str, position: str, salary: float) -> str:
    # INSERT INTO employees...

def get_employees_by_department(department: str) -> str:
    # SELECT * FROM employees WHERE department = ?...

hr_agent = LlmAgent(
    tools=[add_employee, get_employees_by_department]
)
```

---

## ✅ Najlepsze Praktyki

### 1. Parametryzowane Queries (SQL Injection Prevention)

**❌ NIEBEZPIECZNE:**
```python
def get_customer(name: str) -> str:
    query = f"SELECT * FROM customers WHERE name = '{name}'"  # SQL Injection!
    cursor.execute(query)
```

**✅ BEZPIECZNE:**
```python
def get_customer(name: str) -> str:
    query = "SELECT * FROM customers WHERE name = ?"
    cursor.execute(query, (name,))  # Parametryzowane
```

### 2. Walidacja Danych

```python
def add_customer(name: str, email: str) -> str:
    # Walidacja
    if not name or len(name) < 2:
        return "❌ Nazwa musi mieć min 2 znaki"
    
    if "@" not in email:
        return "❌ Niepoprawny email"
    
    # Operacja
    try:
        cursor.execute("INSERT INTO customers (name, email) VALUES (?, ?)", (name, email))
        conn.commit()
        return "✅ Dodano klienta"
    except sqlite3.IntegrityError:
        return "❌ Email już istnieje"
```

### 3. Obsługa Błędów

```python
def get_customer(customer_id: int) -> str:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return f"❌ Nie znaleziono klienta {customer_id}"
        
        return format_customer(row)
    
    except sqlite3.Error as e:
        return f"❌ Błąd bazy danych: {str(e)}"
    except Exception as e:
        return f"❌ Nieoczekiwany błąd: {str(e)}"
```

### 4. Formatowanie Wyników

**❌ Źle:**
```python
return str(row)  # (1, 'Jan', 'jan@example.com', '123456789')
```

**✅ Dobrze:**
```python
return f"""
📋 Klient ID: {row[0]}
Imię: {row[1]}
Email: {row[2]}
Telefon: {row[3]}
"""
```

### 5. Transakcje

```python
def transfer_funds(from_account: int, to_account: int, amount: float) -> str:
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        
        # Transakcja: obie operacje albo żadna
        cursor.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, from_account))
        cursor.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, to_account))
        
        conn.commit()
        return "✅ Transfer zakończony"
    
    except Exception as e:
        conn.rollback()  # Cofnij w przypadku błędu
        return f"❌ Transfer nieudany: {str(e)}"
    finally:
        conn.close()
```

---

## ⚠️ Typowe Pułapki

### 1. Brak Zamykania Połączeń

**Problem:** `conn.close()` nie wywołane → wyciek zasobów.

**Rozwiązanie:** Użyj context manager:
```python
def get_customer(customer_id: int) -> str:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        return cursor.fetchone()
    # conn.close() automatycznie
```

### 2. SQL Injection

**Problem:** Konkatenacja stringów w SQL.

**Rozwiązanie:** ZAWSZE używaj parametryzowanych queries (patrz najlepsze praktyki).

### 3. Brak Walidacji

**Problem:** Agent może wstawić niepoprawne dane.

**Rozwiązanie:** Waliduj WSZYSTKIE dane wejściowe.

### 4. Brak Obsługi Duplikatów

**Problem:** Próba dodania emaila który już istnieje → crash.

**Rozwiązanie:**
```python
try:
    cursor.execute("INSERT INTO customers (email) VALUES (?)", (email,))
except sqlite3.IntegrityError:
    return "❌ Email już istnieje"
```

---

## 🔗 Odniesienia

### SQLite
- [SQLite Python Docs](https://docs.python.org/3/library/sqlite3.html)
- [SQL Tutorial](https://www.sqlitetutorial.net/)

### ADK
- [Tools Overview](https://google.github.io/adk-docs/tools/)

---

## 📝 Podsumowanie

| Koncepcja | Kluczowy Punkt |
|-----------|----------------|
| **CRUD** | Create, Read, Update, Delete |
| **Parametryzowane queries** | Zapobiega SQL injection |
| **Walidacja** | Sprawdzaj dane przed INSERT/UPDATE |
| **Obsługa błędów** | try/except dla wszystkich operacji DB |
| **Context manager** | `with sqlite3.connect()` auto-zamyka |
| **Formatowanie** | Czytelne wyniki dla użytkownika |

**Następny krok:** Module 11 - Memory Bank (pamięć długoterminowa)


"""
Moduł 9: Database Simple - ROZWIĄZANIA ĆWICZEŃ
===============================================
Ćwiczenia (zaproponowane):
1. Dodaj funkcję update_customer() - aktualizacja danych klienta
2. Dodaj funkcję delete_customer() - usuwanie klienta
3. Dodaj funkcję search_customers() - wyszukiwanie po kryteriach
4. Dodaj funkcję get_customer_stats() - statystyki klientów
"""

import os
import sqlite3
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from google.adk.agents import LlmAgent

load_dotenv()
MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")
DB_PATH = "customers.db"

# =============================================================================
# INICJALIZACJA BAZY DANYCH
# =============================================================================

def init_database():
    """Tworzy tabelę customers jeśli nie istnieje."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            company TEXT,
            status TEXT DEFAULT 'active'
        )
    """)
    conn.commit()
    conn.close()

init_database()

# =============================================================================
# FUNKCJE BAZOWE (z oryginalnego agent.py)
# =============================================================================

def add_customer(name: str, email: str, phone: str = "", company: str = "") -> str:
    """Dodaje nowego klienta do bazy."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO customers (name, email, phone, company) VALUES (?, ?, ?, ?)",
            (name, email, phone, company)
        )
        conn.commit()
        customer_id = cursor.lastrowid
        conn.close()
        return f"✅ Dodano klienta: {name} (ID: {customer_id})"
    except sqlite3.IntegrityError:
        return f"❌ Błąd: Email {email} już istnieje w bazie"
    except Exception as e:
        return f"❌ Błąd: {str(e)}"

def get_customer(customer_id: int) -> str:
    """Pobiera dane klienta po ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return f"""
📋 Klient ID: {row[0]}
Imię: {row[1]}
Email: {row[2]}
Telefon: {row[3] or 'brak'}
Firma: {row[4] or 'brak'}
Status: {row[5]}
"""
    return f"❌ Nie znaleziono klienta o ID: {customer_id}"

def list_customers() -> str:
    """Wyświetla wszystkich klientów."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, company, status FROM customers")
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return "📭 Baza klientów jest pusta"
    
    result = "📋 LISTA KLIENTÓW:\n\n"
    for row in rows:
        result += f"ID: {row[0]} | {row[1]} | {row[2]} | {row[3] or 'brak firmy'} | Status: {row[4]}\n"
    return result

# =============================================================================
# ĆWICZENIE 1: UPDATE_CUSTOMER
# =============================================================================

def update_customer(
    customer_id: int,
    name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    company: Optional[str] = None,
    status: Optional[str] = None
) -> str:
    """
    Aktualizuje dane klienta. Tylko podane pola zostaną zaktualizowane.
    
    Args:
        customer_id: ID klienta do aktualizacji
        name: Nowe imię (opcjonalne)
        email: Nowy email (opcjonalne)
        phone: Nowy telefon (opcjonalne)
        company: Nowa firma (opcjonalne)
        status: Nowy status (opcjonalne): 'active', 'inactive', 'lead'
    """
    # Sprawdź czy klient istnieje
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM customers WHERE id = ?", (customer_id,))
    if not cursor.fetchone():
        conn.close()
        return f"❌ Nie znaleziono klienta o ID: {customer_id}"
    
    # Buduj query dynamicznie (tylko dla podanych pól)
    updates = []
    params = []
    
    if name is not None:
        updates.append("name = ?")
        params.append(name)
    if email is not None:
        updates.append("email = ?")
        params.append(email)
    if phone is not None:
        updates.append("phone = ?")
        params.append(phone)
    if company is not None:
        updates.append("company = ?")
        params.append(company)
    if status is not None:
        updates.append("status = ?")
        params.append(status)
    
    if not updates:
        conn.close()
        return "⚠️ Nie podano żadnych pól do aktualizacji"
    
    params.append(customer_id)
    query = f"UPDATE customers SET {', '.join(updates)} WHERE id = ?"
    
    try:
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        return f"✅ Zaktualizowano klienta ID: {customer_id}"
    except sqlite3.IntegrityError:
        conn.close()
        return f"❌ Błąd: Email już istnieje w bazie"
    except Exception as e:
        conn.close()
        return f"❌ Błąd: {str(e)}"

# =============================================================================
# ĆWICZENIE 2: DELETE_CUSTOMER
# =============================================================================

def delete_customer(customer_id: int, confirm: bool = False) -> str:
    """
    Usuwa klienta z bazy (wymaga potwierdzenia).
    
    Args:
        customer_id: ID klienta do usunięcia
        confirm: Potwierdzenie usunięcia (musi być True)
    """
    if not confirm:
        return f"⚠️ Usunięcie wymaga potwierdzenia! Ustaw confirm=True aby usunąć klienta {customer_id}"
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Sprawdź czy istnieje
    cursor.execute("SELECT name FROM customers WHERE id = ?", (customer_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return f"❌ Nie znaleziono klienta o ID: {customer_id}"
    
    customer_name = row[0]
    
    # Usuń
    cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
    conn.commit()
    conn.close()
    
    return f"✅ Usunięto klienta: {customer_name} (ID: {customer_id})"

# =============================================================================
# ĆWICZENIE 3: SEARCH_CUSTOMERS
# =============================================================================

def search_customers(
    name: Optional[str] = None,
    email: Optional[str] = None,
    company: Optional[str] = None,
    status: Optional[str] = None
) -> str:
    """
    Wyszukuje klientów po kryteriach (częściowe dopasowanie).

    Args:
        name: Szukaj po imieniu (częściowe dopasowanie)
        email: Szukaj po emailu (częściowe dopasowanie)
        company: Szukaj po firmie (częściowe dopasowanie)
        status: Szukaj po statusie (dokładne dopasowanie)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Buduj query dynamicznie
    conditions = []
    params = []

    if name:
        conditions.append("name LIKE ?")
        params.append(f"%{name}%")
    if email:
        conditions.append("email LIKE ?")
        params.append(f"%{email}%")
    if company:
        conditions.append("company LIKE ?")
        params.append(f"%{company}%")
    if status:
        conditions.append("status = ?")
        params.append(status)

    if not conditions:
        conn.close()
        return "⚠️ Podaj przynajmniej jedno kryterium wyszukiwania"

    query = f"SELECT id, name, email, company, status FROM customers WHERE {' AND '.join(conditions)}"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "📭 Nie znaleziono klientów spełniających kryteria"

    result = f"🔍 Znaleziono {len(rows)} klientów:\n\n"
    for row in rows:
        result += f"ID: {row[0]} | {row[1]} | {row[2]} | {row[3] or 'brak'} | {row[4]}\n"
    return result

# =============================================================================
# ĆWICZENIE 4: GET_CUSTOMER_STATS
# =============================================================================

def get_customer_stats() -> str:
    """Zwraca statystyki bazy klientów."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Łączna liczba klientów
    cursor.execute("SELECT COUNT(*) FROM customers")
    total = cursor.fetchone()[0]

    # Liczba po statusach
    cursor.execute("SELECT status, COUNT(*) FROM customers GROUP BY status")
    status_counts = cursor.fetchall()

    # Top 5 firm
    cursor.execute("""
        SELECT company, COUNT(*) as count
        FROM customers
        WHERE company IS NOT NULL AND company != ''
        GROUP BY company
        ORDER BY count DESC
        LIMIT 5
    """)
    top_companies = cursor.fetchall()

    conn.close()

    # Formatuj wynik
    result = f"""
📊 STATYSTYKI BAZY KLIENTÓW

Łączna liczba klientów: {total}

Podział po statusach:
"""
    for status, count in status_counts:
        result += f"  • {status}: {count}\n"

    if top_companies:
        result += "\nTop 5 firm (najwięcej klientów):\n"
        for company, count in top_companies:
            result += f"  • {company}: {count} klientów\n"

    return result

# =============================================================================
# AGENT Z WSZYSTKIMI NARZĘDZIAMI
# =============================================================================

root_agent = LlmAgent(
    name="menedzer_klientow",
    model=MODEL,
    instruction="""Jesteś Menedżerem Bazy Klientów (CRM).

DOSTĘPNE OPERACJE:

1. **Dodawanie klienta**: add_customer(name, email, phone, company)
2. **Pobieranie klienta**: get_customer(customer_id)
3. **Lista wszystkich**: list_customers()
4. **Aktualizacja**: update_customer(customer_id, name=..., email=..., ...)
5. **Usuwanie**: delete_customer(customer_id, confirm=True)
6. **Wyszukiwanie**: search_customers(name=..., email=..., company=..., status=...)
7. **Statystyki**: get_customer_stats()

ZASADY:
- Przy usuwaniu ZAWSZE pytaj użytkownika o potwierdzenie
- Przy aktualizacji podawaj tylko pola które mają się zmienić
- Przy wyszukiwaniu używaj częściowego dopasowania (nie musi być dokładne)
- Statusy: 'active', 'inactive', 'lead'

Bądź pomocny i profesjonalny!
""",
    description="Menedżer bazy klientów z pełnym CRUD",
    tools=[
        add_customer,
        get_customer,
        list_customers,
        update_customer,
        delete_customer,
        search_customers,
        get_customer_stats,
    ]
)

# =============================================================================
# PRZYKŁADY TESTOWANIA
# =============================================================================
"""
TESTOWANIE:

1. Dodawanie:
   "Dodaj klienta Jan Kowalski, email jan@example.com, firma TechCorp"

2. Listowanie:
   "Pokaż wszystkich klientów"

3. Aktualizacja (Ćwiczenie 1):
   "Zmień email klienta ID 1 na nowy@example.com"
   "Zmień status klienta ID 2 na inactive"

4. Usuwanie (Ćwiczenie 2):
   "Usuń klienta ID 3"
   → Agent powinien zapytać o potwierdzenie

5. Wyszukiwanie (Ćwiczenie 3):
   "Znajdź klientów z firmy Tech"
   "Znajdź klientów o statusie active"
   "Znajdź klientów z emailem @gmail.com"

6. Statystyki (Ćwiczenie 4):
   "Pokaż statystyki bazy klientów"

URUCHOMIENIE:
adk web
"""


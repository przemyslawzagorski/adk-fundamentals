"""
Moduł 15: Gmail Integration - ROZWIĄZANIA ĆWICZEŃ
==================================================
Ćwiczenia:
1. Dodaj funkcję mark_as_read() - oznaczanie emaili jako przeczytane
2. Dodaj funkcję search_emails_by_sender() - wyszukiwanie po nadawcy
3. Dodaj funkcję get_unread_count() - liczba nieprzeczytanych emaili
"""

import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
from google.adk.agents import LlmAgent

load_dotenv()
MODEL = os.getenv("ADK_MODEL", "gemini-2.5-flash")

# =============================================================================
# MOCK GMAIL API (dla celów demonstracyjnych)
# =============================================================================
# W prawdziwej implementacji użyj: from google.adk.tools import GmailTool

MOCK_EMAILS = [
    {
        "id": "1",
        "from": "boss@company.com",
        "subject": "Urgent: Q4 Report",
        "snippet": "Please send me the Q4 report by EOD...",
        "read": False,
        "labels": ["INBOX", "IMPORTANT"]
    },
    {
        "id": "2",
        "from": "newsletter@tech.com",
        "subject": "Weekly Tech News",
        "snippet": "Top 10 tech trends this week...",
        "read": False,
        "labels": ["INBOX"]
    },
    {
        "id": "3",
        "from": "client@example.com",
        "subject": "Re: Project Timeline",
        "snippet": "Thanks for the update. Can we schedule a call?",
        "read": True,
        "labels": ["INBOX", "SENT"]
    },
]

# =============================================================================
# FUNKCJE BAZOWE (symulacja Gmail API)
# =============================================================================

def list_emails(max_results: int = 10) -> str:
    """Wyświetla ostatnie emaile."""
    emails = MOCK_EMAILS[:max_results]
    
    if not emails:
        return "📭 Brak emaili"
    
    result = f"📧 Ostatnie {len(emails)} emaili:\n\n"
    for email in emails:
        status = "✉️" if not email["read"] else "📖"
        result += f"{status} ID: {email['id']}\n"
        result += f"   Od: {email['from']}\n"
        result += f"   Temat: {email['subject']}\n"
        result += f"   Podgląd: {email['snippet'][:50]}...\n\n"
    
    return result

def send_email(to: str, subject: str, body: str) -> str:
    """Wysyła email."""
    # W prawdziwej implementacji: wywołaj Gmail API
    return f"✅ Wysłano email do {to}\nTemat: {subject}"

def get_email_details(email_id: str) -> str:
    """Pobiera szczegóły emaila."""
    email = next((e for e in MOCK_EMAILS if e["id"] == email_id), None)
    
    if not email:
        return f"❌ Nie znaleziono emaila o ID: {email_id}"
    
    return f"""
📧 Email ID: {email['id']}
Od: {email['from']}
Temat: {email['subject']}
Status: {'Nieprzeczytany' if not email['read'] else 'Przeczytany'}
Etykiety: {', '.join(email['labels'])}

Treść:
{email['snippet']}
"""

# =============================================================================
# ĆWICZENIE 1: MARK_AS_READ
# =============================================================================

def mark_as_read(email_id: str) -> str:
    """
    Oznacza email jako przeczytany.
    
    Args:
        email_id: ID emaila do oznaczenia
    """
    email = next((e for e in MOCK_EMAILS if e["id"] == email_id), None)
    
    if not email:
        return f"❌ Nie znaleziono emaila o ID: {email_id}"
    
    if email["read"]:
        return f"ℹ️ Email {email_id} jest już oznaczony jako przeczytany"
    
    # Oznacz jako przeczytany
    email["read"] = True
    
    return f"✅ Oznaczono email {email_id} jako przeczytany\nTemat: {email['subject']}"

# =============================================================================
# ĆWICZENIE 2: SEARCH_EMAILS_BY_SENDER
# =============================================================================

def search_emails_by_sender(sender_email: str) -> str:
    """
    Wyszukuje emaile od określonego nadawcy.
    
    Args:
        sender_email: Adres email nadawcy (częściowe dopasowanie)
    """
    # Wyszukaj emaile (case-insensitive, częściowe dopasowanie)
    matching_emails = [
        e for e in MOCK_EMAILS 
        if sender_email.lower() in e["from"].lower()
    ]
    
    if not matching_emails:
        return f"📭 Nie znaleziono emaili od: {sender_email}"
    
    result = f"🔍 Znaleziono {len(matching_emails)} emaili od '{sender_email}':\n\n"
    for email in matching_emails:
        status = "✉️" if not email["read"] else "📖"
        result += f"{status} ID: {email['id']}\n"
        result += f"   Od: {email['from']}\n"
        result += f"   Temat: {email['subject']}\n"
        result += f"   Data: {email.get('date', 'N/A')}\n\n"
    
    return result

# =============================================================================
# AGENT Z WSZYSTKIMI NARZĘDZIAMI
# =============================================================================

root_agent = LlmAgent(
    name="asystent_gmail",
    model=MODEL,
    instruction="""Jesteś asystentem Gmail - pomagasz zarządzać skrzynką pocztową.

DOSTĘPNE OPERACJE:

📧 PODSTAWOWE:
1. list_emails() - wyświetl ostatnie emaile
2. send_email(to, subject, body) - wyślij email
3. get_email_details(email_id) - szczegóły emaila

✅ NOWE (z ćwiczeń):
4. mark_as_read(email_id) - oznacz jako przeczytany
5. search_emails_by_sender(sender_email) - znajdź emaile od nadawcy
6. get_unread_count() - ile nieprzeczytanych

🎁 BONUSOWE:
7. archive_email(email_id) - archiwizuj email
8. search_emails_by_subject(keyword) - szukaj po temacie

ZASADY:
- Przy wysyłaniu emaili zawsze potwierdzaj szczegóły
- Podsumowuj wyniki wyszukiwania
- Sugeruj akcje (np. "Masz 5 nieprzeczytanych - chcesz je przejrzeć?")

Bądź pomocny i proaktywny!
""",
    description="Asystent Gmail z pełnym zarządzaniem skrzynką",
    tools=[
        list_emails,
        send_email,
        get_email_details,
        mark_as_read,
        search_emails_by_sender,
        get_unread_count,
        archive_email,
        search_emails_by_subject,
    ]
)

# =============================================================================
# PRZYKŁADY TESTOWANIA
# =============================================================================
"""
TESTOWANIE:

1. Podstawowe operacje:
   "Pokaż moje ostatnie emaile"
   "Wyślij email do jan@example.com z tematem 'Spotkanie' i treścią 'Spotkajmy się jutro'"
   "Pokaż szczegóły emaila ID 1"

2. Ćwiczenie 1 - Mark as read:
   "Oznacz email ID 1 jako przeczytany"
   "Przeczytałem email ID 2"

3. Ćwiczenie 2 - Search by sender:
   "Znajdź wszystkie emaile od boss@company.com"
   "Pokaż emaile od klienta"
   "Szukaj emaili od @tech.com"

4. Ćwiczenie 3 - Unread count:
   "Ile mam nieprzeczytanych emaili?"
   "Pokaż nieprzeczytane"
   "Czy mam nowe wiadomości?"

5. Bonusowe:
   "Zarchiwizuj email ID 2"
   "Znajdź emaile o temacie 'Report'"

6. Złożone scenariusze:
   "Pokaż nieprzeczytane emaile, oznacz je jako przeczytane i zarchiwizuj"
   "Znajdź emaile od szefa i pokaż szczegóły pierwszego"

UWAGA:
To jest MOCK implementation dla celów demonstracyjnych.
W prawdziwej implementacji użyj:
  from google.adk.tools.google_api_tool import GmailToolset
  gmail_toolset = GmailToolset(client_id, client_secret)

URUCHOMIENIE:
adk web
"""

# =============================================================================
# PRAWDZIWA IMPLEMENTACJA (odkomentuj gdy masz credentials)
# =============================================================================
"""
# Wymaga Google Cloud OAuth credentials

from google.adk.tools.google_api_tool import GmailToolset

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

gmail_toolset = GmailToolset(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)

real_gmail_agent = LlmAgent(
    name="gmail_agent_real",
    model=MODEL,
    instruction="Zarządzaj Gmail...",
    tools=[gmail_toolset]  # Prawdziwe narzędzia Gmail
)

# root_agent = real_gmail_agent
"""
# =============================================================================
# ĆWICZENIE 3: GET_UNREAD_COUNT
# =============================================================================

def get_unread_count() -> str:
    """
    Zwraca liczbę nieprzeczytanych emaili.
    """
    unread_emails = [e for e in MOCK_EMAILS if not e["read"]]
    count = len(unread_emails)
    
    if count == 0:
        return "✅ Brak nieprzeczytanych emaili! Inbox zero 🎉"
    
    result = f"📬 Masz {count} nieprzeczytanych emaili:\n\n"
    for email in unread_emails:
        result += f"✉️ {email['subject']} (od: {email['from']})\n"
    
    return result

# =============================================================================
# DODATKOWE FUNKCJE BONUSOWE
# =============================================================================

def archive_email(email_id: str) -> str:
    """Archiwizuje email (usuwa z INBOX)."""
    email = next((e for e in MOCK_EMAILS if e["id"] == email_id), None)
    
    if not email:
        return f"❌ Nie znaleziono emaila o ID: {email_id}"
    
    if "INBOX" in email["labels"]:
        email["labels"].remove("INBOX")
        return f"✅ Zarchiwizowano email: {email['subject']}"
    else:
        return f"ℹ️ Email {email_id} nie jest w INBOX"

def search_emails_by_subject(keyword: str) -> str:
    """Wyszukuje emaile po słowie kluczowym w temacie."""
    matching = [
        e for e in MOCK_EMAILS 
        if keyword.lower() in e["subject"].lower()
    ]
    
    if not matching:
        return f"📭 Nie znaleziono emaili z '{keyword}' w temacie"
    
    result = f"🔍 Znaleziono {len(matching)} emaili z '{keyword}':\n\n"
    for email in matching:
        result += f"📧 {email['subject']} (od: {email['from']})\n"
    
    return result



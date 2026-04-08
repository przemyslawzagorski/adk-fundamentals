# Module 15: Gmail Integration - Teoria

## 🎯 Kluczowe Koncepcje

### GmailToolset - Integracja z Gmail

**GmailToolset** zapewnia narzędzia do operacji na Gmail przez Google API.

```python
from google.adk.tools.google_api_tool import GmailToolset

gmail = GmailToolset(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET"
)

agent = LlmAgent(
    tools=[gmail]  # Agent może czytać/wysyłać emaile!
)
```

### Wymagania

1. **Google Cloud Project** z włączonym Gmail API
2. **OAuth 2.0 Credentials** (Client ID + Secret)
3. **Scopes** (uprawnienia): `gmail.readonly`, `gmail.send`, etc.

### Dostępne Operacje

| Operacja | Opis | Przykład |
|----------|------|----------|
| **List** | Wyświetl emaile | `list_emails(max_results=10)` |
| **Read** | Czytaj email | `get_email(email_id)` |
| **Send** | Wyślij email | `send_email(to, subject, body)` |
| **Search** | Szukaj emaili | `search_emails(query="from:boss")` |
| **Mark** | Oznacz jako przeczytany | `mark_as_read(email_id)` |

---

## 💼 Przypadki Użycia Biznesowego

### 1. Email Assistant - Automatyzacja Skrzynki

```python
email_assistant = LlmAgent(
    instruction="""Zarządzaj skrzynką pocztową:
    
    - Podsumowuj nieprzeczytane emaile
    - Priorytetyzuj ważne wiadomości
    - Sugeruj odpowiedzi
    - Archiwizuj newslettery
    """,
    tools=[gmail_toolset]
)
```

**Korzyści:** Oszczędność czasu, inbox zero, mniej przegapionych emaili.

### 2. Customer Support - Auto-Odpowiedzi

```python
support_agent = LlmAgent(
    instruction="""Odpowiadaj na emaile klientów:
    
    - FAQ → automatyczna odpowiedź
    - Skomplikowane → eskaluj do człowieka
    - Zawsze profesjonalny ton
    """,
    tools=[gmail_toolset]
)
```

### 3. Sales - Follow-up Automation

```python
sales_agent = LlmAgent(
    instruction="""Zarządzaj follow-upami:
    
    - Znajdź emaile bez odpowiedzi >3 dni
    - Wyślij gentle reminder
    - Śledź status leadów
    """,
    tools=[gmail_toolset]
)
```

---

## ✅ Najlepsze Praktyki

### 1. OAuth Setup

**Krok 1: Google Cloud Console**
```
1. Utwórz projekt w GCP
2. Włącz Gmail API
3. Utwórz OAuth 2.0 Credentials
4. Dodaj redirect URI: http://localhost:8080
5. Pobierz Client ID i Secret
```

**Krok 2: .env**
```bash
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_secret
```

### 2. Scopes (Uprawnienia)

```python
# Minimalne uprawnienia (principle of least privilege)
scopes = [
    "https://www.googleapis.com/auth/gmail.readonly",  # Tylko czytanie
    "https://www.googleapis.com/auth/gmail.send"       # Tylko wysyłanie
]

# Pełne uprawnienia (jeśli potrzebne)
scopes = ["https://mail.google.com/"]  # Wszystko
```

### 3. Walidacja Przed Wysłaniem

```python
def send_email_safe(to: str, subject: str, body: str) -> str:
    # Walidacja
    if "@" not in to:
        return "❌ Niepoprawny adres email"
    
    if len(subject) < 3:
        return "❌ Temat zbyt krótki"
    
    if len(body) < 10:
        return "❌ Treść zbyt krótka"
    
    # Wyślij
    return gmail.send_email(to, subject, body)
```

### 4. Rate Limiting

```python
# Gmail API ma limity (np. 250 emaili/dzień dla darmowych kont)

import time

def send_bulk_emails(recipients: list):
    for recipient in recipients:
        send_email(recipient, ...)
        time.sleep(1)  # Pauza między emailami
```

---

## ⚠️ Typowe Pułapki

### 1. Brak Obsługi Błędów OAuth

**Problem:** Token wygasł → crash.

**Rozwiązanie:**
```python
try:
    emails = gmail.list_emails()
except AuthenticationError:
    return "❌ Wymagane ponowne logowanie. Uruchom: adk auth"
```

### 2. Spam Filters

**Problem:** Automatyczne emaile trafiają do spamu.

**Rozwiązanie:**
- Używaj profesjonalnego tonu
- Dodaj personalizację
- Unikaj spam keywords ("FREE", "URGENT", "CLICK HERE")
- Ustaw SPF/DKIM dla domeny

### 3. Przekroczenie Limitów

**Problem:** 250 emaili/dzień → blokada.

**Rozwiązanie:**
- Monitoruj użycie
- Użyj Google Workspace (wyższe limity)
- Batch operations zamiast pojedynczych

### 4. Brak Potwierdzenia Przed Wysłaniem

**Problem:** Agent wysyła email bez pytania użytkownika.

**Rozwiązanie:**
```python
instruction="""
WAŻNE: Przed wysłaniem emaila ZAWSZE:
1. Pokaż użytkownikowi draft
2. Poproś o potwierdzenie
3. Dopiero po "tak" wyślij
"""
```

---

## 🔗 Odniesienia

### Google APIs
- [Gmail API Docs](https://developers.google.com/gmail/api)
- [OAuth 2.0 Setup](https://developers.google.com/identity/protocols/oauth2)

### ADK
- [GmailToolset Docs](https://google.github.io/adk-docs/tools/gmail/)

---

## 📝 Podsumowanie

| Koncepcja | Kluczowy Punkt |
|-----------|----------------|
| **GmailToolset** | Integracja z Gmail przez OAuth |
| **OAuth** | Wymaga Client ID + Secret z GCP |
| **Scopes** | Minimalne uprawnienia (least privilege) |
| **Walidacja** | Sprawdzaj dane przed wysłaniem |
| **Rate Limits** | 250 emaili/dzień (darmowe konto) |
| **Potwierdzenie** | Pytaj przed wysłaniem emaila |

---

## 🎓 Gratulacje!

Ukończyłeś wszystkie moduły szkoleniowe ADK! 🎉

**Nauczyłeś się:**
- Module 01: Podstawy LlmAgent
- Module 02: Custom Tools
- Module 03: RAG (Retrieval-Augmented Generation)
- Module 04: Sequential Agent (pipeline)
- Module 05: Human-in-the-Loop
- Module 07: Parallel Agent
- Module 08: Loop Critique (iteracyjne doskonalenie)
- Module 09: Database Integration
- Module 11: Memory Bank (pamięć długoterminowa)
- Module 12: Router Agent (routing do ekspertów)
- Module 15: Gmail Integration

**Następne kroki:**
- Zbuduj własnego agenta łączącego te wzorce
- Wdróż na produkcję (Cloud Run, Vertex AI)
- Eksperymentuj z zaawansowanymi scenariuszami

*Powodzenia w budowaniu agentów AI!* 🚀


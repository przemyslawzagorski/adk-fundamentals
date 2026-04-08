"""
Module 15: Gmail Integration
=============================
Asystent Gmail — odczytuje, wysyła i przeszukuje emaile.

Demonstracja:
- GmailToolset z ograniczonym tool_filter (mniej narzędzi = mniej promptów OAuth)
- OAuth 2.0 z Google APIs
- Odczyt, wysyłanie i wyszukiwanie wiadomości
"""

import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.genai import types
from google.adk.tools.google_api_tool import GmailToolset

load_dotenv()

# =============================================================================
# Configuration
# =============================================================================

MODEL = "gemini-2.5-flash"
AGENT_APP_NAME = "gmail_assistant"

# OAuth Credentials (from Google Cloud Console)
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

# =============================================================================
# Gmail Toolset — ograniczony zestaw narzędzi
# =============================================================================
# Bez tool_filter GmailToolset eksponuje ~80 endpointów Gmail API.
# Każdy endpoint wymaga osobnej autoryzacji OAuth w sesji → agent zbyt często
# pyta o token. Ograniczamy do niezbędnych operacji.

GMAIL_TOOLS = [
    "gmail_users_messages_list",
    "gmail_users_messages_get",
    "gmail_users_messages_send",
    "gmail_users_labels_list",
]

gmail_toolset = GmailToolset(
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    tool_filter=GMAIL_TOOLS,
)

# =============================================================================
# Agent — Asystent Gmail
# =============================================================================

INSTRUCTION = """Jesteś asystentem Gmail. Pomagasz użytkownikowi zarządzać skrzynką pocztową.

DOSTĘPNE OPERACJE:
1. Wyświetl ostatnie emaile (gmail_users_messages_list)
2. Przeczytaj konkretnego emaila (gmail_users_messages_get)
3. Wyślij email (gmail_users_messages_send)
4. Wyświetl etykiety/foldery (gmail_users_labels_list)

ZASADY:
- Przed wysłaniem emaila ZAWSZE pokaż szkic i poproś o potwierdzenie
- Podsumowuj wyniki zwięźle — podawaj nadawcę, temat i datę
- Jeśli użytkownik nie podał szczegółów, zapytaj o brakujące informacje
- W parametrze userId zawsze podawaj "me"
- Odpowiadaj po polsku
"""

root_agent = LlmAgent(
    name=AGENT_APP_NAME,
    model=MODEL,
    instruction=INSTRUCTION,
    description="Asystent Gmail — odczyt, wysyłanie i wyszukiwanie emaili",
    tools=[gmail_toolset],
    generate_content_config=types.GenerateContentConfig(temperature=0.3),
)

# =============================================================================
# For testing
# =============================================================================

if __name__ == "__main__":
    print("📧 Asystent Gmail — Module 15")
    print("=" * 50)
    print(f"Client ID configured: {'Yes' if GOOGLE_CLIENT_ID else 'No'}")
    print(f"Client Secret configured: {'Yes' if GOOGLE_CLIENT_SECRET else 'No'}")
    print(f"Tool filter: {GMAIL_TOOLS}")
    print()
    print("To run with ADK Dev UI:")
    print("  adk web")
    print()
    print("Note: OAuth consent screen must be configured in GCP Console")
    print("and you'll be prompted to authenticate on first use.")


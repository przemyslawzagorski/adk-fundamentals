"""
Moduł 3: Agent RAG - Wyszukiwanie Wspomagane Generowaniem
==========================================================
LlmAgent z Vertex AI Search dla Retrieval-Augmented Generation.

Ten agent może przeszukiwać dokumentację i bazy wiedzy przechowywane
w Vertex AI Search, łącząc moc LLM z dokładnością wyszukiwania.

Cele edukacyjne:
- Zrozumienie wzorca RAG (Retrieval-Augmented Generation)
- Konfiguracja Vertex AI Search Tool z data_store_id LUB search_engine_id
- Integracja korporacyjnych baz wiedzy z agentami ADK
- Obserwacja jak LLM używa pobranego kontekstu do odpowiedzi
"""

import logging
import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools import VertexAiSearchTool

# .env z TEGO katalogu, z override=True – d1_04 używa tych samych nazw zmiennych.
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"), override=True)

logger = logging.getLogger(__name__)

# =============================================================================
# KONFIGURACJA VERTEX AI SEARCH
# =============================================================================
# Możesz użyć ALBO data_store_id ALBO search_engine_id (nie obu!)
#
# Opcja 1: Data Store ID (bezpośredni dostęp do magazynu danych)
#   Format: "projects/{project}/locations/{location}/collections/{collection}/dataStores/{dataStore}"
#
# Opcja 2: Search Engine ID (aplikacja wyszukiwania z potencjalnie wieloma magazynami danych)
#   Format: "projects/{project}/locations/{location}/collections/{collection}/engines/{engine}"
# =============================================================================

# Odczytaj konfigurację ze środowiska
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")
SEARCH_DATASTORE_ID = os.getenv("SEARCH_DATASTORE_ID")

# Określ które ID użyć (preferuj search_engine_id jeśli oba są ustawione)
if SEARCH_ENGINE_ID:
    # Używanie Search Engine ID
    narzedzie_wyszukiwania = VertexAiSearchTool(
        search_engine_id=SEARCH_ENGINE_ID,
        max_results=10  # Maksymalna liczba dokumentów do pobrania na zapytanie
    )
    logger.info("Vertex AI Search engine: %s", SEARCH_ENGINE_ID)
elif SEARCH_DATASTORE_ID:
    # Używanie Data Store ID bezpośrednio
    narzedzie_wyszukiwania = VertexAiSearchTool(
        data_store_id=SEARCH_DATASTORE_ID,
        max_results=10
    )
    logger.info("Vertex AI Search data store: %s", SEARCH_DATASTORE_ID)
else:
    # Fallback dla demo/testów - zawiedzie w runtime jeśli faktycznie wywołane
    # W rzeczywistym użyciu MUSISZ skonfigurować jedno z ID
    raise ValueError(
        "SEARCH_ENGINE_ID lub SEARCH_DATASTORE_ID musi być ustawione w pliku .env!\n"
        "Zobacz README.md dla instrukcji konfiguracji Vertex AI Search."
    )

# =============================================================================
# PROMPT INSTRUKCJI
# =============================================================================
instruction_prompt = """Jesteś asystentem AI z dostępem do bazy wiedzy organizacji.

Twoje zadania:
1. Odpowiadanie na pytania używając dostępnej dokumentacji
2. Przeszukiwanie bazy wiedzy, procedur i dokumentacji technicznej
3. Dostarczanie dokładnych, dobrze udokumentowanych informacji

WAŻNE WYTYCZNE:
- Gdy użytkownik zadaje pytanie, UŻYJ narzędzia wyszukiwania aby znaleźć odpowiednie informacje
- Jeśli to tylko swobodna rozmowa, nie musisz wyszukiwać
- Zawsze cytuj źródła gdy podajesz informacje z bazy wiedzy
- Jeśli informacji nie ma w bazie, jasno to komunikuj
- Zadawaj pytania wyjaśniające jeśli zapytanie jest niejasne

Odpowiadaj profesjonalnie i precyzyjnie, wykorzystując dostępną wiedzę organizacji.
"""

# =============================================================================
# AGENT RAG
# =============================================================================
root_agent = LlmAgent(
    name="asystent_rag",
    model=os.getenv("ADK_MODEL", "gemini-3.5-flash-lite"),
    instruction=instruction_prompt,
    description="Asystent AI z dostępem do bazy wiedzy organizacji przez RAG.",
    tools=[narzedzie_wyszukiwania]
)


# =============================================================================
# NOTATKI TESTOWE
# =============================================================================
"""
Aby przetestować tego agenta:

1. Skonfiguruj Vertex AI Search w swoim projekcie GCP
2. Stwórz Data Store i wgraj dokumenty (PDFy, HTML, itp.)
3. Skonfiguruj plik .env z odpowiednim ID
4. Uruchom: adk web

Przykładowe pytania do wypróbowania:
- "Jakie są procedury wdrożeniowe opisane w dokumentacji?"
- "Wyszukaj informacje o konfiguracji systemu"
- "Jakie są wymagania bezpieczeństwa dla tego produktu?"
- "Znajdź dokumentację API dla modułu X"

Pamiętaj: Jakość odpowiedzi zależy od dokumentów w Twoim magazynie danych!
"""


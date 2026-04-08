"""
Moduł 10: Local RAG - Wyszukiwanie w plikach firmowych
=======================================================
LlmAgent z FilesRetrieval do przeszukiwania lokalnych dokumentów firmy.

FilesRetrieval używa LlamaIndex do:
1. Wczytania dokumentów z katalogu (SimpleDirectoryReader)
2. Wygenerowania embeddingów (gemini-embedding-2-preview)
3. Zbudowania indeksu wektorowego w pamięci (VectorStoreIndex)
4. Wyszukiwania semantycznego przy zapytaniach agenta

Cele edukacyjne:
- Zrozumienie RAG opartego na plikach lokalnych (bez chmury)
- Porównanie z podejściem Vertex AI Search (moduł 03)
- Konfiguracja FilesRetrieval z ADK
- Obserwacja procesu indeksowania i wyszukiwania
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.retrieval.files_retrieval import FilesRetrieval

# Załaduj zmienne środowiskowe z pliku .env (z katalogu modułu)
_module_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_module_dir, ".env"))

# =============================================================================
# KONFIGURACJA FILESRETRIEVAL
# =============================================================================
# Katalog z dokumentami firmowymi do zaindeksowania
# Obsługiwane formaty: .txt, .md, .pdf, .docx, .csv, .json, .html
DOCS_DIR = os.path.join(os.path.dirname(__file__), "docs")

# Upewnij się, że katalog z dokumentami istnieje
if not os.path.isdir(DOCS_DIR):
    raise FileNotFoundError(
        f"Katalog z dokumentami nie istnieje: {DOCS_DIR}\n"
        "Utwórz katalog 'docs/' i dodaj pliki do zaindeksowania."
    )

# Tworzenie narzędzia FilesRetrieval
# Indeksowanie następuje TUTAJ - przy ładowaniu modułu
narzedzie_rag = FilesRetrieval(
    name="baza_wiedzy_firmowej",
    description=(
        "Przeszukuje lokalną bazę wiedzy firmy: dokumentacje techniczne, "
        "procedury, polityki bezpieczeństwa, instrukcje onboardingu. "
        "Użyj tego narzędzia gdy pytanie dotyczy wewnętrznych informacji firmy."
    ),
    input_dir=DOCS_DIR,
)

# =============================================================================
# PROMPT INSTRUKCJI
# =============================================================================
instruction_prompt = """Jesteś asystentem wiedzy firmowej TechCorp.

Twoje zadania:
1. Odpowiadanie na pytania o procedury, polityki i architekturę firmy
2. Wyszukiwanie informacji w dokumentacji wewnętrznej
3. Pomaganie nowym pracownikom w onboardingu

WYTYCZNE:
- Gdy pytanie dotyczy firmy, UŻYJ narzędzia baza_wiedzy_firmowej
- Cytuj źródła (nazwa dokumentu) gdy podajesz informacje
- Jeśli informacji nie ma w bazie, powiedz o tym wprost
- Odpowiadaj po polsku, profesjonalnie i precyzyjnie
- Przy pytaniach ogólnych (nie o firmę) odpowiadaj na podstawie własnej wiedzy
"""

# =============================================================================
# DEFINICJA AGENTA
# =============================================================================
AGENT_APP_NAME = "local_rag_agent"

root_agent = LlmAgent(
    name=AGENT_APP_NAME,
    model="gemini-2.0-flash",
    instruction=instruction_prompt,
    tools=[narzedzie_rag],
)

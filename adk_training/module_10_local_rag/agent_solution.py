"""
Moduł 10 - Ćwiczenia: Porównanie RAG lokalnego z chmurowym
============================================================
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.retrieval.files_retrieval import FilesRetrieval

load_dotenv()

DOCS_DIR = os.path.join(os.path.dirname(__file__), "docs")

# =============================================================================
# Ćwiczenie 1: Podstawowy agent RAG z plikami lokalnymi
# =============================================================================

narzedzie_rag_basic = FilesRetrieval(
    name="baza_wiedzy",
    description="Przeszukuje dokumenty firmowe - procedury, architekturę, polityki.",
    input_dir=DOCS_DIR,
)

agent_rag_basic = LlmAgent(
    name="basic_file_rag",
    model="gemini-2.0-flash",
    instruction="""Jesteś asystentem wiedzy firmowej.
Odpowiadaj na pytania korzystając z narzędzia baza_wiedzy.
Zawsze podawaj źródło informacji.""",
    tools=[narzedzie_rag_basic],
)

# =============================================================================
# Ćwiczenie 2: Agent BEZ RAG (porównanie jakości odpowiedzi)
# =============================================================================

agent_bez_rag = LlmAgent(
    name="bez_rag",
    model="gemini-2.0-flash",
    instruction="""Jesteś asystentem wiedzy firmowej TechCorp.
Odpowiadaj na pytania na podstawie własnej wiedzy o firmie.
Nie masz dostępu do dokumentacji firmowej.""",
)

# =============================================================================
# Ćwiczenie 3: Agent z własnym katalogiem dokumentów
# =============================================================================
# ZADANIE: Utwórz katalog 'docs_custom/' z własnymi dokumentami
# i skonfiguruj agenta poniżej.
#
# CUSTOM_DOCS_DIR = os.path.join(os.path.dirname(__file__), "docs_custom")
#
# narzedzie_custom = FilesRetrieval(
#     name="moja_baza",
#     description="Twoja własna baza wiedzy",
#     input_dir=CUSTOM_DOCS_DIR,
# )
#
# agent_custom = LlmAgent(
#     name="custom_rag",
#     model="gemini-2.0-flash",
#     instruction="...",
#     tools=[narzedzie_custom],
# )

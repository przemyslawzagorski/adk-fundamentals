"""
Moduł 13: Code Analyst Agent z MCP (Jira + GitLab)
===================================================
Zaawansowany system agentowy łączący:
- Persistent Code RAG (LlamaIndex + SimpleVectorStore) do przeszukiwania kodu
- MCP Atlassian (Jira) do odczytu/tworzenia ticketów
- MCP Git (lokalne operacje) do analizy repozytorium

Przepływ:
1. Użytkownik podaje ticket Jira lub pytanie o kod
2. Agent przeszukuje zaindeksowany kod (RAG)
3. Agent proponuje rozwiązanie z diagramem
4. Opcjonalnie: tworzy stories w Jira

Cele edukacyjne:
- Persistent RAG z LlamaIndex (vs in-memory FilesRetrieval z modulu 10)
- Integracja MCP w ADK (Jira, Git)
- Multi-agent orchestration (Sequential/Router)
- Code-aware chunking i incremental indexing
"""

import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from code_retrieval_tool import search_code, index_project, get_index_stats

# Załaduj zmienne środowiskowe
_module_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_module_dir, ".env"))

# =============================================================================
# NARZĘDZIA ADK
# =============================================================================

tool_search_code = FunctionTool(func=search_code)
tool_index_project = FunctionTool(func=index_project)
tool_get_stats = FunctionTool(func=get_index_stats)

# =============================================================================
# INSTRUKCJA AGENTA
# =============================================================================

INSTRUCTION = """Jesteś zaawansowanym analitykiem kodu. Pomagasz zespołowi developerów
zrozumieć i modyfikować bazę kodu na podstawie ticketów Jira.

## Twoje narzędzia

### Kod
- **search_code(query, top_k)** - Semantyczne przeszukiwanie zaindeksowanego kodu.
  Opisz funkcjonalność po polsku lub angielsku, np. "obsługa autoryzacji JWT"
- **index_project(extensions, incremental)** - Zaindeksuj/odśwież kod w indeksie
- **get_index_stats()** - Sprawdź statystyki indeksu

## Przepływ pracy

### Gdy użytkownik podaje ticket/opis problemu:
1. Przeszukaj kod narzędziem `search_code` - użyj kluczowych terminów z opisu
2. Jeśli wyniki niewystarczające - przeformułuj zapytanie i szukaj ponownie
3. Na podstawie znalezionych fragmentów przygotuj analizę

### Gdy użytkownik prosi o propozycję rozwiązania:
1. Przeszukaj relevantne fragmenty kodu
2. Przygotuj:
   a. Streszczenie wymagań
   b. Lista powiązanych plików z kodu (ze ścieżkami!)
   c. Proponowane rozwiązanie techniczne
   d. Diagram Mermaid (sequence/class/flowchart)
   e. Proponowane stories z acceptance criteria
   f. Estymacja złożoności i ryzyka

### Gdy użytkownik prosi o zaindeksowanie:
1. Uruchom `index_project()` z odpowiednimi parametrami
2. Pokaż statystyki po zakończeniu

## Zasady
- ZAWSZE cytuj ścieżki plików z wyników RAG
- Odpowiadaj po polsku
- Diagramy twórz w formacie Mermaid
- Stories muszą mieć: tytuł, opis, acceptance criteria, definition of done
- Jeśli indeks jest pusty - zaproponuj najpierw zaindeksowanie
- Bądź precyzyjny w estymacjach - podaj konkretne pliki do modyfikacji
"""

# =============================================================================
# AGENT
# =============================================================================

AGENT_APP_NAME = "code_analyst_agent"

root_agent = LlmAgent(
    name=AGENT_APP_NAME,
    model="gemini-2.0-flash",
    instruction=INSTRUCTION,
    tools=[tool_search_code, tool_index_project, tool_get_stats],
    description="Analizuje kod źródłowy przez RAG, proponuje rozwiązania z diagramami",
)

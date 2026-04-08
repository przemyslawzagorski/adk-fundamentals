"""
Moduł 3: Agent RAG - ROZWIĄZANIA ĆWICZEŃ
=========================================
Ten plik zawiera rozwiązania wszystkich ćwiczeń z README.md dla Module 03.

Ćwiczenia:
1. Podstawowy RAG - wgranie dokumentów i testowanie
2. Porównanie z i bez RAG
3. Testowanie limitów pobierania (max_results)
"""

import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools import VertexAiSearchTool

load_dotenv()

# =============================================================================
# KONFIGURACJA VERTEX AI SEARCH
# =============================================================================

SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")
SEARCH_DATASTORE_ID = os.getenv("SEARCH_DATASTORE_ID")

# =============================================================================
# ĆWICZENIE 3.1: PODSTAWOWY RAG
# =============================================================================
# Zadanie: Wgraj 2-3 dokumenty i testuj przeszukiwanie

# Rozwiązanie: Agent z podstawową konfiguracją RAG
if SEARCH_ENGINE_ID:
    rag_tool_basic = VertexAiSearchTool(
        search_engine_id=SEARCH_ENGINE_ID,
        max_results=5  # Umiarkowana liczba wyników
    )
elif SEARCH_DATASTORE_ID:
    rag_tool_basic = VertexAiSearchTool(
        data_store_id=SEARCH_DATASTORE_ID,
        max_results=5
    )
else:
    raise ValueError("Musisz skonfigurować SEARCH_ENGINE_ID lub SEARCH_DATASTORE_ID w .env")

agent_rag_basic = LlmAgent(
    name="asystent_rag_podstawowy",
    model="gemini-2.5-flash",
    instruction="""Jesteś asystentem AI z dostępem do bazy wiedzy organizacji.

TWOJE ZADANIA:
1. Odpowiadaj na pytania używając dokumentacji z bazy wiedzy
2. Zawsze cytuj źródła swoich informacji
3. Jeśli informacji nie ma w bazie, jasno to komunikuj
4. Bądź precyzyjny i konkretny

PROCES ODPOWIADANIA:
1. Gdy użytkownik zadaje pytanie merytoryczne, UŻYJ narzędzia wyszukiwania
2. Przeanalizuj znalezione dokumenty
3. Sformułuj odpowiedź na podstawie dokumentów
4. Podaj źródła (tytuły dokumentów, sekcje)

PRZYKŁAD DOBREJ ODPOWIEDZI:
"Według dokumentacji 'Procedury Wdrożeniowe' (sekcja 3.2), proces wdrożenia
składa się z 5 kroków: 1) Analiza wymagań, 2) Projektowanie..."

Odpowiadaj profesjonalnie i precyzyjnie!
""",
    description="Asystent RAG z podstawową konfiguracją",
    tools=[rag_tool_basic]
)

# =============================================================================
# ĆWICZENIE 3.2: PORÓWNANIE Z I BEZ RAG
# =============================================================================
# Zadanie: Porównaj jakość odpowiedzi z RAG vs bez RAG

# Agent BEZ RAG (dla porównania)
agent_bez_rag = LlmAgent(
    name="asystent_bez_rag",
    model="gemini-2.5-flash",
    instruction="""Jesteś asystentem AI odpowiadającym na pytania.

WAŻNE: NIE MASZ dostępu do bazy wiedzy organizacji!
Odpowiadaj na podstawie swojej ogólnej wiedzy.

Jeśli pytanie dotyczy specyficznych dokumentów lub procedur organizacji,
przyznaj że nie masz dostępu do tych informacji i zasugeruj kontakt
z odpowiednim działem.

Bądź uczciwy co do swoich ograniczeń!
""",
    description="Asystent bez dostępu do RAG (dla porównania)",
    tools=[]  # Brak narzędzi RAG
)

# Agent Z RAG (dla porównania)
agent_z_rag = LlmAgent(
    name="asystent_z_rag",
    model="gemini-2.5-flash",
    instruction="""Jesteś asystentem AI z dostępem do bazy wiedzy organizacji.

MASZ dostęp do narzędzia wyszukiwania w dokumentacji!

Gdy użytkownik zadaje pytanie:
1. UŻYJ narzędzia wyszukiwania aby znaleźć odpowiednie dokumenty
2. Przeanalizuj znalezione informacje
3. Sformułuj odpowiedź cytując źródła

Zawsze podkreślaj że Twoja odpowiedź jest oparta na dokumentacji organizacji.
""",
    description="Asystent z dostępem do RAG (dla porównania)",
    tools=[rag_tool_basic]
)

# =============================================================================
# ĆWICZENIE 3.3: TESTOWANIE LIMITÓW POBIERANIA
# =============================================================================
# Zadanie: Wypróbuj różne wartości max_results (1, 5, 10, 20)

# Konfiguracja z różnymi limitami
if SEARCH_ENGINE_ID:
    rag_tool_min = VertexAiSearchTool(search_engine_id=SEARCH_ENGINE_ID, max_results=1)
    rag_tool_small = VertexAiSearchTool(search_engine_id=SEARCH_ENGINE_ID, max_results=5)
    rag_tool_medium = VertexAiSearchTool(search_engine_id=SEARCH_ENGINE_ID, max_results=10)
    rag_tool_large = VertexAiSearchTool(search_engine_id=SEARCH_ENGINE_ID, max_results=20)
elif SEARCH_DATASTORE_ID:
    rag_tool_min = VertexAiSearchTool(data_store_id=SEARCH_DATASTORE_ID, max_results=1)
    rag_tool_small = VertexAiSearchTool(data_store_id=SEARCH_DATASTORE_ID, max_results=5)
    rag_tool_medium = VertexAiSearchTool(data_store_id=SEARCH_DATASTORE_ID, max_results=10)
    rag_tool_large = VertexAiSearchTool(data_store_id=SEARCH_DATASTORE_ID, max_results=20)

# Agent z minimalnym pobieraniem (1 dokument)
agent_rag_min = LlmAgent(
    name="asystent_rag_min",
    model="gemini-2.5-flash",
    instruction="""Asystent RAG z MINIMALNYM pobieraniem (max 1 dokument).
    
Używaj tego gdy:
- Pytanie jest bardzo konkretne
- Potrzebujesz szybkiej odpowiedzi
- Wiesz że odpowiedź jest w jednym dokumencie
""",
    tools=[rag_tool_min]
)

# Agent z małym pobieraniem (5 dokumentów)
agent_rag_small = LlmAgent(
    name="asystent_rag_small",
    model="gemini-2.5-flash",
    instruction="""Asystent RAG z MAŁYM pobieraniem (max 5 dokumentów).

Używaj tego gdy:
- Pytanie wymaga sprawdzenia kilku źródeł
- Balans między szybkością a dokładnością
- Standardowe zapytania
""",
    tools=[rag_tool_small]
)

# Agent ze średnim pobieraniem (10 dokumentów)
agent_rag_medium = LlmAgent(
    name="asystent_rag_medium",
    model="gemini-2.5-flash",
    instruction="""Asystent RAG ze ŚREDNIM pobieraniem (max 10 dokumentów).

Używaj tego gdy:
- Pytanie jest złożone i wymaga wielu źródeł
- Potrzebujesz kompleksowej odpowiedzi
- Temat może być rozproszony w dokumentacji
""",
    tools=[rag_tool_medium]
)

# Agent z dużym pobieraniem (20 dokumentów)
agent_rag_large = LlmAgent(
    name="asystent_rag_large",
    model="gemini-2.5-flash",
    instruction="""Asystent RAG z DUŻYM pobieraniem (max 20 dokumentów).

Używaj tego gdy:
- Pytanie wymaga bardzo szerokiego kontekstu
- Potrzebujesz przeszukać całą bazę wiedzy
- Jakość > szybkość

UWAGA: Wolniejsze odpowiedzi, wyższe koszty!
""",
    tools=[rag_tool_large]
)

# =============================================================================
# AGENT GŁÓWNY - Wybierz który chcesz użyć
# =============================================================================
# Odkomentuj jedną z poniższych linii:

# root_agent = agent_rag_basic      # Ćwiczenie 3.1 - Podstawowy RAG
# root_agent = agent_bez_rag        # Ćwiczenie 3.2 - BEZ RAG (porównanie)
# root_agent = agent_z_rag          # Ćwiczenie 3.2 - Z RAG (porównanie)
# root_agent = agent_rag_min        # Ćwiczenie 3.3 - max_results=1
# root_agent = agent_rag_small      # Ćwiczenie 3.3 - max_results=5
# root_agent = agent_rag_medium     # Ćwiczenie 3.3 - max_results=10
root_agent = agent_rag_large      # Ćwiczenie 3.3 - max_results=20 (domyślny)

# =============================================================================
# PRZYKŁADY TESTOWANIA
# =============================================================================
"""
TESTOWANIE ĆWICZENIA 3.1 (Podstawowy RAG):
------------------------------------------
1. Wgraj 2-3 dokumenty do Vertex AI Search Data Store:
   - Dokument 1: "Procedury Wdrożeniowe.pdf"
   - Dokument 2: "Polityka Bezpieczeństwa.pdf"
   - Dokument 3: "FAQ Produktu.pdf"

2. Poczekaj na zakończenie indeksowania (10-30 minut)

3. Testuj zapytania:
   - "Jakie są etapy procesu wdrożenia?"
   - "Jakie są wymagania bezpieczeństwa?"
   - "Jak skonfigurować produkt?"

4. Obserwuj:
   - Czy agent cytuje źródła?
   - Czy odpowiedzi są dokładne?
   - Czy agent używa narzędzia wyszukiwania?

TESTOWANIE ĆWICZENIA 3.2 (Porównanie):
---------------------------------------
1. Zadaj to samo pytanie obu agentom:
   Pytanie: "Jakie są procedury wdrożeniowe w naszej firmie?"

2. Porównaj odpowiedzi:

   Agent BEZ RAG:
   - Odpowie ogólnie lub powie że nie ma dostępu
   - Brak konkretów specyficznych dla firmy
   - Może wymyślić informacje (hallucination)

   Agent Z RAG:
   - Znajdzie dokument "Procedury Wdrożeniowe"
   - Poda konkretne kroki z dokumentacji
   - Zacytuje źródło

3. Wnioski:
   - RAG eliminuje hallucinations
   - RAG daje konkretne, zweryfikowane informacje
   - RAG cytuje źródła (weryfikowalność)

TESTOWANIE ĆWICZENIA 3.3 (Limity pobierania):
----------------------------------------------
1. Zadaj złożone pytanie wymagające wielu źródeł:
   "Jakie są wszystkie procedury bezpieczeństwa i wdrożeniowe?"

2. Testuj z różnymi limitami:

   max_results=1:
   - Najszybsza odpowiedź
   - Może pominąć ważne informacje
   - Dobre dla prostych pytań

   max_results=5:
   - Dobry balans
   - Wystarczające dla większości pytań
   - Zalecane dla produkcji

   max_results=10:
   - Bardziej kompleksowe odpowiedzi
   - Wolniejsze
   - Dobre dla złożonych pytań

   max_results=20:
   - Najbardziej kompleksowe
   - Najwolniejsze
   - Najdroższe (więcej tokenów)
   - Użyj tylko gdy naprawdę potrzebne

3. Metryki do obserwacji:
   - Czas odpowiedzi (sekundy)
   - Jakość odpowiedzi (kompletność)
   - Koszt (tokeny użyte)
   - Relevantność wyników

URUCHOMIENIE:
-------------
1. Skonfiguruj Vertex AI Search (zobacz README.md)
2. Wgraj dokumenty do Data Store
3. Skopiuj ID do .env
4. Wybierz agenta (odkomentuj linię root_agent)
5. Uruchom: adk web
6. Testuj!

WSKAZÓWKI:
----------
- Zacznij od małych limitów (max_results=5)
- Zwiększaj tylko gdy potrzebne
- Monitoruj koszty w GCP Console
- Testuj różne typy pytań (proste vs złożone)
"""

# =============================================================================
# DODATKOWE ROZWIĄZANIE: Agent Adaptacyjny
# =============================================================================
# Bonus: Agent który sam dostosowuje strategię wyszukiwania

agent_rag_adaptacyjny = LlmAgent(
    name="asystent_rag_adaptacyjny",
    model="gemini-2.5-flash",
    instruction="""Jesteś inteligentnym asystentem RAG z adaptacyjną strategią wyszukiwania.

STRATEGIA WYSZUKIWANIA:
1. Dla PROSTYCH pytań (jedno konkretne pytanie):
   - Użyj wyszukiwania raz
   - Skoncentruj się na najlepszym wyniku

2. Dla ZŁOŻONYCH pytań (wiele aspektów):
   - Możesz użyć wyszukiwania wielokrotnie
   - Zbierz informacje z różnych źródeł
   - Połącz wyniki w spójną odpowiedź

3. Dla pytań O PORÓWNANIE:
   - Wyszukaj informacje o każdym elemencie
   - Przedstaw porównanie w formie tabeli lub listy

ZAWSZE:
- Cytuj źródła
- Bądź precyzyjny
- Jeśli brak informacji w bazie, przyznaj się

Przykład dobrej odpowiedzi:
"Według dokumentu 'Procedury Wdrożeniowe' (sekcja 2.1), proces składa się z 3 etapów:
1. Analiza (źródło: sekcja 2.1.1)
2. Implementacja (źródło: sekcja 2.1.2)
3. Weryfikacja (źródło: sekcja 2.1.3)

Dodatkowo, dokument 'Polityka Bezpieczeństwa' (sekcja 4.2) wymaga audytu
bezpieczeństwa przed każdym wdrożeniem."
""",
    description="Adaptacyjny asystent RAG dostosowujący strategię do pytania",
    tools=[rag_tool_medium]  # Średni limit jako kompromis
)

# Możesz użyć tego agenta jako root_agent:
# root_agent = agent_rag_adaptacyjny


"""
Moduł 1: Hello World Agent - ROZWIĄZANIA ĆWICZEŃ
=================================================
Ten plik zawiera rozwiązania wszystkich ćwiczeń z README.md dla Module 01.

Ćwiczenia:
1. Modyfikacja osobowości agenta (formalny vs swobodny)
2. Wypróbowanie różnych modeli LLM
3. Dodanie specyficznego kontekstu do instrukcji
"""

from google.adk.agents import LlmAgent

# =============================================================================
# ĆWICZENIE 1.1: MODYFIKACJA OSOBOWOŚCI
# =============================================================================
# Zadanie: Zmień instrukcję, aby agent był bardziej formalny lub bardziej swobodny.

# Rozwiązanie A: Agent FORMALNY
agent_formalny = LlmAgent(
    name="asystent_formalny",
    model="gemini-2.5-flash",
    instruction="""Jestem profesjonalnym asystentem AI działającym zgodnie z najwyższymi 
standardami obsługi klienta.

Moje kompetencje obejmują:
1. Udzielanie precyzyjnych odpowiedzi na zapytania użytkowników
2. Wsparcie w rozwiązywaniu zagadnień technicznych
3. Przekazywanie wiedzy specjalistycznej w sposób metodyczny
4. Zapewnienie dokładnych i weryfikowalnych informacji

Zasady komunikacji:
- Stosowanie formalnego języka polskiego
- Zachowanie profesjonalnego dystansu
- Precyzja i konkretność w odpowiedziach
- Unikanie kolokwializmów i potocznego języka

Każda interakcja jest traktowana z najwyższą powagą i profesjonalizmem.
""",
    description="Formalny asystent AI z profesjonalnym tonem komunikacji"
)

# Rozwiązanie B: Agent SWOBODNY
agent_swobodny = LlmAgent(
    name="asystent_swobodny",
    model="gemini-2.5-flash",
    instruction="""Hej! Jestem Twoim ziomkiem AI, gotowym pomóc w każdej sprawie! 😊

Co mogę dla Ciebie zrobić:
1. Odpowiadać na pytania w luźny, przyjacielski sposób
2. Pomagać z kodem i technicznymi sprawami (bez zbędnego formalizmu!)
3. Tłumaczyć skomplikowane rzeczy prostym językiem
4. Po prostu gadać i pomagać jak dobry kolega

Mój styl:
- Luz i swoboda w rozmowie
- Używam potocznego języka, emotikon 🎉
- Bez sztywnych formalności
- Jak rozmowa z kumplem przy kawie ☕

Pytaj śmiało o co chcesz - jestem tu dla Ciebie!
""",
    description="Swobodny asystent AI z przyjacielskim tonem komunikacji"
)

# =============================================================================
# ĆWICZENIE 1.2: WYPRÓBUJ RÓŻNE MODELE
# =============================================================================
# Zadanie: Zmień gemini-2.5-flash na gemini-2.0-flash i zaobserwuj różnice.

# Rozwiązanie: Agenci z różnymi modelami do porównania

agent_gemini_2_5_flash = LlmAgent(
    name="asystent_gemini_2_5",
    model="gemini-2.5-flash",  # Najnowszy model - szybki i wydajny
    instruction="""Jestem asystentem AI opartym na modelu Gemini 2.5 Flash.

Ten model charakteryzuje się:
- Bardzo szybkim czasem odpowiedzi
- Niskimi kosztami operacyjnymi
- Dobrą jakością odpowiedzi dla większości zadań
- Optymalizacją pod kątem wydajności

Używaj mnie do codziennych zadań wymagających szybkich odpowiedzi!
""",
    description="Asystent używający modelu Gemini 2.5 Flash"
)

agent_gemini_2_0_flash = LlmAgent(
    name="asystent_gemini_2_0",
    model="gemini-2.0-flash",  # Poprzednia wersja modelu
    instruction="""Jestem asystentem AI opartym na modelu Gemini 2.0 Flash.

Ten model to:
- Stabilna, sprawdzona wersja
- Dobra równowaga między jakością a szybkością
- Szeroko przetestowany w produkcji
- Niezawodny wybór dla większości aplikacji

Porównaj moje odpowiedzi z nowszymi modelami!
""",
    description="Asystent używający modelu Gemini 2.0 Flash"
)

# WSKAZÓWKA: Aby przetestować różnice:
# 1. Uruchom adk web
# 2. Zadaj to samo pytanie obu agentom
# 3. Porównaj:
#    - Szybkość odpowiedzi
#    - Jakość i szczegółowość
#    - Styl komunikacji
#    - Dokładność informacji

# =============================================================================
# ĆWICZENIE 1.3: DODAJ KONTEKST
# =============================================================================
# Zadanie: Dodaj specyficzną wiedzę do instrukcji (np. historię firmy, nazwy produktów).

# Rozwiązanie: Agent z kontekstem firmy technologicznej

agent_z_kontekstem = LlmAgent(
    name="asystent_techcorp",
    model="gemini-2.5-flash",
    instruction="""Jestem asystentem AI firmy TechCorp Solutions - wiodącego dostawcy 
rozwiązań chmurowych w Polsce.

KONTEKST FIRMY:
- Założona: 2015 rok w Warszawie
- Specjalizacja: Rozwiązania AI i Cloud Computing
- Główne produkty:
  * CloudMaster Pro - platforma zarządzania chmurą
  * DataFlow AI - system analizy danych w czasie rzeczywistym
  * SecureVault - bezpieczne przechowywanie danych
  * DevOps Suite - narzędzia CI/CD dla zespołów

KLUCZOWI KLIENCI:
- Banki: PKO BP, mBank, ING
- E-commerce: Allegro, Empik
- Telekomunikacja: Orange, T-Mobile

WARTOŚCI FIRMY:
- Innowacyjność i ciągły rozwój
- Bezpieczeństwo danych klientów
- Wsparcie 24/7 w języku polskim
- Transparentność i uczciwość

Moja rola:
1. Odpowiadanie na pytania o produkty TechCorp
2. Pomoc techniczna dla klientów
3. Informacje o cenach i planach subskrypcji
4. Wsparcie w procesie wdrożenia

Zawsze odnoszę się do naszych produktów i wartości w odpowiedziach!
""",
    description="Asystent firmy TechCorp Solutions z pełnym kontekstem biznesowym"
)

# =============================================================================
# AGENT GŁÓWNY - Wybierz który chcesz użyć
# =============================================================================
# Odkomentuj jedną z poniższych linii, aby wybrać agenta do uruchomienia:

# root_agent = agent_formalny          # Ćwiczenie 1.1 - Formalny
# root_agent = agent_swobodny          # Ćwiczenie 1.1 - Swobodny
# root_agent = agent_gemini_2_5_flash  # Ćwiczenie 1.2 - Gemini 2.5
# root_agent = agent_gemini_2_0_flash  # Ćwiczenie 1.2 - Gemini 2.0
root_agent = agent_z_kontekstem      # Ćwiczenie 1.3 - Z kontekstem (domyślny)

# =============================================================================
# JAK UŻYWAĆ TEGO PLIKU
# =============================================================================
# 1. Skopiuj ten plik jako agent.py (lub zmień nazwę)
# 2. Wybierz agenta odkomentowując odpowiednią linię root_agent
# 3. Uruchom: adk web
# 4. Testuj różne warianty i porównuj wyniki!
#
# PRZYKŁADOWE PYTANIA DO TESTOWANIA:
# - "Kim jesteś i czym się zajmujesz?"
# - "Opowiedz mi o Pythonie"
# - "Jakie są Twoje produkty?" (dla agent_z_kontekstem)
# - "Pomóż mi zrozumieć machine learning"
# =============================================================================


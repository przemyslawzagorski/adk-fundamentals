"""
Moduł 1: Hello World Agent - Podstawowy Agent
==============================================
Prosty LlmAgent wprowadzający podstawowe koncepcje ADK.

Ten agent służy jako asystent, odpowiadając na pytania użytkowników
w przyjazny i pomocny sposób.

Cele edukacyjne:
- Zrozumienie struktury LlmAgent
- Konfiguracja parametrów modelu i instrukcji
- Uruchomienie agenta za pomocą interfejsu ADK web
- Obserwacja zachowania i odpowiedzi agenta
"""

import os
from google.adk.agents import LlmAgent
from google.adk.tools import google_search
# =============================================================================
# PODSTAWOWY AGENT ASYSTENT
# =============================================================================
# LlmAgent jest fundamentem wszystkich agentów ADK. Opakowuje model LLM
# i zapewnia ustrukturyzowany sposób interakcji z nim.

root_agent = LlmAgent(
    # Identyfikator agenta - używany do logowania i referencji w systemach wieloagentowych
    name="asystent_podstawowy",

    # Model LLM - gemini-3.5-flash-lite: najtańszy (~5x taniej niż 3.5-flash)
    # Inne opcje (ADK_MODEL w .env): gemini-3.5-flash, gemini-3.8-flash
    model=os.getenv("ADK_MODEL", "gemini-3.5-flash-lite"),
    # Instrukcja systemowa - definiuje osobowość i zachowanie agenta
    # To najważniejsza konfiguracja kształtująca odpowiedzi
    instruction="""Jesteś pomocnym asystentem AI. Twoje zadania to:

1. Odpowiadanie na pytania użytkowników w jasny i zrozumiały sposób
2. Pomaganie w rozwiązywaniu problemów programistycznych
3. Dzielenie się wiedzą techniczną w przystępny sposób
4. Dostarczanie dokładnych i pomocnych informacji

Zasady odpowiedzi:
- Używaj jasnego, profesjonalnego języka polskiego
- Bądź pomocny i konkretny
- Przy pytaniach technicznych podawaj dokładne informacje z przykładami
- Jeśli czegoś nie wiesz, przyznaj się do tego uczciwie

Pamiętaj: Dobry asystent służy użytkownikom z wiedzą i cierpliwością!
""",

    # Opis - pomaga innym agentom zrozumieć cel tego agenta
    # Ważne w systemach wieloagentowych (omówione w późniejszych modułach)
    description="Podstawowy asystent AI pomagający użytkownikom w odpowiadaniu "
                "na pytania i dostarczaniu informacji technicznych.",
    tools=[google_search]
)

# =============================================================================
# JAK URUCHOMIĆ TEGO AGENTA
# =============================================================================
# 1. Skonfiguruj zmienne środowiskowe (skopiuj .env.template do .env)
# 2. Uruchom: adk web
# 3. Otwórz interfejs webowy i wybierz "asystent_podstawowy"
# 4. Zacznij rozmawiać z agentem!
#
# Przykładowe pytania do wypróbowania:
# - "Cześć! Kim jesteś i czym się zajmujesz?"
# - "Opowiedz mi o programowaniu w Pythonie"
# - "Jak działa agent AI?"
# - "Pomóż mi zrozumieć czym jest ADK"
# =============================================================================


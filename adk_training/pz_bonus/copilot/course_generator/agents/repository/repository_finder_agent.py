"""
🔍 Repository Finder Agent
Znajduje optymalne repozytorium Java do ćwiczeń
"""

import os
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

from google.adk.agents import LlmAgent


class RepositoryInfo(BaseModel):
    """Informacje o wybranym repozytorium"""
    name: str = Field(description="Nazwa repozytorium")
    full_name: str = Field(description="Pełna nazwa (owner/repo)")
    url: str = Field(description="URL do repozytorium")
    clone_url: str = Field(description="URL do klonowania")
    description: str = Field(description="Opis repozytorium")
    stars: int = Field(description="Liczba gwiazdek")
    language: str = Field(description="Główny język programowania")
    topics: List[str] = Field(description="Tagi/tematy")
    license: str = Field(description="Licencja")
    rationale: str = Field(description="Uzasadnienie wyboru")
    suitability_score: float = Field(description="Ocena przydatności (0-10)")


class RepositorySearchResult(BaseModel):
    """Wynik wyszukiwania repozytorium"""
    selected_repository: RepositoryInfo = Field(description="Wybrane repozytorium")
    alternative_repositories: List[RepositoryInfo] = Field(description="Alternatywne repozytoria (top 3)")
    search_summary: str = Field(description="Podsumowanie wyszukiwania")


def create_repository_finder_agent(model="gemini-2.5-flash", tools=None, planner=None, **kwargs):
    """
    Tworzy agenta do wyszukiwania repozytorium.
    
    Args:
        model: Model Gemini do użycia
        tools: Lista narzędzi (search_github)
        planner: Opcjonalny planner
    
    Returns:
        LlmAgent skonfigurowany do wyszukiwania
    """
    
    instruction = """Jesteś ekspertem w wyszukiwaniu i ocenie repozytoriów open-source.

**KONTEKST:**
Szukasz JEDNEGO uniwersalnego repozytorium Java do ćwiczeń dla WSZYSTKICH modułów szkolenia Copilot.
Otrzymujesz plan szkolenia z poprzedniego agenta.

**TWOJE ZADANIE:**

1. **PRZEANALIZUJ PLAN SZKOLENIA:**
   - Jakie koncepcje będą omawiane? (Agents, MCP, Customization, etc.)
   - Jakie ćwiczenia są planowane?
   - Czego potrzebujemy w repozytorium?

2. **OKREŚL WYMAGANIA:**
   
   **MUST-HAVE:**
   - Język: Java (Spring Boot preferowany)
   - Struktura: wielowarstwowa (controller, service, repository)
   - Testy: JUnit/TestNG
   - Build: Maven lub Gradle
   - Rozmiar: średni (1000-10000 KB) - nie za prosty, nie za skomplikowany
   - Licencja: MIT, Apache 2.0 lub podobna
   - Gwiazdki: min. 500+
   
   **NICE-TO-HAVE:**
   - REST API
   - Database (JPA/Hibernate)
   - Frontend (opcjonalnie)
   - Docker support
   - Aktywnie utrzymywane (ostatni commit < 6 miesięcy)
   - Dobra dokumentacja

3. **UŻYJ NARZĘDZIA search_github:**
   
   Wykonaj wyszukiwanie z zapytaniami typu:
   - "spring boot sample application"
   - "spring petclinic"
   - "spring boot rest api example"
   - "java spring boot demo"
   
   Parametry:
   - language: "Java"
   - min_stars: 500
   - max_results: 20

4. **OCEŃ REPOZYTORIA** według kryteriów:
   
   **Scoring (0-10):**
   - Gwiazdki (0-2 pkt): stars/1000 (max 2)
   - Licencja (0-2 pkt): MIT/Apache = 2, inne = 1, brak = 0
   - Tematy (0-2 pkt): spring, boot, rest, testing = +0.5 każdy
   - Rozmiar (0-2 pkt): 1000-10000 KB = 2, <1000 = 1, >10000 = 1
   - Aktywność (0-2 pkt): ostatni commit < 3 mies = 2, < 6 mies = 1

5. **WYBIERZ NAJLEPSZE REPOZYTORIUM:**
   - Najwyższy score
   - Uzasadnij wybór (dlaczego to repo jest idealne?)
   - Podaj 3 alternatywy

**REKOMENDOWANE REPOZYTORIA (jeśli znajdziesz):**
- spring-projects/spring-petclinic (klasyka!)
- jhipster/jhipster-sample-app
- Inne Spring Boot samples

**FORMAT ODPOWIEDZI:**
Zwróć strukturyzowany JSON zgodny z modelem RepositorySearchResult.

**PRZYKŁAD UZASADNIENIA:**
"spring-petclinic to idealne repozytorium do szkolenia:
- Klasyczna aplikacja Spring Boot z wieloma warstwami
- Ma REST API, testy, JPA, Thymeleaf
- Dobrze udokumentowane, aktywnie utrzymywane
- Wystarczająco złożone do pokazania Agents, MCP, Customization
- Nie za skomplikowane - kursanci szybko zrozumieją strukturę"

**DOSTĘP DO DANYCH:**
Plan szkolenia (podsumowanie modułów) jest przekazany w initial_message jako JSON.

**WAŻNE:**
Jeśli narzędzie search_github nie jest dostępne, zaproponuj spring-petclinic jako default
(https://github.com/spring-projects/spring-petclinic).

Rozpocznij wyszukiwanie!
"""
    
    return LlmAgent(
        model=model,
        name="RepositoryFinderAgent",
        instruction=instruction,
        tools=tools or [],
        planner=planner,
        output_schema=RepositorySearchResult,
        **kwargs
    )


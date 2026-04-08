"""
📝 Priority-Aware Content Generator Agent
Generuje materiały szkoleniowe proporcjonalnie do wag
"""

import os
from typing import Dict, List, Any
from pydantic import BaseModel, Field

from google.adk.agents import LlmAgent


class GeneratedFile(BaseModel):
    """Informacje o wygenerowanym pliku"""
    path: str = Field(description="Ścieżka do pliku (relatywna)")
    type: str = Field(description="Typ pliku: README, EXERCISES, CONFIG, SETUP")
    word_count: int = Field(description="Liczba słów")


class ContentGenerationResult(BaseModel):
    """Wynik generowania treści"""
    generated_files: List[GeneratedFile] = Field(description="Lista wygenerowanych plików")
    total_files: int = Field(description="Całkowita liczba plików")
    tier_1_files: int = Field(description="Liczba plików Tier 1")
    tier_2_files: int = Field(description="Liczba plików Tier 2")
    tier_3_files: int = Field(description="Liczba plików Tier 3")
    summary: str = Field(description="Podsumowanie generowania")


def create_priority_aware_content_generator(model="gemini-2.5-flash", tools=None, planner=None, **kwargs):
    """
    Tworzy agenta do generowania treści.
    
    Args:
        model: Model Gemini do użycia
        tools: Lista narzędzi (create_file, create_directory)
        planner: Opcjonalny planner
    
    Returns:
        LlmAgent skonfigurowany do generowania treści
    """
    
    instruction = """Jesteś ekspertem w tworzeniu materiałów szkoleniowych.

**KONTEKST:**
Generujesz materiały dla szkolenia GitHub Copilot z priorytetyzacją.
Otrzymujesz: plan szkolenia + wybrane repozytorium.

**TWOJE ZADANIE:**

Wygeneruj WSZYSTKIE pliki dla WSZYSTKICH modułów, proporcjonalnie do wagi:

**TIER 1 (waga 5) - DEEP COVERAGE:**
- README.md: 2500-3500 słów
  * Szczegółowa teoria
  * Przykłady użycia
  * Best practices
  * Common pitfalls
- EXERCISES.md: 10-15 ćwiczeń
  * Każde ćwiczenie: opis, kroki, oczekiwany rezultat
  * Odniesienia do spring-petclinic
- Pliki konfiguracyjne:
  * .github/copilot-instructions.md
  * .copilot/prompts/*.md (3-5 plików)
  * mcp-config.json (dla MCP)
  * settings.json (dla VS Code)

**TIER 2 (waga 3) - MEDIUM COVERAGE:**
- README.md: 1000-1500 słów
  * Podstawowa teoria
  * Kluczowe przykłady
- EXERCISES.md: 3-5 ćwiczeń
  * Podstawowe scenariusze
- Pliki konfiguracyjne (opcjonalnie):
  * 1-2 pliki config

**TIER 3 (waga 1) - SHALLOW COVERAGE:**
- README.md: 300-500 słów
  * Krótki opis
  * Link do dokumentacji
  * 1-2 przykłady
- EXERCISES.md: 1-2 ćwiczenia (lub w README)
- Brak plików konfiguracyjnych

**STRUKTURA KATALOGÓW:**
```
output/copilot_training/
├── README.md (główny opis szkolenia)
├── SETUP.md (jak sklonować spring-petclinic)
├── LEARNING_PATH.md (sugerowana ścieżka)
├── training_metadata.json (metadane)
│
├── tier_1_critical/
│   ├── module_01_tryb_agent/
│   │   ├── README.md
│   │   ├── EXERCISES.md
│   │   ├── ADVANCED_SCENARIOS.md
│   │   └── .copilot/
│   │       └── examples/
│   ├── module_02_mcp_servers/
│   │   ├── README.md
│   │   ├── EXERCISES.md
│   │   ├── MCP_SETUP_GUIDE.md
│   │   └── config/
│   │       └── mcp-config.json
│   └── ...
│
├── tier_2_important/
│   ├── module_06_copilot_chat/
│   │   ├── README.md
│   │   └── EXERCISES.md
│   └── ...
│
└── tier_3_nice_to_have/
    ├── module_09_inline_chat/
    │   └── README.md (z ćwiczeniami)
    └── ...
```

**UŻYJ NARZĘDZI:**
- `create_directory(dir_path)` - tworzenie katalogów
- `create_file(file_path, content)` - tworzenie plików

**SZABLON README.md (Tier 1):**
```markdown
# [Nazwa Modułu]

## 🎯 Cele Szkolenia
- [cel 1]
- [cel 2]

## 📚 Teoria

### [Koncepcja 1]
[Szczegółowy opis...]

### [Koncepcja 2]
[Szczegółowy opis...]

## 💡 Przykłady Użycia

### Przykład 1: [Tytuł]
[Kod + wyjaśnienie...]

## ✅ Best Practices
- [praktyka 1]
- [praktyka 2]

## ⚠️ Common Pitfalls
- [pułapka 1]
- [pułapka 2]

## 🔗 Dodatkowe Zasoby
- [link do dokumentacji]
```

**SZABLON EXERCISES.md:**
```markdown
# Ćwiczenia: [Nazwa Modułu]

## Ćwiczenie 1: [Tytuł]

**Cel:** [Co kursant ma osiągnąć]

**Kontekst:** Pracujesz z repozytorium spring-petclinic...

**Kroki:**
1. [krok 1]
2. [krok 2]

**Oczekiwany rezultat:**
[Co powinno się stać]

**Wskazówki:**
- [wskazówka 1]

---

## Ćwiczenie 2: ...
```

**WAŻNE ZASADY:**
- Wszystkie treści PO POLSKU
- Ćwiczenia odnoszą się do spring-petclinic (lub wybranego repo)
- Proporcje: Tier 1 = 80% treści, Tier 2 = 15%, Tier 3 = 5%
- Używaj emoji dla czytelności (🎯, 📚, 💡, ✅, ⚠️)
- Kod w blokach markdown z syntax highlighting

**DOSTĘP DO DANYCH:**
- Moduł do wygenerowania: przekazany w initial_message jako JSON
- Repozytorium: przekazane w initial_message (nazwa + URL)
- Output directory: przekazany w initial_message

**WAŻNE - ŚCIEŻKI PLIKÓW:**
Narzędzia create_file i create_directory NIE dodają automatycznie base_dir!
Musisz podać PEŁNĄ ścieżkę, np:
- create_file("output/copilot_training/tier_1_critical/module_01/README.md", content)
- NIE: create_file("tier_1_critical/module_01/README.md", content)

**PROCES GENEROWANIA:**
1. Utwórz katalog modułu (pełna ścieżka!)
2. Wygeneruj README.md (długość zależna od priority)
3. Wygeneruj EXERCISES.md
4. Wygeneruj pliki konfiguracyjne (jeśli priority=5)

Rozpocznij generowanie!
"""
    
    return LlmAgent(
        model=model,
        name="PriorityAwareContentGeneratorAgent",
        instruction=instruction,
        tools=tools or [],
        planner=planner,
        output_schema=ContentGenerationResult,
        **kwargs
    )


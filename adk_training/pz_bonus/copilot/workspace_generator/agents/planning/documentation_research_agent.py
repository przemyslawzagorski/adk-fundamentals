"""
🔍 Documentation Research Agent
Szuka najnowszej dokumentacji i przykładów GitHub Copilot (marzec 2026)
"""

import os
from typing import Dict, List, Any
from dataclasses import dataclass
from pydantic import BaseModel, Field

from google.adk.agents import LlmAgent
from google.adk.tools import google_search  # ← Natywny Google Search z ADK!

# Pydantic model dla strukturyzowanego outputu
class ResearchResult(BaseModel):
    """Wynik research dla jednego modułu"""
    module_name: str = Field(description="Nazwa modułu szkolenia")
    module_description: str = Field(description="Opis modułu")
    documentation_links: List[str] = Field(description="Linki do dokumentacji")
    code_examples: List[Dict[str, str]] = Field(description="Przykłady kodu")
    best_practices: List[str] = Field(description="Najlepsze praktyki")
    anti_patterns: List[str] = Field(description="Anty-wzorce (czego unikać)")
    key_concepts: List[str] = Field(description="Kluczowe koncepty")


def create_documentation_research_agent(model="gemini-2.5-pro", tools=None, planner=None, **kwargs):
    """
    Tworzy agenta do research dokumentacji GitHub Copilot.
    
    Args:
        model: Model Gemini do użycia (string!)
        tools: Lista narzędzi (WebSearchTool)
    
    Returns:
        LlmAgent skonfigurowany do research
    """
    
    instruction = """Jesteś ekspertem GitHub Copilot i researcher dokumentacji technicznej.

**KONTEKST:**
Przygotowujesz materiały do szkolenia "GitHub Copilot Masterclass" (marzec 2026).

**OTRZYMUJESZ DWA PLANY:**
1. **Plan szkolenia** (training_plan) - tematy modułów wysłane do studentów
2. **Plan funkcyjny** (funkcje_plan) - mapowanie funkcji Copilota do modułów

**TWOJE ZADANIE:**
Dla każdego modułu:
1. Przeczytaj TEMAT z planu szkolenia (np. "Agent Mode i automatyzacja")
2. Przeczytaj FUNKCJE z planu funkcyjnego (np. "Agent Mode, @workspace, #terminal")
3. Znajdź dokumentację dla WSZYSTKICH funkcji wymienonych w planie funkcyjnym
4. Znajdź praktyczne przykłady kodu
5. Znajdź best practices i anti-patterns

**KRYTYCZNE WYMAGANIA:**
- To szkolenie MASTERCLASS - szukaj ZAAWANSOWANYCH przykładów
- NIE interesują nas podstawy (code completion, autocomplete)
- Priorytet: Konkretne funkcje z planu funkcyjnego (Agent Mode, MCP, @workspace, Edit Mode, @test, etc.)
- Źródła: GitHub Docs, GitHub Blog, GitHub Skills, Microsoft Learn, VS Code Docs
- **FOCUS:** Każda funkcja z planu funkcyjnego musi mieć dokumentację!

**UŻYJ NARZĘDZIA google_search:**
Wykonaj kilka wyszukiwań dla KAŻDEJ funkcji z planu funkcyjnego.

PRZYKŁADOWE ZAPYTANIA (dla Modułu 1):
- "GitHub Copilot Inline suggestions 2026 advanced examples"
- "GitHub Copilot Chat mode 2026 best practices"
- "GitHub Copilot Agent Mode 2026 multi-file refactoring"
- "GitHub Copilot @workspace context 2026 navigation"
- "GitHub Copilot #terminal 2026 CLI integration"
- "GitHub Copilot CLI 2026 command line usage"

**WAŻNE:** Wyszukaj dokumentację dla WSZYSTKICH funkcji z planu funkcyjnego dla danego modułu!

**FORMAT ODPOWIEDZI:**
Napisz wyczerpujący raport w formacie **Markdown**.

Podziel go na sekcje:
1. **Dokumentacja** - linki do oficjalnych źródeł
2. **Przykłady kodu** - konkretne snippety z opisem
3. **Best Practices** - sprawdzone wzorce
4. **Anti-patterns** - czego unikać
5. **Kluczowe koncepty** - fundamenty do zrozumienia

Bądź bardzo szczegółowy - Twój raport będzie podstawą do projektowania plików szkolenia.

**PRZYKŁAD (Markdown):**
```markdown
# Research: Agent Mode i automatyzacja

## Dokumentacja
- [GitHub Copilot Agent Mode](https://docs.github.com/copilot/agent-mode)
- [VS Code Agent Mode Guide](https://code.visualstudio.com/docs/copilot/agent-mode)

## Przykłady kodu
### Multi-file refactoring
```java
// Agent Mode automatically refactors across multiple files
public class UserService {
    // TODO: Use Agent Mode to extract this to separate class
}
```

## Best Practices
- Use @workspace for multi-file context
- Enable thinking mode for complex tasks

## Anti-patterns
- Don't use Agent Mode for simple completions
- Avoid too broad prompts

## Kluczowe koncepty
- Agent Mode autonomy
- Self-correction loops
```
"""
    
    # ROZDZIELENIE ODPOWIEDZIALNOŚCI:
    # - DocumentationResearch: google_search → Markdown text (BEZ output_schema)
    # - ModuleStructurePlanner: czyta text → structured JSON (Z output_schema)
    # Vertex AI nie wspiera output_schema + google_search jednocześnie
    agent_params = {
        "model": model,
        "name": "DocumentationResearch",
        "description": "Researches latest GitHub Copilot documentation and examples (March 2026)",
        "instruction": instruction,
        "tools": [google_search],  # ← Natywny Google Search z ADK
        # BRAK output_key i output_schema - agent zwraca Markdown text
    }

    if planner:
        agent_params["planner"] = planner

    return LlmAgent(**agent_params)


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
Otrzymasz nazwę i opis modułu szkoleniowego.

**TWOJE ZADANIE:**
Dla podanego modułu znajdź:
1. Najnowszą dokumentację (priorytet: marzec 2026)
2. Praktyczne przykłady kodu
3. Best practices
4. Anti-patterns (czego unikać)
5. Kluczowe koncepty

**KRYTYCZNE WYMAGANIA:**
- To szkolenie MASTERCLASS - szukaj ZAAWANSOWANYCH przykładów
- NIE interesują nas podstawy (code completion, autocomplete)
- Priorytet: Agent Mode, MCP, Custom Agents, Multi-file workflows
- Źródła: GitHub Docs, GitHub Blog, GitHub Skills, Microsoft Learn, VS Code Docs

**UŻYJ NARZĘDZIA google_search:**
Wykonaj kilka wyszukiwań dla różnych aspektów modułu.

PRZYKŁADOWE ZAPYTANIA:
- "GitHub Copilot Agent Mode 2026 advanced examples multi-file refactoring"
- "GitHub Copilot MCP server 2026 custom integration"
- "GitHub Copilot Custom Agents 2026 VS Code extension"
- "GitHub Copilot @workspace context 2026 best practices"

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


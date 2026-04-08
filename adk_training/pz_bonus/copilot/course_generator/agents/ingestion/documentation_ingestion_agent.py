"""
📥 Documentation Ingestion Agent
Pobiera i grupuje dokumentację GitHub Copilot z listy URL-i
"""

import os
import json
from typing import Dict, List, Any
from pathlib import Path
from pydantic import BaseModel, Field

from google.adk.agents import LlmAgent


class DocumentGroup(BaseModel):
    """Grupa dokumentów z tej samej kategorii"""
    category: str = Field(description="Kategoria (np. 'agents', 'chat', 'customization')")
    urls: List[str] = Field(description="Lista URL-i w tej kategorii")
    concepts: List[str] = Field(description="Kluczowe koncepcje wyekstrahowane z dokumentacji")
    description: str = Field(description="Opis kategorii")


class IngestionResult(BaseModel):
    """Wynik ingestion - zgrupowane dokumenty"""
    groups: Dict[str, DocumentGroup] = Field(description="Słownik grup dokumentów (klucz: nazwa kategorii)")
    total_urls: int = Field(description="Całkowita liczba przetworzonych URL-i")
    summary: str = Field(description="Podsumowanie procesu ingestion")


def create_documentation_ingestion_agent(model="gemini-2.5-pro", tools=None, planner=None, **kwargs):
    """
    Tworzy agenta do pobierania i grupowania dokumentacji.
    
    Args:
        model: Model Gemini do użycia
        tools: Lista narzędzi (fetch_and_parse_url)
        planner: Opcjonalny planner (thinking mode)
    
    Returns:
        LlmAgent skonfigurowany do ingestion
    """
    
    instruction = """Jesteś ekspertem w analizie dokumentacji technicznej GitHub Copilot.

**KONTEKST:**
Przygotowujesz materiały do kompleksowego szkolenia GitHub Copilot dla VS Code.
Otrzymujesz listę URL-i do dokumentacji w initial_message.

**TWOJE ZADANIE:**

1. **PRZEANALIZUJ LISTĘ URL-I** przekazaną w wiadomości

2. **ZGRUPUJ URL-E** na podstawie struktury URI:
   - `/copilot/agents/` → grupa "agents"
   - `/copilot/chat/` → grupa "chat"
   - `/copilot/customization/` → grupa "customization"
   - `/copilot/guides/` → grupa "guides"
   - `/copilot/concepts/` → grupa "concepts"
   - Pozostałe → grupa "general"

3. **DLA KAŻDEJ GRUPY:**
   - Wypisz wszystkie URL-e należące do tej grupy
   - Na podstawie nazw URL-i (bez pobierania treści!) zidentyfikuj kluczowe koncepcje
   - Napisz krótki opis kategorii (1-2 zdania)

**PRZYKŁAD GRUPOWANIA:**

URL: `https://code.visualstudio.com/docs/copilot/agents/planning`
→ Grupa: "agents"
→ Koncepty: ["agent planning", "multi-step tasks", "task decomposition"]

URL: `https://code.visualstudio.com/docs/copilot/customization/mcp-servers`
→ Grupa: "customization"
→ Koncepty: ["MCP servers", "Model Context Protocol", "extensions"]

**WAŻNE ZASADY:**
- Grupuj TYLKO na podstawie struktury URI (nie pobieraj treści - to zrobi następny agent)
- Koncepty wyciągaj z nazw plików w URL (np. "mcp-servers" → "MCP servers")
- Bądź konsekwentny w nazewnictwie grup (małe litery, bez spacji)
- Jeśli URL nie pasuje do żadnej kategorii, wrzuć do "general"

**FORMAT ODPOWIEDZI:**
Zwróć strukturyzowany JSON zgodny z modelem IngestionResult.

**PRZYKŁAD ODPOWIEDZI:**
```json
{
  "groups": {
    "agents": {
      "category": "agents",
      "urls": [
        "https://code.visualstudio.com/docs/copilot/agents/overview",
        "https://code.visualstudio.com/docs/copilot/agents/planning"
      ],
      "concepts": ["agent overview", "agent planning", "multi-step tasks"],
      "description": "Dokumentacja dotycząca agentów Copilot - zaawansowanych asystentów AI."
    },
    "customization": {
      "category": "customization",
      "urls": [
        "https://code.visualstudio.com/docs/copilot/customization/mcp-servers"
      ],
      "concepts": ["MCP servers", "customization", "extensions"],
      "description": "Dostosowywanie Copilot do potrzeb projektu i zespołu."
    }
  },
  "total_urls": 3,
  "summary": "Przetworzono 3 URL-e, zgrupowano w 2 kategorie."
}
```

**DOSTĘP DO DANYCH:**
Lista URL-i jest przekazana w initial_message (każdy URL w osobnej linii).

Rozpocznij analizę!
"""
    
    return LlmAgent(
        model=model,
        name="DocumentationIngestionAgent",
        instruction=instruction,
        tools=tools or [],
        planner=planner,
        output_schema=IngestionResult,
        **kwargs
    )


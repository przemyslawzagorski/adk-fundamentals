# Stack technologiczny

## Zależności runtime

| Komponent | Technologia | Wersja | Cel |
|-----------|-------------|--------|-----|
| **Framework agentowy** | Google ADK | >=1.28.0 | Orkiestracja agentów, zarządzanie sesją, routing |
| **Model LLM (domyślny)** | Gemini 2.5 Flash | latest | Szybkie zadania: klasyfikacja, formatowanie, review |
| **Model LLM (złożone)** | Gemini 2.5 Pro | latest | Złożone analizy: architektura, synteza |
| **Walidacja danych** | Pydantic | >=2.0 | Project Knowledge Contract, walidacja wejść |
| **Parsowanie YAML** | PyYAML | latest | Frontmatter skilli (agentskills.io) |
| **Konfiguracja** | python-dotenv | latest | Zmienne środowiskowe z pliku `.env` |
| **Integracja MCP** | Comarch MCP Server | via npx | Jira, Confluence, GitLab |
| **Python** | CPython | >=3.11 | Runtime |

---

## Wzorce Google ADK

### Typy agentów

| Typ ADK | Użycie w systemie | Pliki |
|---------|-------------------|-------|
| `LlmAgent` | Każdy wyspecjalizowany agent (12 agentów) | `agents/*.py` |
| `SequentialAgent` | Pipeline kroków w orkiestratorach | `orchestrators/*.py` |
| `ParallelAgent` | Równoległa analiza w `analyze_requirement` | `orchestrators/analyze_requirement.py` |

### Mechanizmy ADK

| Mechanizm | Zastosowanie |
|-----------|-------------|
| `AgentTool` | Root agent → orkiestrator routing |
| `FunctionTool` | Auto-wrapping funkcji Python jako narzędzi |
| `output_key` | Przekazywanie stanu między krokami pipeline |
| `McpToolset` | Integracja z zewnętrznym MCP server |
| `session.state` | Persistentny stan sesji (dict) |

---

## Struktura katalogów

```
module_20_analyst_system/
├── agent.py                          # Root agent (Analyst Captain)
├── .env.template                     # Zmienne środowiskowe
├── requirements.txt                  # Zależności Python
│
├── contract/                         # Kontrakt wiedzy
│   ├── project_knowledge.py          # Modele Pydantic
│   └── sample_contract.json          # Przykład: IoT Connect
│
├── tools/                            # Narzędzia (FunctionTool)
│   ├── file_tools.py                 # read, write, list
│   ├── template_tools.py             # list, load
│   ├── skill_tools.py                # validate, list, get, read, write
│   └── mcp_setup.py                  # Fabryka McpToolset
│
├── prompts/                          # Budowniczy instrukcji
│   └── agent_instructions.py         # load_contract, build_*_instruction
│
├── agents/                           # 12 instrukcji agentów
│   ├── source_collector.py
│   ├── clarity_analyst.py
│   ├── scope_analyst.py
│   ├── cross_ref_analyst.py
│   ├── docs_gap_analyst.py
│   ├── synthesis_agent.py
│   ├── template_writer.py
│   ├── quality_reviewer.py
│   ├── skill_knowledge_extractor.py
│   ├── skill_dedup_checker.py
│   ├── skill_architect.py
│   └── skill_quality_reviewer.py
│
├── orchestrators/                    # 6 orkiestratorów
│   ├── analyze_requirement.py        # 3-step + ParallelAgent
│   ├── create_epic.py                # 4-step
│   ├── generate_document.py          # 5-step + dynamic skills
│   ├── generate_test_plan.py         # 4-step
│   ├── review_document.py            # 3-step
│   └── generate_skill.py             # 6-step Knowledge Loop
│
├── skills/                           # Repozytorium skilli
│   ├── diataxis-writing/SKILL.md
│   ├── style-guide/SKILL.md
│   ├── document-templates/
│   │   ├── SKILL.md
│   │   └── assets/                   # hld, lld, epic, test_plan templates
│   └── requirement-analysis/SKILL.md
│
└── docs/                             # Dokumentacja
```

---

## Testy

| Metryka | Wartość |
|---------|---------|
| Framework testowy | Python unittest (e2e_tests) |
| Liczba testów | 16 |
| Wynik | 16/16 PASS :material-check-circle:{ .green } |
| Plik | `e2e_tests/test_module_20.py` |

### Pokrycie testami

| Obszar | Testy | Status |
|--------|-------|--------|
| Ładowanie root agenta | 1 | :material-check-circle: |
| Walidacja kontraktu | 2 | :material-check-circle: |
| file_tools | 1 | :material-check-circle: |
| template_tools | 1 | :material-check-circle: |
| skill_tools | 1 | :material-check-circle: |
| Struktury orkiestratorów | 3 | :material-check-circle: |
| Opisy orkiestratorów | 1 | :material-check-circle: |
| Frontmatter skilli | 1 | :material-check-circle: |
| Placeholdery szablonów | 1 | :material-check-circle: |
| Instrukcje agentów | 1 | :material-check-circle: |
| Referencje state variables | 1 | :material-check-circle: |
| Prompt builder | 1 | :material-check-circle: |
| output_key chains | 1 | :material-check-circle: |

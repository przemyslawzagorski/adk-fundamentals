# Analyst System — Dokumentacja techniczna

## 1. Architektura systemu

### 1.1. Stack technologiczny

| Komponent | Technologia | Wersja |
|-----------|-------------|--------|
| Framework agentowy | Google ADK | >=1.28.0 |
| Model LLM (domyślny) | Gemini 2.5 Flash | latest |
| Model LLM (złożone) | Gemini 2.5 Pro | latest |
| Walidacja danych | Pydantic | >=2.0 |
| Parsowanie YAML | PyYAML | latest |
| Konfiguracja | python-dotenv | latest |
| Integracja MCP | Comarch MCP Server | via npx |
| Python | CPython | >=3.11 |

### 1.2. Wzorce ADK

System wykorzystuje następujące wzorce Google ADK:

| Wzorzec | Użycie | Pliki |
|---------|--------|-------|
| **LlmAgent** | Każdy agent wyspecjalizowany w jednym zadaniu | `agents/*.py`, orkiestratory |
| **SequentialAgent** | Pipeline kroków w orkiestratorach | Wszystkie orkiestratory |
| **ParallelAgent** | Równoległa analiza w `analyze_requirement` | `orchestrators/analyze_requirement.py` |
| **AgentTool** | Root agent routuje do orkiestratorów | `agent.py` |
| **FunctionTool** | Narzędzia Python wystawione agentom | `tools/*.py` (auto-wrapping) |
| **output_key** | Przekazywanie stanu między krokami | Każdy agent w pipeline |
| **McpToolset** | Integracja z Jira/Wiki/GitLab | `tools/mcp_setup.py` |

### 1.3. Przepływ danych (state passing)

Agenci w pipeline komunikują się przez mechanizm `output_key` ADK:

```
Agent_1 (output_key="result_a")
  → Agent_2 (instruction: "Use {result_a}")  (output_key="result_b")
    → Agent_3 (instruction: "Use {result_a} and {result_b}")
```

Stan jest przechowywany w `session.state` (dict) i automatycznie wstrzykiwany w instrukcje agentów przez ADK.

---

## 2. Struktura katalogów

```
module_20_analyst_system/
├── agent.py                          # Root agent — Analyst Captain router
├── .env.template                     # Zmienne środowiskowe
├── requirements.txt                  # Zależności Python
├── README.md                         # Opis modułu
│
├── contract/                         # Kontrakt wiedzy projektowej
│   ├── __init__.py
│   ├── project_knowledge.py          # Modele Pydantic
│   └── sample_contract.json          # Przykładowy kontrakt (IoT Connect)
│
├── tools/                            # Narzędzia (FunctionTool)
│   ├── __init__.py
│   ├── file_tools.py                 # read_file, write_document, list_files
│   ├── template_tools.py            # list_templates, load_template
│   ├── skill_tools.py               # validate/list/get/read/write skills
│   └── mcp_setup.py                  # Fabryka McpToolset dla Comarch MCP
│
├── prompts/                          # Budowniczy instrukcji
│   ├── __init__.py
│   └── agent_instructions.py        # load_contract, build_*_instruction, discover_relevant_skills
│
├── agents/                           # Instrukcje agentów (INSTRUCTION const)
│   ├── __init__.py
│   ├── source_collector.py           # Zbieranie źródeł
│   ├── clarity_analyst.py            # Analiza jasności wymagań
│   ├── scope_analyst.py              # Analiza zakresu
│   ├── cross_ref_analyst.py          # Analiza zależności
│   ├── docs_gap_analyst.py           # Analiza luk w dokumentacji
│   ├── synthesis_agent.py            # Synteza wyników analiz
│   ├── template_writer.py            # Formatowanie do szablonów
│   ├── quality_reviewer.py           # Recenzja jakości (współdzielony)
│   ├── skill_knowledge_extractor.py  # Ekstrakcja wiedzy (generate_skill)
│   ├── skill_dedup_checker.py        # Sprawdzanie duplikatów
│   ├── skill_architect.py            # Projektowanie skill-i
│   └── skill_quality_reviewer.py     # Recenzja skill-i
│
├── orchestrators/                    # Orkiestratory (SequentialAgent)
│   ├── __init__.py
│   ├── analyze_requirement.py        # 3-step (Sequential → Parallel → Sequential)
│   ├── create_epic.py                # 4-step pipeline
│   ├── generate_document.py          # 5-step pipeline z dynamicznymi skill-ami
│   ├── generate_test_plan.py         # 4-step pipeline
│   ├── review_document.py            # 3-step pipeline
│   └── generate_skill.py            # 6-step Knowledge Loop pipeline
│
├── skills/                           # Baza umiejętności (Agent Skills spec)
│   ├── diataxis-writing/SKILL.md     # Diátaxis framework
│   ├── style-guide/SKILL.md          # Microsoft-inspired style guide
│   ├── document-templates/           # Szablony dokumentów
│   │   ├── SKILL.md
│   │   └── assets/
│   │       ├── hld_template.md
│   │       ├── lld_template.md
│   │       ├── epic_template.md
│   │       └── test_plan_template.md
│   └── requirement-analysis/SKILL.md # Analiza wymagań
│
└── docs/                             # Dokumentacja
    ├── BUSINESS_DOCUMENTATION.md
    └── TECHNICAL_DOCUMENTATION.md
```

---

## 3. Konfiguracja

### 3.1. Zmienne środowiskowe

| Zmienna | Wymagana | Opis |
|---------|----------|------|
| `GOOGLE_API_KEY` | Tak | Klucz API Google AI Studio |
| `ADK_MODEL` | Nie | Model LLM (domyślnie: `gemini-2.5-flash`) |
| `ADK_STRONG_MODEL` | Nie | Model dla złożonych zadań (domyślnie: `gemini-2.5-pro`) |
| `OUTPUT_DIR` | Nie | Katalog wyjściowy (domyślnie: `./output`) |
| `SKILLS_DIR` | Nie | Katalog skill-i (domyślnie: `./skills`) |
| `NODE_EXTRA_CA_CERTS` | Nie | Ścieżka do certyfikatu CA (dla MCP w sieciach korporacyjnych) |
| `COMARCH_MCP_COMMAND` | Nie | Komenda uruchamiająca Comarch MCP Server |

### 3.2. Uruchamianie

```bash
# Kopiuj i skonfiguruj zmienne
cp .env.template .env
# Edytuj .env — ustaw GOOGLE_API_KEY

# Instalacja zależności
pip install -r requirements.txt

# Uruchamianie przez ADK CLI
cd module_20_analyst_system
adk run .

# Lub przez ADK Web UI
adk web .
```

---

## 4. Szczegóły komponentów

### 4.1. Root Agent (`agent.py`)

**Typ:** `LlmAgent` z `AgentTool`

**Rola:** Router — na podstawie treści zapytania kieruje do odpowiedniego orkiestratora.

**Tabela routingu:**

| Pattern w zapytaniu | Orkiestrator docelowy |
|--------------------|-----------------------|
| „przeanalizuj wymaganie", „requirement" | `analyze_requirement` |
| „utwórz epik", „epic", „user story" | `create_epic` |
| „wygeneruj dokument", „HLD", „LLD" | `generate_document` |
| „plan testów", „test plan" | `generate_test_plan` |
| „zrecenzuj", „review" | `review_document` |
| „utwórz skill", „nowa umiejętność" | `generate_skill` |

### 4.2. Kontrakt (`contract/project_knowledge.py`)

**Modele Pydantic v2:**

```python
class ProjectKnowledgeContract(BaseModel):
    project_name: str
    domain: DomainContext
    documentation: DocumentationConfig
    jira: JiraConfig | None = None
    wiki: WikiConfig | None = None
    tech_stack: list[str] = []

class DomainContext(BaseModel):
    domain: str
    bounded_contexts: list[str]
    key_entities: list[str]
    glossary: dict[str, str] = {}

class DocumentationConfig(BaseModel):
    framework: DocumentationFramework = DocumentationFramework.DIATAXIS
    primary_language: DocumentLanguage = DocumentLanguage.POLISH
    style_notes: list[str] = []
```

### 4.3. Orkiestratory — szczegółowy pipeline

#### analyze_requirement (3 kroki)

```
source_collector [collected_sources]
    ↓
ParallelAgent:
  ├── clarity_analyst    [clarity_analysis]
  ├── scope_analyst      [scope_analysis]
  ├── cross_ref_analyst  [cross_ref_analysis]
  └── docs_gap_analyst   [docs_gap_analysis]
    ↓
synthesis_agent [requirement_analysis]
```

#### generate_skill (6 kroków)

```
source_collector      [collected_knowledge]
    ↓
knowledge_extractor   [extracted_knowledge]
    ↓
dedup_checker         [dedup_decision]
    ↓
skill_architect       [skill_draft]
    ↓
quality_reviewer      [skill_reviewed]
    ↓
presenter             [skill_result]
```

#### generate_document (5 kroków)

```
doc_type_classifier    [doc_type]
    ↓
doc_source_collector   [doc_sources]
    ↓
doc_content_writer     [doc_content]        ← dynamicznie ładuje skill-e
    ↓
doc_quality_reviewer   [doc_review]
    ↓
doc_file_writer        [doc_result]
```

#### create_epic (4 kroki)

```
epic_collector      [epic_sources]
    ↓
epic_writer         [epic_content]
    ↓
epic_reviewer       [epic_reviewed]
    ↓
epic_template_writer [epic_result]
```

#### generate_test_plan (4 kroki)

```
test_collector     [test_sources]
    ↓
test_planner       [test_plan_content]
    ↓
test_reviewer      [test_plan_reviewed]
    ↓
test_writer        [test_plan_result]
```

#### review_document (3 kroki)

```
doc_reader         [doc_content]
    ↓
doc_reviewer       [doc_review]           ← ładuje skill-e review
    ↓
review_reporter    [review_result]
```

### 4.4. Narzędzia

| Funkcja | Moduł | Opis |
|---------|-------|------|
| `read_file(path)` | file_tools | Odczyt pliku, zwraca `{status, content, path}` |
| `write_document(name, content, subdir)` | file_tools | Zapis do OUTPUT_DIR |
| `list_files(dir, pattern)` | file_tools | Listowanie plików glob |
| `list_templates()` | template_tools | Lista dostępnych szablonów |
| `load_template(name)` | template_tools | Załadowanie szablonu |
| `validate_skill_name(name)` | skill_tools | Walidacja nazwy wg agentskills.io |
| `list_skills()` | skill_tools | Lista skill-i z metadanymi |
| `get_skill_metadata(name)` | skill_tools | Frontmatter YAML |
| `read_skill(name)` | skill_tools | Pełna treść + referencje + assety |
| `write_skill_draft(name, content)` | skill_tools | Zapis nowego skill-a |
| `create_comarch_mcp()` | mcp_setup | Fabryka McpToolset (Jira, Wiki, GitLab) |

### 4.5. Agent Skills (agentskills.io)

Skill-e są przechowywane w formacie zgodnym ze specyfikacją agentskills.io:

```
skills/<skill-name>/
├── SKILL.md           # Frontmatter YAML + treść (max 500 linii)
├── references/        # Opcjonalne pliki referencyjne
└── assets/            # Opcjonalne zasoby (szablony, przykłady)
```

**Frontmatter:**

```yaml
---
name: skill-name        # 2-64 znaki, lowercase, litery/cyfry/myślniki
description: >-         # USE FOR / DO NOT USE FOR pattern
  Opis kiedy używać skill-a...
metadata:
  version: "1.0"
  globs: ["**/*.md"]    # Opcjonalne filtry plików
---
```

---

## 5. Testowanie

### 5.1. Testy E2E

Lokalizacja: `e2e_tests/test_module_20.py`

**16 testów w 8 kategoriach:**

| Kategoria | Testy | Weryfikacja |
|-----------|-------|-------------|
| Ładowanie modułu | 1 | Root agent: nazwa, typ, 6 AgentTools |
| Kontrakt Pydantic | 2-3 | Walidacja poprawnych i niepoprawnych danych |
| File tools | 4 | read/write/list z temp directory |
| Template tools | 5 | list/load, weryfikacja placeholderów |
| Skill tools | 6 | validate/list/get/read/write (z temp dir) |
| Struktura orkiestratorów | 7-10 | Typy agentów, sub_agents count, descriptions |
| Skill-e i szablony | 11-12 | Frontmatter compliance, TODO placeholders |
| Instrukcje agentów | 13-14 | INSTRUCTION export, state variable refs |
| Prompt builder | 15 | Contract loading, skill discovery |
| Output keys | 16 | Unikalność i kompletność łańcuchów state |

### 5.2. Uruchamianie testów

```bash
# Wszystkie testy modułu 20
python e2e_tests/test_module_20.py

# Wszystkie moduły
python e2e_tests/run_all_tests.py
```

---

## 6. Rozszerzanie systemu

### 6.1. Dodawanie nowego skill-a

1. Utwórz katalog `skills/<skill-name>/`
2. Utwórz `SKILL.md` z frontmatterem YAML
3. Waliduj: `validate_skill_name("<skill-name>")`
4. Opcjonalnie dodaj `references/` i `assets/`
5. Skill jest automatycznie odkrywany przez `list_skills()` i `discover_relevant_skills()`

### 6.2. Dodawanie nowego orkiestratora

1. Utwórz plik `orchestrators/<name>.py`
2. Zdefiniuj agentów jako `LlmAgent` z `output_key`
3. Złóż w `SequentialAgent`
4. Zaimportuj w `agent.py` i dodaj `AgentTool` do root agenta
5. Zaktualizuj instrukcję routera

### 6.3. Dodawanie nowego narzędzia

1. Utwórz funkcję w `tools/` (pure function → dict return)
2. Zaimportuj w odpowiednim orkiestratorze
3. Przekaż jako `tools=[func]` do `LlmAgent` (ADK automatycznie opakowuje w `FunctionTool`)

### 6.4. Zmiana kontraktu projektu

1. Edytuj `contract/sample_contract.json` lub utwórz nowy plik JSON
2. Rozszerz modele w `contract/project_knowledge.py` jeśli potrzeba
3. Kontekst jest automatycznie wstrzykiwany do instrukcji agentów

---

## 7. Zależności i wymagania

### 7.1. Wymagania systemowe

- Python >=3.11
- Node.js (dla Comarch MCP, opcjonalnie)
- Aktywny klucz Google AI Studio API

### 7.2. Zależności Python

```
google-adk>=1.28.0     # Framework agentowy
python-dotenv           # Zmienne środowiskowe
pydantic>=2.0           # Walidacja danych
pyyaml                  # Parsowanie frontmatter YAML
```

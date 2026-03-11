# 🏗️ Architektura Systemu Agentowego

**Szczegółowy opis architektury wieloagentowej dla GitHub Copilot Masterclass Workspace Generator**

---

## 📐 WZORCE ORKIESTRACJI (Google ADK)

### 1. Sequential Agents
**Użycie:** Główny przepływ Planning → Execution → Validation

```python
from google.adk.agents import SequentialAgent

orchestrator = SequentialAgent(
    agents=[
        planning_phase,
        execution_phase,
        validation_phase
    ],
    name="MasterOrchestrator"
)
```

**Dlaczego Sequential?**
- Planning musi zakończyć się przed Execution
- Validation wymaga kompletnego workspace'a
- Jasny, przewidywalny przepływ

---

### 2. Parallel Agents
**Użycie:** Research + Planning, Generowanie modułów 1-3 równolegle

```python
from google.adk.agents import ParallelAgent

planning_phase = ParallelAgent(
    agents=[
        documentation_research_agent,
        module_structure_planner
    ],
    name="PlanningPhase"
)
```

**Dlaczego Parallel?**
- Research i Planning są niezależne
- Moduły 1-3 można generować równolegle
- Oszczędność czasu (3x szybciej)

---

### 3. Loop Agent
**Użycie:** Iteracyjne generowanie kodu z walidacją

```python
from google.adk.agents import LoopAgent

code_generation_loop = LoopAgent(
    agent=java_code_agent,
    critic=syntax_critic,
    max_iterations=3,
    name="CodeGenerationLoop"
)
```

**Dlaczego Loop?**
- Kod może wymagać poprawek (błędy składni)
- Syntax Critic daje feedback
- Max 3 iteracje = balance jakość/czas

---

## 🤖 SZCZEGÓŁOWY OPIS AGENTÓW

### PLANNING PHASE

#### 1. Documentation Research Agent
**Model:** Gemini 2.5-pro + Google Search Tool

**Prompt:**
```
Jesteś ekspertem GitHub Copilot. Analizujesz moduł szkolenia:
{module_name}: {module_description}

Zadanie:
1. Znajdź najnowsze (marzec 2026) przykłady i dokumentację
2. Szukaj: "GitHub Copilot {topic} 2026 examples"
3. Priorytet: GitHub Docs, GitHub Blog, GitHub Skills
4. Zwróć JSON:
{
  "module": "...",
  "documentation_links": [...],
  "code_examples": [...],
  "best_practices": [...],
  "anti_patterns": [...]
}
```

**Tools:**
- `google_search(query: str) -> List[SearchResult]`
- `fetch_url(url: str) -> str`
- `extract_code_snippets(html: str) -> List[CodeSnippet]`

**Output:** JSON z research results dla każdego modułu

---

#### 2. Module Structure Planner
**Model:** Gemini 2.5-pro + thinking mode

**Prompt:**
```
Jesteś architektem workspace'ów szkoleniowych. 
Plan szkolenia: {training_plan}
Research results: {research_results}

Zadanie:
Zaprojektuj strukturę plików dla modułu: {module_name}

Wymagania:
- Kod MUSI zawierać TODO dla Copilot (to Masterclass!)
- Przykłady MUSZĄ być zaawansowane (Agent Mode, MCP, Custom Agents)
- Każdy plik MUSI mieć cel dydaktyczny
- Struktura MUSI wspierać hands-on exercises

Zwróć JSON:
{
  "module": "...",
  "files": [
    {
      "path": "src/module1/AgentModeExample.java",
      "type": "java_code",
      "purpose": "Demonstrate Agent Mode workflow",
      "copilot_todos": 5,
      "difficulty": "advanced"
    },
    ...
  ],
  "dependencies": [...],
  "learning_objectives": [...]
}
```

**Tools:**
- `validate_structure(structure: dict) -> bool`
- `check_dependencies(files: List[File]) -> List[Dependency]`

**Output:** JSON ze strukturą workspace'a

---

#### 3. Planning Aggregator
**Model:** Gemini 2.5-flash

**Zadanie:**
- Łączy wyniki Research + Structure Planner
- Tworzy finalny plan wykonania
- Identyfikuje konflikty i zależności

**Output:** Unified execution plan (JSON)

---

### EXECUTION PHASE

#### 4. Java Code Agent
**Model:** Gemini 2.5-flash

**Prompt:**
```
Jesteś ekspertem Java i GitHub Copilot.
Generujesz kod dla szkolenia Masterclass.

File spec: {file_spec}
Module context: {module_context}
Research examples: {examples}

KRYTYCZNE WYMAGANIA:
1. Kod MUSI być zaawansowany (nie "hello world"!)
2. TODO komentarze MUSZĄ być precyzyjne dla Copilot
3. Przykłady MUSZĄ pokazywać real-world scenarios
4. Kod MUSI kompilować się (Java 17+)

Przykład TODO:
// TODO: Use Copilot Agent Mode to refactor this method
//       Extract validation logic to separate service
//       Apply SOLID principles
//       Hint: @workspace "show me validation patterns"

Wygeneruj kompletny plik Java z:
- Package declaration
- Imports
- Class documentation
- TODO komentarze (min 3-5 per file)
- Partial implementation (70% done, 30% TODO)
```

**Tools:**
- `validate_java_syntax(code: str) -> ValidationResult`
- `count_todos(code: str) -> int`
- `check_complexity(code: str) -> ComplexityScore`

**Output:** Java code (string)

---

#### 5. Syntax Critic
**Model:** Gemini 2.5-flash

**Prompt:**
```
Jesteś code reviewer. Sprawdź kod:
{generated_code}

Kryteria:
1. Czy kompiluje się? (Java 17+)
2. Czy TODO są precyzyjne dla Copilot?
3. Czy przykłady są zaawansowane?
4. Czy kod jest czytelny?

Zwróć JSON:
{
  "valid": true/false,
  "errors": [...],
  "suggestions": [...],
  "quality_score": 1-10
}

Jeśli quality_score < 7, zwróć "RETRY" z sugestiami.
```

**Tools:**
- `compile_java(code: str) -> CompilationResult`
- `run_checkstyle(code: str) -> List[Issue]`

**Output:** Validation result + feedback

---

#### 6. Didactic Content Agent
**Model:** Gemini 2.5-flash

**Zadanie:**
- Generuje README.md dla modułu
- Tworzy instrukcje hands-on
- Pisze learning objectives
- Dodaje hints i tips

**Output:** Markdown files

---

#### 7. Test Generator
**Model:** Gemini 2.5-flash

**Zadanie:**
- Generuje JUnit 5 tests
- Tworzy test scenarios
- Dodaje TODO dla test-driven exercises

**Output:** Test files (Java)

---

#### 8. Config Agent
**Model:** Gemini 2.5-flash

**Zadanie:**
- Tworzy `.github/copilot-instructions.md`
- Generuje `prompt-files/` dla modułów
- Konfiguruje MCP servers (jeśli moduł 7)
- Tworzy `.vscode/settings.json`

**Output:** Config files (JSON, YAML, MD)

---

### VALIDATION PHASE

#### 9. Coherence Validator
**Model:** Gemini 2.5-pro + thinking mode (max 3 iter)

**Prompt:**
```
Jesteś architektem systemów. Sprawdź spójność workspace'a:
{workspace_structure}

Pytania:
1. Czy moduły są logicznie powiązane?
2. Czy dependencies są poprawne?
3. Czy progression jest naturalna (łatwe → trudne)?
4. Czy TODO w module N nie wymagają wiedzy z module N+1?
5. Czy przykłady nie duplikują się?

Zwróć JSON z oceną i sugestiami poprawek.
```

**Tools:**
- `analyze_dependencies(workspace: Workspace) -> DependencyGraph`
- `check_progression(modules: List[Module]) -> ProgressionScore`

**Output:** Validation report + fixes

---

#### 10. Pedagogical Reviewer
**Model:** Gemini 2.5-pro + thinking mode

**Prompt:**
```
Jesteś ekspertem dydaktyki programowania.
Oceń wartość szkoleniową workspace'a:
{workspace}

Kryteria:
1. Czy learning objectives są jasne?
2. Czy hands-on exercises są efektywne?
3. Czy progression jest odpowiednia?
4. Czy materiały są engaging?
5. Czy TODO prowadzą do nauki?

Oceń 1-10 i zasugeruj improvements.
```

**Output:** Pedagogical report (1-10 score)

---

#### 11. Final Reporter
**Model:** Gemini 2.5-flash

**Zadanie:**
- Agreguje wszystkie metryki
- Generuje finalny raport
- Tworzy summary dla trenera

**Output:** Final report (Markdown)

---

## 🔄 PRZEPŁYW DANYCH

```
Training Plan (TXT)
    ↓
[Documentation Research] + [Module Structure Planner]
    ↓
Unified Execution Plan (JSON)
    ↓
[Parallel: Module 1-3 Generators]
    ↓
Workspace Files (Java, MD, JSON)
    ↓
[Coherence Validator] + [Pedagogical Reviewer]
    ↓
Final Workspace + Report
```

---

## 📦 STATE MANAGEMENT

**Shared State między agentami:**
```python
class WorkspaceState:
    training_plan: str
    research_results: Dict[str, ResearchResult]
    execution_plan: ExecutionPlan
    generated_files: List[GeneratedFile]
    validation_results: ValidationResults
    final_report: Report
```

**Przekazywanie kontekstu:**
- Planning Phase → Execution Phase: execution_plan
- Execution Phase → Validation Phase: generated_files
- Validation Phase → Final: validation_results

---

**Następne kroki:** Zobacz `IMPLEMENTATION.md` dla szczegółów implementacji


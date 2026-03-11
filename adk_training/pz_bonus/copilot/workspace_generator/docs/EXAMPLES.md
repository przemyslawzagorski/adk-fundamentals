# 📚 Przykłady Użycia

**Praktyczne przykłady użycia systemu agentowego**

---

## 🎯 PRZYKŁAD 1: Podstawowe Generowanie Workspace'a

### Scenariusz
Generujesz workspace dla pełnego 2-dniowego szkolenia GitHub Copilot Masterclass.

### Kod

```bash
# 1. Przygotuj plan szkolenia
cat > training_plan.txt << EOF
Program Szkolenia: GitHub Copilot Masterclass
Moduł 1: Komunikacja z AI i eksploracja kodu
Moduł 2: Refaktoring z Copilot Edits
...
EOF

# 2. Uruchom generator
python main.py \
    --training-plan training_plan.txt \
    --output-dir ./output/masterclass_2026

# 3. Sprawdź wyniki
ls -la ./output/masterclass_2026/
```

### Oczekiwany Output

```
output/masterclass_2026/
├── module1_komunikacja_ai/
│   ├── src/
│   │   ├── PromptEngineering.java
│   │   ├── ContextManagement.java
│   │   └── FewShotExamples.java
│   ├── tests/
│   │   └── PromptEngineeringTest.java
│   ├── docs/
│   │   ├── README.md
│   │   └── EXERCISES.md
│   └── .github/
│       └── copilot-instructions.md
├── module2_refaktoring/
│   ├── src/
│   │   ├── LegacyCodeRefactoring.java
│   │   ├── SOLIDPrinciples.java
│   │   └── CodeSmellsDetection.java
│   ...
├── generation_state.json
└── FINAL_REPORT.md
```

---

## 🎯 PRZYKŁAD 2: Generowanie Pojedynczego Modułu

### Scenariusz
Chcesz wygenerować tylko Moduł 5 (Agent Mode) do testowania.

### Kod

```python
# custom_generator.py
from workspace_generator import CopilotMasterclassWorkspaceGenerator
from agents.execution.module_generator import ModuleGenerator

# Initialize generator
generator = CopilotMasterclassWorkspaceGenerator(
    training_plan_path="opis_szkolenia_plan_copilot",
    output_dir="./output/module5_test"
)

# Generate only Module 5
module5_generator = ModuleGenerator(
    module_id=5,
    tools=generator.tools
)

# Run with custom state
state = {
    "module_name": "Agent Mode i automatyzacja",
    "module_description": "Autonomiczne operacje, Self-Correction Loop, Custom Agents",
    "research_results": {...}  # From planning phase
}

result = module5_generator.run(state)
print(f"Generated {len(result['files'])} files for Module 5")
```

---

## 🎯 PRZYKŁAD 3: Custom Research dla Specyficznego Tematu

### Scenariusz
Chcesz zbadać najnowsze przykłady MCP (Model Context Protocol) przed generowaniem Modułu 7.

### Kod

```python
# research_mcp.py
from agents.planning.documentation_research_agent import DocumentationResearchAgent
from tools.web_search import WebSearchTool
from google.adk.models import Gemini25Pro

# Initialize agent
research_agent = DocumentationResearchAgent(
    model=Gemini25Pro(),
    tools=[WebSearchTool()],
    name="MCPResearcher"
)

# Research MCP
result = research_agent.research_module(
    module_name="Moduł 7: Model Context Protocol (MCP)",
    module_description="""
    Integracja Copilot z zewnętrznymi systemami
    Architektura i przypadki użycia
    Budowa własnego MCP server
    """
)

# Print results
print(f"Found {len(result.documentation_links)} documentation links:")
for link in result.documentation_links:
    print(f"  - {link}")

print(f"\nBest Practices:")
for practice in result.best_practices:
    print(f"  ✓ {practice}")

print(f"\nAnti-Patterns:")
for anti in result.anti_patterns:
    print(f"  ✗ {anti}")
```

### Output

```
Found 5 documentation links:
  - https://docs.github.com/copilot/customizing-copilot/using-model-context-protocol
  - https://github.com/modelcontextprotocol
  - https://learn.microsoft.com/en-us/nuget/concepts/nuget-mcp-server
  - https://code.visualstudio.com/docs/copilot/customization/mcp-servers
  - https://github.blog/ai-and-ml/mcp-integration-guide

Best Practices:
  ✓ Use MCP for external data integration (databases, APIs)
  ✓ Implement proper authentication and authorization
  ✓ Cache responses to reduce latency
  ✓ Provide clear tool descriptions for Copilot
  ✓ Test MCP servers independently before integration

Anti-Patterns:
  ✗ Don't use MCP for simple file operations (use native tools)
  ✗ Avoid exposing sensitive data without encryption
  ✗ Don't create overly complex MCP servers (keep it simple)
  ✗ Avoid synchronous blocking calls in MCP servers
```

---

## 🎯 PRZYKŁAD 4: Walidacja Wygenerowanego Workspace'a

### Scenariusz
Po wygenerowaniu workspace'a chcesz uruchomić tylko fazę walidacji.

### Kod

```python
# validate_workspace.py
from agents.validation.coherence_validator import CoherenceValidator
from agents.validation.pedagogical_reviewer import PedagogicalReviewer
from google.adk.models import Gemini25Pro
import json

# Load generated workspace state
with open("output/masterclass_2026/generation_state.json") as f:
    state = json.load(f)

# Initialize validators
coherence_validator = CoherenceValidator(
    model=Gemini25Pro(thinking_mode=True),
    max_iterations=3,
    name="CoherenceValidator"
)

pedagogical_reviewer = PedagogicalReviewer(
    model=Gemini25Pro(thinking_mode=True),
    name="PedagogicalReviewer"
)

# Run validation
coherence_result = coherence_validator.validate(state)
pedagogical_result = pedagogical_reviewer.review(state)

# Print results
print("=" * 60)
print("COHERENCE VALIDATION")
print("=" * 60)
print(f"Score: {coherence_result['score']}/10")
print(f"Issues found: {len(coherence_result['issues'])}")
for issue in coherence_result['issues']:
    print(f"  ⚠️  {issue}")

print("\n" + "=" * 60)
print("PEDAGOGICAL REVIEW")
print("=" * 60)
print(f"Score: {pedagogical_result['score']}/10")
print(f"Strengths:")
for strength in pedagogical_result['strengths']:
    print(f"  ✓ {strength}")
print(f"Improvements:")
for improvement in pedagogical_result['improvements']:
    print(f"  → {improvement}")
```

---

## 🎯 PRZYKŁAD 5: Iteracyjne Doskonalenie Kodu

### Scenariusz
Używasz LoopAgent do iteracyjnego generowania i poprawiania kodu Java.

### Kod

```python
# iterative_code_generation.py
from google.adk.agents import LoopAgent
from agents.execution.java_code_agent import JavaCodeAgent
from agents.execution.syntax_critic import SyntaxCritic
from google.adk.models import Gemini25Flash
from tools.code_validator import CodeValidatorTool

# Initialize agents
code_agent = JavaCodeAgent(
    model=Gemini25Flash(),
    tools=[CodeValidatorTool()],
    name="JavaCodeAgent"
)

syntax_critic = SyntaxCritic(
    model=Gemini25Flash(),
    name="SyntaxCritic"
)

# Create loop agent
loop_agent = LoopAgent(
    agent=code_agent,
    critic=syntax_critic,
    max_iterations=3,
    name="CodeGenerationLoop"
)

# Generate code with self-correction
file_spec = {
    "path": "src/module5/AgentModeWorkflow.java",
    "purpose": "Demonstrate Agent Mode multi-file refactoring",
    "copilot_todos": 5,
    "difficulty": "advanced"
}

result = loop_agent.run(file_spec)

# Print iteration history
print("Iteration History:")
for i, iteration in enumerate(result['iterations'], 1):
    print(f"\nIteration {i}:")
    print(f"  Quality Score: {iteration['quality_score']}/10")
    print(f"  Errors: {len(iteration['errors'])}")
    if iteration['errors']:
        for error in iteration['errors']:
            print(f"    - {error}")
    print(f"  Status: {iteration['status']}")

print(f"\nFinal Code Quality: {result['final_quality_score']}/10")
```

### Output

```
Iteration History:

Iteration 1:
  Quality Score: 5/10
  Errors: 3
    - Missing import for ArrayList
    - TODO comments too vague
    - Method complexity too high (score: 18)
  Status: RETRY

Iteration 2:
  Quality Score: 7/10
  Errors: 1
    - One TODO still needs more context
  Status: RETRY

Iteration 3:
  Quality Score: 9/10
  Errors: 0
  Status: PASS

Final Code Quality: 9/10
```

---

## 🎯 PRZYKŁAD 6: Custom Configuration

### Scenariusz
Chcesz użyć custom konfiguracji dla specyficznych wymagań.

### Kod

```yaml
# config/custom_config.yaml
java_code_agent:
  model: gemini-2.5-pro  # Use pro instead of flash for higher quality
  temperature: 0.8  # More creative code
  max_tokens: 16384
  code_style:
    java_version: "21"  # Use latest Java
    use_lombok: true  # Enable Lombok
    max_line_length: 120

syntax_critic:
  quality_threshold: 8  # Higher quality bar (8/10 instead of 7/10)
  
orchestration:
  execution_phase:
    batch_size: 2  # Smaller batches for more control
    timeout_per_module_minutes: 60  # More time per module
```

```bash
# Run with custom config
python main.py \
    --training-plan opis_szkolenia_plan_copilot \
    --config config/custom_config.yaml \
    --output-dir ./output/custom_masterclass
```

---

## 🎯 PRZYKŁAD 7: Dry Run (Planning Only)

### Scenariusz
Chcesz tylko zobaczyć plan bez generowania plików.

### Kod

```bash
# Dry run - only planning phase
python main.py \
    --training-plan opis_szkolenia_plan_copilot \
    --dry-run \
    --output-dir ./output/dry_run

# Check planning results
cat ./output/dry_run/execution_plan.json | jq .
```

### Output

```json
{
  "modules": {
    "module1": {
      "name": "Komunikacja z AI i eksploracja kodu",
      "files_count": 7,
      "todos_count": 23,
      "estimated_duration_minutes": 90
    },
    ...
  },
  "execution_batches": [
    ["module1", "module2", "module3"],
    ["module4", "module5", "module6"],
    ["module7", "module8"]
  ],
  "total_files": 87,
  "total_todos": 245,
  "estimated_duration_hours": 16
}
```

---

**Więcej przykładów:** Zobacz `tests/` dla unit i integration tests


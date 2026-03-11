# 🛠️ Przewodnik Implementacji

**Jak zaimplementować i uruchomić system agentowy**

---

## 📋 PREREQUISITES

### 1. Instalacja Google ADK

```bash
# Zainstaluj Google ADK (Agent Development Kit)
pip install google-adk

# Lub z GitHub (jeśli nie ma w PyPI)
pip install git+https://github.com/google/adk.git
```

### 2. Konfiguracja API Keys

```bash
# Utwórz plik .env
cat > .env << EOF
GOOGLE_API_KEY=your_google_ai_studio_api_key
GOOGLE_SEARCH_API_KEY=your_google_custom_search_api_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
EOF

# Załaduj zmienne środowiskowe
export $(cat .env | xargs)
```

### 3. Instalacja zależności

```bash
cd workspace_generator
pip install -r requirements.txt
```

---

## 🚀 QUICK START

### Podstawowe użycie

```bash
# Generuj workspace dla planu szkolenia
python main.py \
    --training-plan ../opis_szkolenia_plan_copilot \
    --output-dir ./output/copilot_masterclass
```

### Zaawansowane opcje

```bash
# Z custom konfiguracją
python main.py \
    --training-plan ../opis_szkolenia_plan_copilot \
    --output-dir ./output/copilot_masterclass \
    --config config/custom_config.yaml \
    --verbose \
    --dry-run  # Tylko planning, bez execution
```

---

## 🔧 IMPLEMENTACJA KROK PO KROKU

### Krok 1: Implementacja Tools

#### File Operations Tool

```python
# tools/file_operations.py
from google.adk.tools import Tool
from pathlib import Path

class FileOperationsTool(Tool):
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        super().__init__(
            name="file_operations",
            description="Create directories and write files"
        )
    
    def create_directory(self, path: str) -> bool:
        """Create directory"""
        full_path = self.base_dir / path
        full_path.mkdir(parents=True, exist_ok=True)
        return True
    
    def write_file(self, path: str, content: str) -> bool:
        """Write file"""
        full_path = self.base_dir / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding='utf-8')
        return True
```

#### Code Validator Tool

```python
# tools/code_validator.py
from google.adk.tools import Tool
import javalang

class CodeValidatorTool(Tool):
    def __init__(self):
        super().__init__(
            name="code_validator",
            description="Validate Java code syntax"
        )
    
    def validate_java(self, code: str) -> dict:
        """Validate Java syntax"""
        try:
            tree = javalang.parse.parse(code)
            return {
                "valid": True,
                "errors": [],
                "warnings": []
            }
        except javalang.parser.JavaSyntaxError as e:
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": []
            }
```

---

### Krok 2: Implementacja Agentów

#### Planning Aggregator

```python
# agents/planning/planning_aggregator.py
from google.adk.agents import Agent
from google.adk.models import Gemini25Flash

class PlanningAggregator(Agent):
    """Łączy wyniki Research + Structure Planner"""
    
    SYSTEM_PROMPT = """
Jesteś aggregatorem wyników planowania.

Otrzymujesz:
1. Research results (dokumentacja, przykłady)
2. Module structures (pliki, TODO, zależności)

Zadanie:
Stwórz unified execution plan w JSON:
{
  "modules": {
    "module1": {
      "research": {...},
      "structure": {...},
      "execution_order": 1,
      "parallel_group": 1
    },
    ...
  },
  "execution_batches": [
    ["module1", "module2", "module3"],  # Batch 1 (parallel)
    ["module4", "module5", "module6"],  # Batch 2 (parallel)
    ["module7", "module8"]               # Batch 3 (parallel)
  ],
  "total_files": 87,
  "total_todos": 245,
  "estimated_duration_hours": 16
}
"""
    
    def __init__(self, model: Gemini25Flash, name: str = "PlanningAggregator"):
        super().__init__(
            model=model,
            system_prompt=self.SYSTEM_PROMPT,
            name=name
        )
    
    def aggregate(self, research_results: dict, structures: dict) -> dict:
        """Agreguje wyniki planowania"""
        prompt = f"""
Research Results: {research_results}
Module Structures: {structures}

Stwórz unified execution plan.
"""
        response = self.run(prompt)
        return self._parse_json(response)
```

---

### Krok 3: Implementacja Module Generator

```python
# agents/execution/module_generator.py
from google.adk.agents import SequentialAgent, LoopAgent
from google.adk.models import Gemini25Flash

class ModuleGenerator(SequentialAgent):
    """
    Generator dla pojedynczego modułu.
    
    Sequential flow:
    1. LoopAgent (Code Generation + Syntax Critic)
    2. Didactic Content Agent
    3. Test Generator
    4. Config Agent
    """
    
    def __init__(self, module_id: int, tools: dict):
        # Code generation loop
        code_loop = LoopAgent(
            agent=JavaCodeAgent(
                model=Gemini25Flash(),
                tools=[tools["code_validator"]],
                name=f"JavaCodeAgent_M{module_id}"
            ),
            critic=SyntaxCritic(
                model=Gemini25Flash(),
                name=f"SyntaxCritic_M{module_id}"
            ),
            max_iterations=3,
            name=f"CodeLoop_M{module_id}"
        )
        
        # Sequential agents
        agents = [
            code_loop,
            DidacticContentAgent(
                model=Gemini25Flash(),
                tools=[tools["file_operations"]],
                name=f"DidacticContent_M{module_id}"
            ),
            TestGenerator(
                model=Gemini25Flash(),
                tools=[tools["file_operations"], tools["code_validator"]],
                name=f"TestGenerator_M{module_id}"
            ),
            ConfigAgent(
                model=Gemini25Flash(),
                tools=[tools["file_operations"]],
                name=f"ConfigAgent_M{module_id}"
            )
        ]
        
        super().__init__(
            agents=agents,
            name=f"ModuleGenerator_{module_id}"
        )
```

---

### Krok 4: Uruchomienie Systemu

```python
# main.py (simplified example)
from workspace_generator import CopilotMasterclassWorkspaceGenerator

# Create generator
generator = CopilotMasterclassWorkspaceGenerator(
    training_plan_path="opis_szkolenia_plan_copilot",
    output_dir="./output"
)

# Generate workspace
result = generator.generate()

# Print results
print(f"Generated {len(result['generated_files'])} files")
print(f"Total TODOs: {result['total_todos']}")
print(f"Validation score: {result['validation_score']}/10")
```

---

## 📊 MONITORING I DEBUGGING

### Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('workspace_generation.log'),
        logging.StreamHandler()
    ]
)
```

### Progress Tracking

```python
from tqdm import tqdm

# W Module Generator
for module_id in tqdm(range(1, 9), desc="Generating modules"):
    module_generator = ModuleGenerator(module_id, tools)
    result = module_generator.run(state)
```

---

## 🧪 TESTING

### Unit Tests

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_agents.py::test_documentation_research_agent

# With coverage
pytest --cov=agents --cov-report=html
```

### Integration Tests

```bash
# Test full pipeline (dry-run)
python main.py --training-plan test_data/mini_plan.txt --dry-run
```

---

## 🐛 TROUBLESHOOTING

### Problem: API Rate Limits

**Rozwiązanie:**
```python
# Add retry logic with exponential backoff
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def call_gemini_api(prompt):
    return model.generate(prompt)
```

### Problem: JSON Parsing Errors

**Rozwiązanie:**
```python
# Add robust JSON extraction
import re
import json

def extract_json(response: str) -> dict:
    # Try direct parse
    try:
        return json.loads(response)
    except:
        # Extract JSON from markdown code blocks
        match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        raise ValueError("No valid JSON found")
```

---

**Następne kroki:** Zobacz `EXAMPLES.md` dla przykładów użycia


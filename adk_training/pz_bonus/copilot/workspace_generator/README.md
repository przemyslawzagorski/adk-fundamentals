# 🤖 GitHub Copilot Masterclass - Agentic Workspace Generator

**System wieloagentowy do automatycznego generowania workspace'ów szkoleniowych**

---

## 🎯 CEL SYSTEMU

System agentowy wykorzystujący **Google ADK (Agent Development Kit)** do automatycznego generowania kompletnych workspace'ów szkoleniowych na podstawie planu szkolenia GitHub Copilot Masterclass.

**To NIE jest generator workspace'a - to SYSTEM DO BUDOWANIA generatorów!**

---

## 🏗️ ARCHITEKTURA WIELOAGENTOWA

```
ORCHESTRATOR (Sequential)
│
├─▶ PLANNING PHASE (Sequential)
│   ├─▶ ParallelAgent:
│   │   ├─▶ Documentation Research Agent (Gemini 2.5-pro + Google Search)
│   │   └─▶ Module Structure Planner (Gemini 2.5-pro + thinking)
│   └─▶ Planning Aggregator
│
├─▶ EXECUTION PHASE (Sequential przez batche)
│   ├─▶ ParallelAgent (Moduły 1-3):
│   │   ├─▶ Module 1 Generator (Sequential):
│   │   │   ├─▶ LoopAgent (max 3 iteracje):
│   │   │   │   ├─▶ Java Code Agent (Gemini 2.5-flash)
│   │   │   │   ├─▶ Syntax Critic (Gemini 2.5-flash)
│   │   │   │   └─▶ Loop Controller
│   │   │   ├─▶ Didactic Content Agent (Gemini 2.5-flash)
│   │   │   ├─▶ Test Generator (Gemini 2.5-flash)
│   │   │   └─▶ Config Agent (Gemini 2.5-flash)
│   │   ├─▶ Module 2 Generator (analogicznie)
│   │   └─▶ Module 3 Generator
│   │
│   └─▶ ParallelAgent (Moduły 4-6):
│       ├─▶ Module 4 Generator
│       ├─▶ Module 5 Generator
│       └─▶ Module 6 Generator
│
└─▶ VALIDATION PHASE (Sequential)
    ├─▶ ParallelAgent:
    │   ├─▶ Coherence Validator (Gemini 2.5-pro + thinking, max 3 iter)
    │   └─▶ Pedagogical Reviewer (Gemini 2.5-pro + thinking)
    └─▶ Final Reporter (Gemini 2.5-flash)
```

---

## 📋 WYMAGANIA

### Techniczne
- Python 3.10+
- Google ADK (Agent Development Kit)
- Google AI Studio API Key
- Dostęp do Gemini 2.5-pro i 2.5-flash

### Wiedza
- Plan szkolenia GitHub Copilot Masterclass
- Dokumentacja GitHub Copilot 2026 (Agent Mode, MCP, Custom Agents)
- Znajomość Java/Python (języki docelowe workspace'a)

---

## 🚀 QUICK START

```bash
# 1. Instalacja zależności
pip install -r requirements.txt

# 2. Konfiguracja API
export GOOGLE_API_KEY="your-api-key"

# 3. Uruchomienie systemu
python main.py --training-plan ../opis_szkolenia_plan_copilot

# 4. Workspace zostanie wygenerowany w:
./output/copilot_masterclass_workspace/
```

---

## 📁 STRUKTURA PROJEKTU

```
workspace_generator/
├── README.md                    # Ten plik
├── main.py                      # Główny orchestrator
├── requirements.txt             # Zależności Python
│
├── agents/                      # Definicje agentów
│   ├── __init__.py
│   ├── planning/
│   │   ├── documentation_research_agent.py
│   │   ├── module_structure_planner.py
│   │   └── planning_aggregator.py
│   │
│   ├── execution/
│   │   ├── java_code_agent.py
│   │   ├── syntax_critic.py
│   │   ├── didactic_content_agent.py
│   │   ├── test_generator.py
│   │   └── config_agent.py
│   │
│   └── validation/
│       ├── coherence_validator.py
│       ├── pedagogical_reviewer.py
│       └── final_reporter.py
│
├── tools/                       # Narzędzia dla agentów
│   ├── __init__.py
│   ├── file_operations.py       # create_directory, write_file
│   ├── web_search.py            # Google Search integration
│   ├── code_validator.py        # Walidacja składni Java/Python
│   └── github_copilot_docs.py   # Scraping dokumentacji Copilot
│
├── orchestration/               # Orkiestracja przepływu
│   ├── __init__.py
│   ├── sequential_flow.py
│   ├── parallel_flow.py
│   └── loop_flow.py
│
├── config/                      # Konfiguracja
│   ├── agents_config.yaml       # Konfiguracja agentów
│   ├── models_config.yaml       # Konfiguracja modeli AI
│   └── workspace_templates.yaml # Szablony workspace'ów
│
├── prompts/                     # Prompty dla agentów
│   ├── planning_prompts.py
│   ├── execution_prompts.py
│   └── validation_prompts.py
│
└── tests/                       # Testy systemu
    ├── test_agents.py
    ├── test_tools.py
    └── test_orchestration.py
```

---

## 🎓 FILOZOFIA SYSTEMU

### 1. **Masterclass ≠ Code Completion**
System NIE generuje prostych przykładów typu "hello world". 
Generuje **zaawansowane scenariusze** zgodne z planem Masterclass:
- Agent Mode workflows
- Multi-file refactoring
- MCP server integration
- Custom Agents development

### 2. **Research-Driven Generation**
Każdy moduł jest poprzedzony **research phase**:
- Documentation Research Agent szuka najnowszych przykładów (marzec 2026)
- Analizuje GitHub Copilot docs, blog posts, GitHub Skills
- Identyfikuje best practices i anti-patterns

### 3. **Iterative Quality Control**
- LoopAgent (max 3 iteracje) dla każdego pliku kodu
- Syntax Critic weryfikuje poprawność
- Coherence Validator sprawdza spójność między modułami
- Pedagogical Reviewer ocenia wartość dydaktyczną

---

## 🔧 KLUCZOWE KOMPONENTY

### Planning Phase
**Cel:** Analiza planu szkolenia i stworzenie struktury workspace'a

**Agenty:**
1. **Documentation Research Agent**
   - Model: Gemini 2.5-pro + Google Search
   - Zadanie: Szuka najnowszych przykładów dla każdego modułu
   - Output: JSON z linkami do dokumentacji i przykładów

2. **Module Structure Planner**
   - Model: Gemini 2.5-pro + thinking mode
   - Zadanie: Projektuje strukturę plików dla każdego modułu
   - Output: JSON z hierarchią plików i zależnościami

### Execution Phase
**Cel:** Generowanie kodu i materiałów szkoleniowych

**Agenty (dla każdego modułu):**
1. **Java Code Agent** - generuje kod z TODO dla Copilot
2. **Syntax Critic** - weryfikuje poprawność składni
3. **Didactic Content Agent** - tworzy README i instrukcje
4. **Test Generator** - generuje testy jednostkowe
5. **Config Agent** - tworzy pliki konfiguracyjne (.copilot, MCP)

### Validation Phase
**Cel:** Zapewnienie jakości i spójności

**Agenty:**
1. **Coherence Validator** - sprawdza spójność między modułami
2. **Pedagogical Reviewer** - ocenia wartość dydaktyczną
3. **Final Reporter** - generuje raport z metrykami

---

## 📊 METRYKI SUKCESU

System generuje raport zawierający:
- ✅ Liczba wygenerowanych plików
- ✅ Pokrycie tematów z planu szkolenia
- ✅ Liczba TODO dla Copilot
- ✅ Wynik walidacji składni (0 błędów)
- ✅ Ocena pedagogiczna (1-10)
- ✅ Czas generowania

---

**Następne kroki:** Przejdź do `docs/ARCHITECTURE.md` dla szczegółów implementacji


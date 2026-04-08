# 📝 CHANGELOG - Workspace Generator

## v1.6.0 (2026-03-11) - Izolacja Sesji + Bugfixy

### 🔧 Naprawa Tool Calling (KRYTYCZNA!):
- **Problem:** Model generował kod w tekście zamiast wywoływać `create_file`
- **Przyczyna:** Sprzeczne instrukcje: "wywołaj create_file" ORAZ "ZWRÓĆ TYLKO KOD"
- **Rozwiązanie:**
  - Usunięto wymóg zwracania kodu w tekście
  - Dodano wyraźną instrukcję: "POD ŻADNYM POZOREM NIE WKLEJAJ KODU DO CZATU"
  - Agent ma zwracać TYLKO krótkie podsumowanie (lista plików)
  - Cały kod idzie przez narzędzie `create_file`

### ✅ Załatanie LoopController (ZAIMPLEMENTOWANE!):
- **Problem:** LoopController przepuszczał iterację mimo że pliki nie powstały
- **Rozwiązanie:**
  - Sprawdzanie faktycznie utworzonych plików na dysku
  - Blokowanie iteracji jeśli `files_created == 0`
  - Dodanie feedback do stanu: "KRYTYCZNY BŁĄD: Nie użyłeś narzędzia create_file!"

### ✅ Ożywienie YAML Config (ZAIMPLEMENTOWANE!):
- **Problem:** `agents_config.yaml` był ignorowany
- **Rozwiązanie:**
  - Wczytywanie YAML w `__init__` (PyYAML)
  - Przekazywanie `config` do wszystkich agentów
  - Używanie `temperature` z config:
    - PolyglotCodeAgent: 0.7 (default, kreatywność)
    - TrainingValueCritic: 0.3 (default, deterministyczność)

### ✅ Izolacja Sesji + Shared Context (ZAIMPLEMENTOWANE!):
- **Problem:** Zanik pamięci po 3-4 modułach (jedna sesja dla wszystkich)
- **Rozwiązanie - Hybrydowa architektura:**
  - **Faza 1: Planning** (jedna sesja) → `execution_plan.json`
  - **Faza 2: Execution** (osobna sesja dla KAŻDEGO modułu)
    - Każdy moduł dostaje CZYSTĄ sesję (brak zanikania pamięci)
    - Przekazywanie `previous_modules_summary` w state (unikanie duplikacji)
    - Przekazywanie `project_guidelines` (spójność)
    - Przekazywanie `current_module` (kontekst)
  - **Faza 3: Validation** (jedna sesja)
- **Korzyści:**
  - ✅ Czysty umysł dla każdego modułu (zawsze pamięta o `create_file`)
  - ✅ Unikanie duplikacji klas (widzi poprzednie moduły w summary)
  - ✅ Spójność (jednolite standardy z `project_guidelines`)
  - ✅ Różnorodność (każdy moduł w innej domenie)
- **State przekazywany do każdej sesji:**
  ```python
  {
    "module_id": 3,
    "execution_plan": {...},  # Pełny plan
    "training_plan": "...",
    "funkcje_plan": "...",
    "previous_modules_summary": [  # KLUCZOWE!
      {"module_id": 1, "domain": "E-commerce", "classes": ["Treasure", "Pirate"]},
      {"module_id": 2, "domain": "Banking", "classes": ["Account", "Transaction"]}
    ],
    "project_guidelines": {  # Spójność
      "java_version": "17",
      "spring_boot_version": "3.2.0",
      ...
    },
    "current_module": {  # Kontekst obecnego modułu
      "domain": "Healthcare",
      "copilot_features": ["Edit Mode", "Working Set"],
      ...
    }
  }
  ```

### 🐛 Bugfixy (KRYTYCZNE!):
1. **Typ narzędzi (Dict → List):**
   - Problem: `self._initialize_tools()` zwraca Dict, ADK wymaga List
   - Rozwiązanie: `exec_tools = list(exec_tools_dict.values())`

2. **State Injection (current_module.domain):**
   - Problem: `{{{{current_module.domain}}}}` nie działa (Dict nie ma atrybutu .domain)
   - Rozwiązanie: Wyciągnięcie do osobnego pola `current_module_domain` w state

3. **Zahardkodowana ścieżka ./output:**
   - Problem: LoopController zawsze szukał w `./output`, ignorując `--output-dir`
   - Rozwiązanie: Przekazywanie `output_dir` w state, używanie w LoopController

4. **Zmartwychwstanie Monolitu:**
   - Problem: `_run_planning_phase()` budowała cały orchestrator (8 modułów!)
   - Rozwiązanie: Bezpośrednie budowanie PlanningPhase bez orchestratora

---

## v1.5.1 (2026-03-11) - Różnorodność domen

### 🎯 Naprawa duplikacji klas:
- **Problem:** Moduły 4, 5, 6 generowały te same klasy (InsurancePolicy, InsurancePolicyService, InsurancePolicyRepository)
- **Przyczyna:** Brak wyraźnej instrukcji o różnorodności domen w prompcie
- **Rozwiązanie:**
  - Dodano mapowanie domen do modułów w `PolyglotCodeAgent`:
    - Moduł 1: E-commerce / Pirate Treasure Shop
    - Moduł 2: Banking / Financial Services
    - Moduł 3: Healthcare / Medical Records
    - Moduł 4: Logistics / Shipping & Delivery
    - Moduł 5: HR / Employee Management
    - Moduł 6: Real Estate / Property Management
    - Moduł 7: Education / Online Learning Platform
    - Moduł 8: Social Media / Content Platform
  - Dodano czerwoną flagę w `TrainingValueCritic`: "Używa tych samych klas co poprzednie moduły"
  - Wyraźna instrukcja: "NIE używaj klas z poprzednich modułów! Każdy moduł to NOWY projekt!"

### 🔧 Zmiany techniczne:
- `module_generator.py`: Dodano sekcję "RÓŻNORODNOŚĆ DOMEN" z mapowaniem
- `training_value_critic.py`: Dodano czerwone flagi dla duplikacji klas i braku różnorodności

---

## v1.5.0 (2026-03-11) - Training Value Critic + Plan Funkcyjny

### 🎓 Nowy system szkoleniowy:
- **TrainingValueCritic:** Nowy krytyk z wysokim common sense
  - Sprawdza czy ćwiczenie uczy konkretnej funkcji Copilota
  - Wykrywa przykładowe odpowiedzi (czerwona flaga!)
  - Sprawdza dublowanie z innymi ćwiczeniami
  - Ocenia wartość praktyczną i poziom trudności
  - Score 1.0-10.0 (8.0+ = approved)
- **Plan funkcyjny:** `funkcje_copilot_plan.md`
  - Mapowanie funkcji Copilota do 8 modułów
  - Inline, Chat, Agent Mode, @workspace, Edit Mode, @test, MCP, Custom Agents
  - Moduły dodatkowe: CLI, DevOps, Dokumentacja, Advanced
- **Zasady generowania:**
  - Nie generujemy przykładowych odpowiedzi
  - Konkretne zadania ("Użyj @workspace do...")
  - Małe przykłady (focus na funkcji)
  - Wartość szkoleniowa (każde ćwiczenie uczy)

### 🔧 Zmiany techniczne:
- `module_generator.py`: TrainingValueCritic zamiast SyntaxCritic
- `LoopController`: Sprawdza `training_critique` zamiast `critique`
- `track_iteration`: Inicjalizuje `training_critique` w stanie
- `main.py`: Ładuje OBA plany (`training_plan` + `funkcje_plan`) i przekazuje do state
- `documentation_research_agent.py`: Wyszukuje dokumentację dla WSZYSTKICH funkcji z planu funkcyjnego
- `module_structure_planner.py`: Projektuje pliki tak, żeby każdy uczył konkretnej funkcji

---

## v1.4.3 (2026-03-11) - Rozdzielenie Research od Formatowania

### ✅ Zmiany:
- **Rozdzielenie odpowiedzialności:**
  - `DocumentationResearch`: google_search → **Markdown text** (BEZ output_schema)
  - `ModuleStructurePlanner`: czyta text → **structured JSON** (Z output_schema)
- **Powód:** Vertex AI nie wspiera `output_schema` + `google_search` jednocześnie
- **Skutek:** Eleganckie rozwiązanie - jeden agent "gada" z narzędziami, drugi "sprząta" do struktury
- **Format:** Research zwraca wyczerpujący raport Markdown z sekcjami (Dokumentacja, Przykłady, Best Practices, Anti-patterns, Koncepty)

---

## v1.4.2 (2026-03-11) - Natywny Google Search

### ✅ Zmiany:
- **Natywny google_search:** Użycie `google.adk.tools.google_search` zamiast `googlesearch-python`
- **Stabilność:** Wbudowany w ADK, lepsze zarządzanie rate limiting
- **Usunięto:** `tools/web_search.py` (nie jest już potrzebny)
- **Zmiana:** `documentation_research_agent.py` używa `tools=[google_search]`

---

## v1.4.1 (2026-03-11) - Krytyczna naprawa Module ID

### ❌ NAPRAWIONO:
- **Zanik pamięci operacyjnej:** Wszystkie 8 agentów generowały Moduł 1
- **Przyczyna:** Brak `module_id` w prompcie PolyglotCodeAgent
- **Rozwiązanie:**
  - Przekazanie `module_id` do `create_polyglot_code_agent(module_id=...)`
  - Prompt: "Jesteś programistą realizującym MODUŁ NR {module_id}"
  - Unikalna nazwa agenta: `PolyglotCodeAgent_M{module_id}`
  - Wymuszenie iteracji: "Musisz wywołać 'create_file' TYLE RAZY, ILE PLIKÓW"
- **Skutek:** Każdy agent generuje swój moduł (1-8), nie nadpisuje Modułu 1

---

## v1.4.0 (2026-03-11) - Optymalizacje inżynierskie

### 🔧 Zmiany:
- **Sequential Planning:** ParallelAgent → SequentialAgent w Planning Phase
  - Kolejność: Research → Structure → Aggregator
  - Zmniejszone ryzyko 429 errors (nie sumujemy RPM)
- **Throttling w web_search:** `await asyncio.sleep(2)` przed każdym zapytaniem
  - Unika 429 z Google Search
  - Logging: "🔍 Web search (throttled): {query}"

---

## v1.3.1 (2026-03-11) - Write-Verify-Commit

### ✅ Zmiany:
- **PolyglotCodeAgent:** Otrzymuje `tools` (create_file, validate_java_code, count_todo_comments)
- **Automatyczny zapis:** Agent sam wywołuje `create_file` po wygenerowaniu kodu
- **Nadpisywanie:** Każda iteracja LoopAgent nadpisuje plik - na dysku zawsze najnowsza wersja
- **Widoczność:** Pliki pojawiają się w `output/` na bieżąco

---

## v1.3.0 (2026-03-11) - Polyglot Support + Streaming Logs

### 🚀 Nowe funkcje:

#### Polyglot Support (Java/Python/React)
- **FileType:** Dodano `REACT_COMPONENT` dla modułu 8
- **FileSpec:** Zmieniono `class_name` → `file_name` (uniwersalne)
- **PolyglotCodeAgent:** Generuje kod w Java/Python/React zależnie od `file_type`
- **SyntaxCritic:** Waliduje składnię dla wszystkich języków
- **code_validator:** Bypass dla non-Java (`.py`, `.tsx`)

#### Streaming Logs (Real-time visibility)
- **ANSI Colors:** Niebieski dla nagłówków agentów, żółty dla tool calls
- **event.author:** Wykrywanie zmiany agenta
- **Streaming text:** `print(part.text, end="", flush=True)`
- **Tool calls:** Logowanie użycia narzędzi

#### Dobór języka (automatyczny)
- **Moduły 1-6:** Java 17+, Spring Boot 3.x, JUnit 5
- **Moduł 7:** Python 3.10+, typing, pytest
- **Moduł 8:** React, TypeScript (.tsx), Functional Components

---

## v1.2.0 (2026-03-11) - Naprawy krytyczne

### 🔧 Naprawy:
- **Usunięto:** Katastrofalny retry na Runnerze (restartował cały proces przy 429)
- **Usunięto:** Błędny Request Counter (zliczał chunki zamiast requestów)
- **Dodano:** Throttling między modułami (`THROTTLE_DELAY_SECONDS=3`)
- **Naprawiono:** Sygnatury funkcji (`planner=None, **kwargs`)

---

## v1.1.0 (2026-03-11) - Exponential Backoff (WYCOFANE)

### ❌ Wycofane funkcje:
- Retry logic z tenacity (powodował nieskończone pętle)
- Request counter w eventach (błędne statystyki)

---

## v1.0.0 (2026-03-11) - Initial Release

### ✅ Funkcje:
- Multi-agent architecture (Planning, Execution, Validation)
- LoopAgent dla self-correction (Writer → Critic → Controller)
- 11 agentów (Research, Structure, Aggregator, 8× ModuleGenerator, Validators)
- 8 narzędzi (web_search, file_operations, code_validator)
- Google ADK 1.18.0
- Vertex AI (Gemini 2.5 Pro + Flash)

---

## 📊 Statystyki:

- **Pliki:** 20+ plików Python
- **Agenty:** 11 agentów ADK
- **Narzędzia:** 8 funkcji
- **Modele:** Gemini 2.5 Pro (Planning), Gemini 2.5 Flash (Execution)
- **Języki:** Java, Python, React/TypeScript
- **Moduły:** 8 modułów szkoleniowych

---

## 🎯 Następne kroki:

- [ ] Testy integracyjne
- [ ] Dokumentacja API
- [ ] Przykładowe workspace'y
- [ ] CI/CD pipeline
- [ ] Docker container


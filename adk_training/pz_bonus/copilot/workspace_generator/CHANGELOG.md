# 📝 CHANGELOG - Workspace Generator

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


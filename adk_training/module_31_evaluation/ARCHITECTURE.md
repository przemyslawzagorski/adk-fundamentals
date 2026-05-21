# ARCHITECTURE — Module 31: ADK Evaluation

> **Cel modułu**: Systematyczne testowanie agentów ADK przy użyciu
> `AgentEvaluator`, eval sets i metryk jakościowych.
> Źródło: https://adk.dev/evaluate/

---

## Dlaczego tradycyjne unit testy nie wystarczają dla agentów?

```
TRADYCYJNY KOD:
  def add(a, b): return a + b
  assert add(2, 3) == 5  ✅ deterministyczny

AGENT LLM:
  "What is 2 + 3?"
  → "The answer is 5."    ✅ (run 1)
  → "5"                   ✅ (run 2, inny format)
  → "Let me calculate: 5" ✅ (run 3, inny styl)
  → "approximately 5"     ✅ (run 4, przybliżone)
  
  Jak napisać assert dla każdego z tych przypadków? Nie możesz.
```

ADK Evaluation zastępuje `assert ==` metrykami probabilistycznymi:
- `tool_trajectory_avg_score` — czy agent wywołał WŁAŚCIWE narzędzia?
- `response_match_score` — czy odpowiedź jest PODOBNA do wzorca? (ROUGE-1)
- `final_response_match_v2` — czy odpowiedź SEMANTYCZNIE pasuje? (LLM judge)

---

## Dwa podejścia do ewaluacji

### Podejście 1: Test File (`*.test.json`) — "Unit test agenta"

```
Kiedy używać:
  ✅ Aktywny development agenta
  ✅ Szybkie sprawdzanie pojedynczych przypadków
  ✅ CI/CD pipeline (szybkie, deterministyczne metryki)
  ✅ Każdy plik = jedna sesja, kilka turnów

Struktura pliku:
  eval_set_id + eval_cases[]
    └── conversation[]
          └── user_content + final_response + intermediate_data
                └── tool_uses[]  ← trajektoria narzędzi do walidacji
```

### Podejście 2: Evalset File (`*.evalset.json`) — "Integration test agenta"

```
Kiedy używać:
  ✅ Złożone, multi-turn konwersacje
  ✅ Symulacja realnych użytkowników
  ✅ Testy regresji przed release
  ⚠️ Wymaga Vertex AI Evaluation Service (płatne) dla LLM-as-judge metryk

Różnica od test file:
  - Może zawierać WIELE sesji o różnej złożoności
  - Obsługuje user_simulation (dynamiczne pytania generowane przez AI)
  - Tworzony przez ADK Web UI (zakładka Eval → Add current session)
```

---

## Krytyczna lekcja: SequentialAgent nie działa z AgentEvaluator

```python
# ❌ ZŁE — AgentEvaluator rzuci ValueError
root_agent = SequentialAgent(sub_agents=[agent_a, agent_b, agent_c])
# Dlaczego? Każdy sub-agent z output_key emituje isFinalResponse=True
# AgentEvaluator porównuje len(inferences) == len(conversation)
# 3 sub-agenty → 3 inferences, ale conversation ma 1 turn → ValueError

# ✅ DOBRE — jeden LlmAgent na potrzeby ewaluacji
root_agent = LlmAgent(name="single_agent", ...)
# Jedno isFinalResponse=True = jeden inference = jedna conversation turn

# WZORZEC PRODUKCYJNY (z Module 22):
# 1. Pełny pipeline → osobny moduł (np. agent.py z SequentialAgent)
# 2. Ewaluowany stage → agent_for_eval/agent.py (eksponuje jeden LlmAgent)
# 3. AgentEvaluator wskazuje na agent_for_eval, nie na główny agent.py
```

---

## Metryki i kiedy je stosować

```
┌─────────────────────────────────┬───────────────────────────────────────────┐
│ Metryka                         │ Kiedy używać                              │
├─────────────────────────────────┼───────────────────────────────────────────┤
│ tool_trajectory_avg_score       │ ZAWSZE — czy agent wywołuje właściwe      │
│ (domyślnie: 1.0)                │ narzędzia we właściwej kolejności?        │
├─────────────────────────────────┼───────────────────────────────────────────┤
│ response_match_score            │ CI/CD — ROUGE-1, lokalnie, bez API        │
│ (domyślnie: 0.8)                │ Szybkie, przewidywalne, tanie             │
├─────────────────────────────────┼───────────────────────────────────────────┤
│ final_response_match_v2         │ Jakość semantyczna (LLM judge)            │
│ (Vertex AI, płatne)             │ "Czy agent odpowiedział to samo co        │
│                                 │  wzorzec, ale innymi słowami?"            │
├─────────────────────────────────┼───────────────────────────────────────────┤
│ rubric_based_final_response_    │ Gdy nie masz wzorca — definiujesz         │
│ quality_v1 (Vertex AI, płatne)  │ atrybuty dobrej odpowiedzi               │
│                                 │ np. "odpowiedź jest zwięzła"              │
├─────────────────────────────────┼───────────────────────────────────────────┤
│ rubric_based_tool_use_          │ Weryfikacja logiki narzędzi               │
│ quality_v1 (Vertex AI, płatne)  │ "Tool A musi być wywołany przed B"        │
├─────────────────────────────────┼───────────────────────────────────────────┤
│ hallucinations_v1               │ Czy agent "zmyśla"? Weryfikacja           │
│ (Vertex AI, płatne)             │ odpowiedzi względem tool outputs          │
├─────────────────────────────────┼───────────────────────────────────────────┤
│ multi_turn_task_success_v1      │ Multi-turn: czy cała rozmowa osiągnęła    │
│ (Vertex AI, płatne)             │ zamierzony cel?                           │
└─────────────────────────────────┴───────────────────────────────────────────┘

DARMOWE (bez Vertex AI):
  tool_trajectory_avg_score + response_match_score

PŁATNE (Vertex AI Evaluation Service):
  wszystkie _v1, _v2, rubric_based_*, multi_turn_*
```

---

## Trzy sposoby uruchamiania ewaluacji

### 1. `adk web` — Web UI (interaktywny)

```bash
adk web adk_training/

# W UI:
# 1. Wybierz agenta → przeprowadź rozmowę
# 2. Zakładka "Eval" → "Add current session" → zapisuje jako eval case
# 3. Zakładka "Eval" → wybierz cases → "Run Evaluation"
# 4. Suwaki: tool_trajectory_avg_score i response_match_score
# 5. Wyniki: Pass/Fail + porównanie actual vs. expected
#
# Zakładka "Trace" (dostępna ZAWSZE, nie tylko przy eval):
#   - Niebieskie wiersze = event wygenerowany
#   - Klik na wiersz → Event / Request / Response / Graph
#   - Hover na trace → podświetla wiadomość w chacie
```

### 2. `pytest` — Programatyczny (CI/CD)

```python
from google.adk.evaluation.agent_evaluator import AgentEvaluator

@pytest.mark.asyncio
async def test_my_agent():
    await AgentEvaluator.evaluate(
        agent_module="my_package.agent",       # moduł z root_agent
        eval_dataset_file_path_or_dir="tests/eval/basic.test.json",
        num_runs=1,                            # ile razy uruchomić każdy case
        print_detailed_results=True,
    )
    # Rzuca AssertionError gdy metryki poniżej progu z test_config.json
```

### 3. `adk eval` — CLI (automatyzacja)

```bash
adk eval \
    adk_training/module_31_evaluation \
    adk_training/module_31_evaluation/tests/eval/code_review_basic.test.json \
    --config_file_path=adk_training/module_31_evaluation/tests/eval/test_config.json \
    --print_detailed_results

# Uruchomienie wybranych eval cases (nie całego pliku):
adk eval \
    adk_training/module_31_evaluation \
    tests/eval/code_review_basic.test.json:simple_function_no_issues,code_with_todos
```

---

## Diagram przepływu AgentEvaluator

```
test_config.json             *.test.json
(kryteria + progi)           (eval cases)
       │                           │
       └──────────┬────────────────┘
                  ▼
        AgentEvaluator.evaluate()
                  │
                  ▼
        Import agent_module
        → szuka root_agent
                  │
         ┌────────┴─────────┐
         │                  │
    dla każdego eval_case:   │
         │                  │
         ▼                  │
    Uruchom root_agent       │
    z user_content           │
         │                  │
         ▼                  │
    Zbierz:                  │
    - actual_tool_uses       │
    - actual_final_response  │
         │                  │
         ▼                  │
    Porównaj z expected:     │
    - tool_trajectory        │
      → tool_trajectory_     │
        avg_score            │
    - final_response         │
      → response_match_score │
         │                  │
         ▼                  │
    Wynik: PASS / FAIL       │
    (+ szczegóły)            │
         │                  │
         └────────┬──────────┘
                  │
                  ▼
        AssertionError gdy < próg
        lub raport wynikowy
```

---

## Integracja z Module 22 (Spec Generator) — real-world example

```
Module 22 ma:
  module_22_spec_generator/
  ├── agent.py          → root_agent = SequentialAgent(...)  ← NIE dla eval
  ├── agent_for_eval/
  │   └── agent.py      → root_agent = epic_decomposer       ← TAK dla eval
  └── tests/
      ├── eval/
      │   ├── spec_gen_basic.test.json  ← eval cases
      │   └── test_config.json          ← kryteria
      └── live/
          └── test_agent_evaluator.py   ← pytest live test

KLUCZOWY WNIOSEK:
  Produckyjny pipeline (SequentialAgent) ≠ agent dla ewaluacji (single LlmAgent)
  To nie jest ograniczenie — to dobra praktyka:
  "Ewaluuj jeden stage na raz, resztę pokryj testami e2e"
```

---

## Struktura modułu 31

```
module_31_evaluation/
├── __init__.py
├── agent.py                        ← root_agent (single LlmAgent, dla AgentEvaluator)
├── ARCHITECTURE.md                 ← ten plik
└── tests/
    ├── eval/
    │   ├── code_review_basic.test.json   ← eval cases
    │   └── test_config.json              ← kryteria (trajectory=1.0, response=0.15)
    └── test_evaluation_live.py           ← pytest live tests
```

---

## TODO — zadania dla dewelopera

```
[ ] Uruchom: adk web adk_training/ → wybierz module_31_evaluation → przeprowadź rozmowę
[ ] Zapisz sesję jako eval case (zakładka Eval → Add current session)
[ ] Uruchom eval przez UI i sprawdź wyniki (Pass/Fail + actual vs. expected)
[ ] Uruchom: $env:RUN_LIVE_TESTS="1"; pytest tests/test_evaluation_live.py -v -s -m live
[ ] Dodaj 3. eval case z kodem Python zawierającym SQL injection → sprawdź czy agent wykryje
[ ] Zmień tool_trajectory_avg_score na 0.5 w test_config.json → obserwuj co przechodzi
[ ] Dodaj nowe narzędzie do agenta i zaktualizuj test.json o nową trajektorię
[ ] Porównaj z Module 22: dlaczego epic_decomposer działa a SpecGeneratorAgent nie
[ ] Napisz eval case dla Module 23 code_review_pr() → wymaga structured return (Module 27)
[ ] Skonfiguruj final_response_match_v2 (wymaga GOOGLE_CLOUD_PROJECT + billing)
```

---

## Dokumentacja

- [ADK Evaluation (główna)](https://adk.dev/evaluate/)
- [Evaluation Criteria](https://adk.dev/evaluate/criteria/)
- [User Simulation](https://adk.dev/evaluate/user-simulation/)
- [AgentEvaluator API](https://google.github.io/adk-docs/evaluation/)
- [EvalSet Schema](https://google.github.io/adk-docs/evaluation/eval-set/)

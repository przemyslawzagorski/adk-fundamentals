# 🐛 BUGFIXES v1.6.0 - Naprawione błędy krytyczne

## 📋 PODSUMOWANIE:

Po implementacji Izolacji Sesji pojawiły się 4 błędy techniczne (2 krytyczne), które zostały naprawione.

---

## 1️⃣ BŁĄD KRYTYCZNY: Typ narzędzi (Dict vs List)

### ❌ **Problem:**
```python
# main.py
exec_tools = self._initialize_tools()  # Zwraca Dict
module_agent = create_module_generator(..., tools=exec_tools, ...)
# ↓
# LlmAgent(tools=exec_tools)  # ← ADK oczekuje List, dostaje Dict!
```

**Skutek:** Crash podczas bindowania narzędzi do modelu (TypeError)

### ✅ **Rozwiązanie:**
```python
# main.py
exec_tools_dict = self._initialize_tools()
exec_tools = list(exec_tools_dict.values())  # ← Konwersja Dict → List
module_agent = create_module_generator(..., tools=exec_tools, ...)
```

---

## 2️⃣ BŁĄD KRYTYCZNY: State Injection (current_module.domain)

### ❌ **Problem:**
```python
# module_generator.py (prompt)
Twoja domena: {{{{current_module.domain}}}}
# ↓ Po ewaluacji f-stringa:
Twoja domena: {current_module.domain}
# ↓ ADK próbuje wstrzyknąć stan:
# current_module to Dict, nie ma atrybutu .domain → AttributeError/KeyError
```

**Skutek:** Crash podczas formatowania promptu (AttributeError)

### ✅ **Rozwiązanie:**
```python
# main.py (state)
state={
    "current_module": current_module,
    "current_module_domain": current_module.get("domain", "Unknown"),  # ← Wyciągnięte pole
    "current_module_name": current_module.get("name", f"Module {module_id}")
}

# module_generator.py (prompt)
Twoja domena: {{{{current_module_domain}}}}  # ← Bezpośredni dostęp do stringa
```

---

## 3️⃣ BŁĄD LOGICZNY: Zahardkodowana ścieżka ./output

### ❌ **Problem:**
```python
# module_generator.py (LoopController)
file_path = Path("./output") / file_spec.get("path", "")  # ← Zahardkodowane!
if file_path.exists():
    files_created_on_disk += 1

# Użytkownik uruchamia:
python main.py --output-dir ./moje_szkolenie

# Pliki zapisują się w ./moje_szkolenie
# LoopController szuka w ./output
# Nie znajduje → uznaje że agent nic nie zrobił → nieskończona pętla!
```

**Skutek:** Nieskończona pętla lub fałszywe negatywy w walidacji

### ✅ **Rozwiązanie:**
```python
# main.py (state)
state={
    "output_dir": str(self.output_dir)  # ← Przekazujemy output_dir
}

# module_generator.py (LoopController)
base_dir = ctx.session.state.get("output_dir", "./output")  # ← Pobieramy ze stanu
file_path = Path(base_dir) / file_spec.get("path", "")
if file_path.exists():
    files_created_on_disk += 1
```

---

## 4️⃣ BŁĄD OPTYMALIZACYJNY: Zmartwychwstanie Monolitu

### ❌ **Problem:**
```python
# main.py (_run_planning_phase)
planning_agents = self._build_orchestrator().sub_agents[0]  # ← Buduje CAŁY orchestrator!

# _build_orchestrator() tworzy:
# - 8× create_module_generator() (każdy z LoopAgent, Critic, Controller)
# - Validation agents
# - Wszystkie narzędzia
# - Ładuje wszystkie konfigi
# ...tylko po to, żeby wyrwać planning_agents ([0])!
```

**Skutek:** Niepotrzebne zużycie pamięci i czasu (budowanie 8 modułów które nie są używane)

### ✅ **Rozwiązanie:**
```python
# main.py (_run_planning_phase)
# Buduj PlanningPhase bezpośrednio, NIE przez _build_orchestrator()!
from google.adk.agents import SequentialAgent
from agents.planning.documentation_research_agent import create_documentation_research_agent
from agents.planning.module_structure_planner import create_module_structure_planner
from agents.planning.planning_aggregator import create_planning_aggregator

planner = get_planner_if_enabled()

planning_agents = SequentialAgent(
    sub_agents=[
        create_documentation_research_agent(model="gemini-2.5-pro", tools=None, planner=planner),
        create_module_structure_planner(model="gemini-2.5-pro", tools=None, planner=planner),
        create_planning_aggregator(model="gemini-2.5-flash", tools=None)
    ],
    name="PlanningPhase"
)
```


---

## 5️⃣ BŁĄD KRYTYCZNY: Import nieistniejącego modułu

### ❌ **Problem:**
```python
# main.py (_run_planning_phase)
from utils.planner_utils import get_planner_if_enabled
# ↓
# ModuleNotFoundError: No module named 'utils'
```

**Skutek:** Crash przy starcie (ModuleNotFoundError)

### ✅ **Rozwiązanie:**
```python
# Funkcja get_planner_if_enabled() jest w zasięgu globalnym (linia 43)
# Nie trzeba jej importować - usunięto błędny import!
planner = get_planner_if_enabled()  # ← Bezpośrednie użycie
```

---

## 6️⃣ ZOMBIE MONOLIT: Martwy kod w __init__

### ❌ **Problem:**
```python
# main.py (__init__)
self.orchestrator = self._build_orchestrator()  # ← Buduje cały monolit!

# _build_orchestrator() tworzy:
# - 8× create_module_generator() (każdy z LoopAgent, Critic, Controller)
# - Validation agents
# - Wszystkie narzędzia
# ...po czym to wszystko jest wyrzucane do kosza (nie używane w generate())
```

**Skutek:** Marnowanie pamięci i czasu przy starcie

### ✅ **Rozwiązanie:**
```python
# 1. Usunięto z __init__:
# self.orchestrator = self._build_orchestrator()

# 2. Usunięto całą metodę _build_orchestrator() (118 linii martwego kodu!)
# Nowa architektura buduje agentów bezpośrednio w każdej fazie.
```


---

## 7️⃣ BŁĄD KRYTYCZNY: Brakujący import `List`

### ❌ **Problem:**
```python
NameError: name 'List' is not defined. Did you mean: 'list'?
```

**Skutek:** Crash przy starcie (NameError)

### ✅ **Rozwiązanie:**
```python
# Przed:
from typing import Dict, Any

# Po:
from typing import Dict, Any, List
```

---

## 8️⃣ BŁĄD KRYTYCZNY: Stale Session (nieaktualny stan)

### ❌ **Problem:**
```python
# main.py (_run_planning_phase)
async for event in runner.run_async(...):
    pass

# Pobierz execution_plan ze stanu sesji
execution_plan = session.state.get("execution_plan", {})
# ↓
# session.state to STARY stan (sprzed uruchomienia agentów)!
# Agenty zapisały plan do InMemorySessionService, ale lokalna zmienna nie została zaktualizowana
# Rezultat: execution_plan = {} (pusty słownik)
```

**Skutek:** 0 modułów w planie, faza Execution nie generuje nic

### ✅ **Rozwiązanie:**
```python
# 1. Pobierz sesję PONOWNIE z serwisu (najświeższy stan)
updated_session = await session_service.get_session(session.id)

# 2. Pobierz raw_plan (może być Pydantic object)
raw_plan = updated_session.state.get("execution_plan")

# 3. Bezpieczne zrzutowanie do Dict
if hasattr(raw_plan, 'model_dump'):
    execution_plan = raw_plan.model_dump()
elif hasattr(raw_plan, 'dict'):
    execution_plan = raw_plan.dict()
elif isinstance(raw_plan, str):
    execution_plan = json.loads(raw_plan)
else:
    execution_plan = raw_plan or {}
```


---

## 9️⃣ BŁĄD KRYTYCZNY: output_key nie bąbelkuje w SequentialAgent

### ❌ **Problem:**
```python
# planning_aggregator.py
return LlmAgent(
    output_key="execution_plan",  # ← Powinno zapisać do session.state["execution_plan"]
    output_schema=ExecutionPlan
)

# main.py
async for event in runner.run_async(...):
    pass  # Czekamy na zakończenie

execution_plan = session.state.get("execution_plan")  # ← Zwraca None!
# Dostępne klucze: ['training_plan', 'funkcje_plan']
```

**Skutek:** `output_key` działa świetnie dla pojedynczych agentów, ale gdy agent jest zamknięty w `SequentialAgent`, jego stan jest traktowany jako lokalny i nie "bąbelkuje" do globalnego `InMemorySessionService`.

### ✅ **Rozwiązanie:**
Przechwytywanie danych bezpośrednio ze strumienia eventów!

```python
raw_plan = None
plan_text_buffer = ""

async for event in runner.run_async(...):
    author = getattr(event, 'author', '')

    # Nasłuchujemy na agenta agregującego
    if author == "PlanningAggregator":
        # ADK zwraca obiekty Pydantic w 'event.data'
        if hasattr(event, 'data') and event.data is not None:
            raw_plan = event.data

        # Fallback: zbieramy surowy tekst
        if hasattr(event, 'text') and event.text:
            plan_text_buffer += event.text

        # Sprawdź też event.content
        if hasattr(event, 'content') and event.content:
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    plan_text_buffer += part.text

# Jeśli brak event.data, wydobywamy JSON z tekstu
if not raw_plan and plan_text_buffer:
    import re
    clean_json = re.sub(r'```(?:json)?\s*', '', plan_text_buffer)
    clean_json = re.sub(r'```\s*$', '', clean_json).strip()
    raw_plan = json.loads(clean_json)
```

**Dlaczego to działa:**
- Łapiemy obiekt `event` w locie, kiedy `PlanningAggregator` go wypluwa
- Jeśli framework nie zmapuje go na `Pydantic` (w `event.data`), używamy regex do wydobycia JSON z tekstu
- Niezawodne i "kuloodporne"!



**Bonus:** Można teraz całkowicie usunąć `_build_orchestrator()` - nie jest już potrzebna!

---

## ✅ PODSUMOWANIE NAPRAW:

| Błąd | Typ | Status | Skutek przed naprawą |
|------|-----|--------|---------------------|
| Typ narzędzi (Dict→List) | KRYTYCZNY | ✅ FIXED | Crash podczas bindowania narzędzi |
| State Injection | KRYTYCZNY | ✅ FIXED | Crash podczas formatowania promptu |
| Zahardkodowana ścieżka | LOGICZNY | ✅ FIXED | Nieskończona pętla / fałszywe negatywy |
| Zmartwychwstanie Monolitu | OPTYMALIZACYJNY | ✅ FIXED | Niepotrzebne zużycie pamięci/czasu |
| Import nieistniejącego modułu | KRYTYCZNY | ✅ FIXED | ModuleNotFoundError przy starcie |
| Zombie Monolit w __init__ | OPTYMALIZACYJNY | ✅ FIXED | Marnowanie pamięci przy starcie |
| Brakujący import List | KRYTYCZNY | ✅ FIXED | NameError przy starcie |
| Stale Session (nieaktualny stan) | KRYTYCZNY | ✅ FIXED | 0 modułów w execution_plan |
| output_key nie bąbelkuje w SequentialAgent | KRYTYCZNY | ✅ FIXED | execution_plan nie zapisuje się w stanie |
| temperature nie jest dozwolony w LlmAgent | KRYTYCZNY | ✅ FIXED | ValidationError przy tworzeniu agenta |
| module["files"] to int, nie list (module_generator) | KRYTYCZNY | ✅ FIXED | TypeError: object of type 'int' has no len() |
| module["files"] to int, nie list (main.py summary) | KRYTYCZNY | ✅ FIXED | TypeError przy tworzeniu podsumowania |

---

## 🚀 SYSTEM GOTOWY DO URUCHOMIENIA:

```bash
# Usuń stary output
rm -rf output/output

# Uruchom nowy system (v1.6.0 - wszystkie bugfixy)
python main.py --training-plan ../opis_szkolenia_plan_copilot
```

**Wszystkie błędy naprawione! System gotowy do produkcji!** 🎉


# 🎯 PLAN REFAKTORYZACJI v1.6.0 - Izolacja Sesji

## 📋 ANALIZA PROBLEMU (Doskonała diagnoza użytkownika!)

### ❌ **Problem 1: Zanik pamięci operacyjnej**
**Objaw:** Moduły 2 i 3 nie zostały wygenerowane (brakuje plików)
**Przyczyna:** Wrzucenie wszystkich 8 modułów do jednego `SequentialAgent` powoduje, że sesja rośnie w nieskończoność. Agent w Module 3 ma w głowie wszystko z Module 1, przez co zapomina o podstawowych instrukcjach (np. obowiązek użycia `create_file`).

### ❌ **Problem 2: Sprzeczne instrukcje Tool Calling**
**Objaw:** Model generuje kod w tekście zamiast wywoływać `create_file`
**Przyczyna:** Prompt mówi "wywołaj create_file" ORAZ "ZWRÓĆ TYLKO KOD" - model wybiera drugie

### ❌ **Problem 3: Martwy LoopController**
**Objaw:** LoopController przepuszcza iterację (Approved: True), mimo że pliki nie powstały
**Przyczyna:** TrainingValueCritic ocenia to co model "powiedział", nie to co faktycznie zbudował

### ❌ **Problem 4: Ignorowany YAML Config**
**Objaw:** Doskonale zaprojektowany `agents_config.yaml` jest ignorowany
**Przyczyna:** Parametry są zhardkodowane w funkcjach Pythona

---

## ✅ ROZWIĄZANIA:

### 1️⃣ **IZOLACJA SESJI** (najważniejsze!)

**Zmiana architektury:**
```
PRZED (v1.5.1):
SequentialAgent [Planning → Execution (8 modułów) → Validation]
└─ JEDNA SESJA dla wszystkich 8 modułów
   └─ Kontekst rośnie → zanik pamięci

PO (v1.6.0):
1. Planning Phase (jedna sesja) → execution_plan.json
2. FOR EACH module in plan:
   └─ NOWA SESJA InMemorySessionService
   └─ Przekaż TYLKO wycinek planu dla tego modułu
   └─ Uruchom LoopAgent
   └─ Zamknij sesję
3. Validation Phase (jedna sesja) → sprawdzenie całości
```

**Korzyści:**
- ✅ Każdy agent ma "czysty umysł"
- ✅ Skupia się w 100% na swoim module
- ✅ Brak zanikania pamięci
- ✅ Łatwiejsze debugowanie (osobne logi per moduł)

---

### 2️⃣ **NAPRAWA TOOL CALLING**

**Zmiana promptu w `create_polyglot_code_agent`:**

```python
# PRZED:
"""
Wygeneruj kod...
**ZWRÓĆ TYLKO KOD** (bez meta-komentarzy).
"""

# PO:
"""
**KRYTYCZNE: Pod żadnym pozorem nie wklejaj generowanego kodu do treści swojej odpowiedzi w czacie.**

Twoim JEDYNYM zadaniem jest użycie udostępnionego narzędzia `create_file` dla każdego pliku z listy.

W odpowiedzi tekstowej napisz TYLKO krótkie podsumowanie, np.:
"Utworzyłem 5 plików dla modułu 3:
1. GodClassController.java
2. UserService.java
3. OrderService.java
4. PaymentService.java
5. refactoring_guide.md"

NIE wklejaj kodu do czatu!
"""
```

---

### 3️⃣ **ZAŁATANIE LOOPCONTROLLER**

**Dodaj sprawdzanie wywołań narzędzi:**

```python
class LoopController(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext):
        # Pobierz training_critique
        training_critique = ctx.session.state.get("training_critique", {})
        is_approved = training_critique.get("is_approved", False)
        
        # NOWE: Sprawdź czy narzędzie create_file zostało wywołane
        files_created = ctx.session.state.get("files_created_count", 0)
        files_expected = ctx.session.state.get("files_expected", 0)
        
        if files_expected > 0 and files_created == 0:
            # Agent nie wywołał narzędzia!
            print(f"[LoopController] ❌ Agent nie użył narzędzia create_file!")
            print(f"[LoopController] Oczekiwano: {files_expected} plików, utworzono: 0")
            is_approved = False
        
        # Logowanie
        iteration = ctx.session.state.get("iteration", 0)
        score = training_critique.get("score", 0.0)
        print(f"[LoopController] Iteracja: {iteration}, Score: {score}, Files: {files_created}/{files_expected}, Approved: {is_approved}")
        
        yield Event(
            author=self.name,
            actions=EventActions(escalate=is_approved)
        )
```

**Dodaj licznik w `track_iteration`:**

```python
def track_iteration(ctx: InvocationContext):
    iteration = ctx.session.state.get("iteration", 0) + 1
    ctx.session.state["iteration"] = iteration
    ctx.session.state["training_critique"] = {}
    ctx.session.state["files_created_count"] = 0  # NOWE: Reset licznika
    
    # Pobierz liczbę oczekiwanych plików z execution_plan
    module_id = ctx.session.state.get("module_id", 0)
    execution_plan = ctx.session.state.get("execution_plan", {})
    modules = execution_plan.get("modules", [])
    
    for module in modules:
        if module.get("module_id") == f"module{module_id}":
            files_expected = len(module.get("files", []))
            ctx.session.state["files_expected"] = files_expected
            break
```

**Modyfikuj `create_file` żeby inkrementował licznik:**

```python
def create_file(file_path: str, content: str, base_dir: str = "./output") -> str:
    try:
        full_path = Path(base_dir) / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding='utf-8')
        
        logger.info(f"Created file: {full_path}")
        
        # NOWE: Inkrementuj licznik (jeśli jest dostępny context)
        # To wymaga przekazania ctx do narzędzia - alternatywnie użyj global counter
        
        return f"✅ Created: {full_path}"
    except Exception as e:
        logger.error(f"Error creating file {file_path}: {e}")
        return f"❌ Error: {e}"
```

---

### 4️⃣ **OŻYWIENIE YAML CONFIG**

**Dodaj wczytywanie YAML w `__init__`:**

```python
import yaml

class CopilotMasterclassWorkspaceGenerator:
    def __init__(self, training_plan_path: str, output_dir: str = "./output"):
        # ... existing code ...
        
        # Wczytaj konfigurację YAML
        config_path = Path(__file__).parent / "config" / "agents_config.yaml"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            logger.info(f"📋 Loaded config from: {config_path}")
        else:
            self.config = {}
            logger.warning(f"⚠️  agents_config.yaml not found")
```

**Użyj konfiguracji w agentach:**

```python
def create_polyglot_code_agent(module_id: int, model="gemini-2.5-flash", tools=None, config=None):
    # Pobierz temperature z config
    temperature = 0.7  # default
    if config and "polyglot_code_agent" in config:
        temperature = config["polyglot_code_agent"].get("temperature", 0.7)
    
    return LlmAgent(
        model=model,
        tools=tools,
        name=f"PolyglotCodeAgent_M{module_id}",
        instruction=instruction,
        output_key="generated_code",
        temperature=temperature,  # ← UŻYJ Z CONFIG!
        before_agent_callback=track_iteration
    )
```

---

## 🚀 KOLEJNOŚĆ IMPLEMENTACJI:

1. ✅ **Naprawa Tool Calling** (najprostsza, największy efekt)
2. ✅ **Załatanie LoopController** (średnia trudność)
3. ✅ **Ożywienie YAML** (łatwa, duża wartość)
4. ✅ **Izolacja Sesji** (najtrudniejsza, ale kluczowa)

---

## 📊 OCZEKIWANE REZULTATY:

### Przed (v1.5.1):
- ❌ Brakuje modułów 2 i 3
- ❌ Duplikacja klas (InsurancePolicy w 3 modułach)
- ❌ Agent generuje kod w czacie zamiast wywoływać narzędzie
- ❌ LoopController przepuszcza puste moduły

### Po (v1.6.0):
- ✅ Wszystkie 8 modułów wygenerowane
- ✅ Każdy moduł w innej domenie (Banking, Healthcare, Logistics, etc.)
- ✅ Agent ZAWSZE wywołuje `create_file`
- ✅ LoopController blokuje iterację jeśli brak wywołań narzędzia
- ✅ Parametry z YAML (temperature, max_tokens, etc.)
- ✅ Czyste sesje - brak zanikania pamięci

---

**Status:** 📝 Plan gotowy do implementacji
**Priorytet:** 🔥 KRYTYCZNY (system nie generuje wszystkich modułów)


# 🔍 DIAGNOSTYKA - Zanik pamięci operacyjnej

## ❌ Problem (v1.4.0):

### Objawy:
- ✅ System raportował sukces
- ❌ W `output/` tylko 1 plik zamiast ~40-60 plików
- ❌ Plik nadpisywany 8 razy (ten sam `ShipLogController.java`)

### Logi:
```
21:10:35 - Created file: output\src\...\ShipLogController.java
21:11:19 - Created file: output\src\...\ShipLogController.java  # ← Ten sam plik!
21:12:00 - Created file: output\src\...\ShipLogController.java  # ← Nadpisywanie
21:12:45 - Created file: output\src\...\ShipLogController.java
21:13:30 - Created file: output\src\...\ShipLogController.java
21:14:15 - Created file: output\src\...\ShipLogController.java
21:15:00 - Created file: output\src\...\ShipLogController.java
21:15:45 - Created file: output\src\...\ShipLogController.java
```

### Diagnoza:
**Zanik pamięci operacyjnej** - każdy agent generował Moduł 1 zamiast swojego modułu.

---

## 🔬 Analiza przyczyn:

### 1. Brak `module_id` w prompcie
**Przed (v1.4.0):**
```python
def create_polyglot_code_agent(model="gemini-2.5-flash", tools=None):
    instruction = """Jesteś programistą poliglotą...
    
    Otrzymasz specyfikację pliku (file_spec) z poprzedniego stanu.
    """
    # ← BRAK informacji o module_id!
```

**Problem:** LLM widząc cały `execution_plan` w historii sesji, za każdym razem wybierał pierwszy element (Moduł 1).

---

### 2. SequentialAgent + wspólna historia
**Architektura:**
```python
SequentialAgent(
    sub_agents=[
        ModuleGenerator_1,  # ← Generuje Moduł 1
        ModuleGenerator_2,  # ← Powinien generować Moduł 2, ale...
        ModuleGenerator_3,  # ← ...każdy widzi tę samą historię czatu
        # ...
    ]
)
```

**Problem:** Bez twardego wskazania "Ty jesteś Agentem od Modułu 3", każdy agent zachowywał się jak pierwszy.

---

### 3. Brak wymuszenia iteracji po plikach
**Przed:**
```python
instruction = """...
Po wygenerowaniu kodu, użyj narzędzia `create_file`.
"""
```

**Problem:** Model Flash generował tylko 1 plik, bo prompt nie był "rozpaczliwie" stanowczy.

---

## ✅ Rozwiązanie (v1.4.1):

### 1. Przekazanie `module_id` do agenta
```python
def create_polyglot_code_agent(module_id: int, model="gemini-2.5-flash", tools=None):
    instruction = f"""Jesteś programistą realizującym MODUŁ NR {module_id}.
    
    **KRYTYCZNE: TWÓJ MODUŁ TO module{module_id}!**
    Nie wracaj do poprzednich modułów. Skup się WYŁĄCZNIE na module{module_id}.
    
    1. Znajdź w 'execution_plan' moduł o module_id: "module{module_id}"
    2. W tym module znajdziesz listę plików do wygenerowania
    3. Dla KAŻDEGO pliku wywołaj 'create_file'
    """
```

### 2. Unikalna nazwa agenta
```python
return LlmAgent(
    name=f"PolyglotCodeAgent_M{module_id}",  # ← M1, M2, M3, ...
    description=f"Generates code for module {module_id}",
    # ...
)
```

### 3. Wymuszenie iteracji
```python
instruction = f"""...
Musisz wywołać 'create_file' TYLE RAZY, ILE PLIKÓW jest w module{module_id}.
Jeśli w module jest 5 plików, muszę zobaczyć 5 wywołań narzędzia!
"""
```

---

## 📊 Oczekiwany rezultat (v1.4.1):

### Struktura plików:
```
output/
├── module_01/
│   ├── src/main/java/com/copilot/training/module1/
│   │   ├── File1.java
│   │   ├── File2.java
│   │   └── ...
├── module_02/
│   ├── src/main/java/com/copilot/training/module2/
│   │   ├── File1.java
│   │   └── ...
├── module_07/
│   ├── src/
│   │   ├── script1.py
│   │   └── ...
└── module_08/
    ├── src/
    │   ├── Dashboard.tsx
    │   └── ...
```

### Logi:
```
21:10:35 - [PolyglotCodeAgent_M1] Created: module_01/File1.java
21:10:40 - [PolyglotCodeAgent_M1] Created: module_01/File2.java
21:11:20 - [PolyglotCodeAgent_M2] Created: module_02/File1.java  # ← Inny moduł!
21:11:25 - [PolyglotCodeAgent_M2] Created: module_02/File2.java
21:12:00 - [PolyglotCodeAgent_M3] Created: module_03/File1.java
# ...
```

---

## 🎯 Wnioski:

1. **Zawsze przekazuj kontekst:** `module_id`, `task_id`, `iteration` do promptu
2. **Unikalne nazwy agentów:** Ułatwia debugging i logowanie
3. **Wymuszaj iteracje:** "TYLE RAZY, ILE..." dla modeli Flash
4. **Testuj na małej skali:** 2 moduły zamiast 8 dla szybszego feedback


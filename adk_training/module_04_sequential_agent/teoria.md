# Module 04: Sequential Agent - Teoria

## 🎯 Kluczowe Koncepcje

### SequentialAgent - Orkiestracja Pipeline

**SequentialAgent** uruchamia agentów **po kolei**, przekazując dane przez `output_key` → `{key_name}`.

```python
pipeline = SequentialAgent(
    name="pipeline",
    sub_agents=[agent1, agent2, agent3]  # Kolejność ma znaczenie!
)
```

### Przepływ Danych

```
User Query
    ↓
Agent 1 → output_key="step1" → State["step1"]
    ↓
Agent 2 → instruction="{step1}" → output_key="step2" → State["step2"]
    ↓
Agent 3 → instruction="{step1} {step2}" → output_key="final"
    ↓
Final Response
```

### Wzorzec: output_key + {key_name}

```python
# Agent 1: Zapisuje wynik
agent1 = LlmAgent(
    instruction="Zbierz dane...",
    output_key="dane"  # Zapisz do state["dane"]
)

# Agent 2: Czyta wynik Agent 1
agent2 = LlmAgent(
    instruction="Przeanalizuj: {dane}",  # Odczyt z state
    output_key="analiza"
)
```

---

## 💼 Przypadki Użycia Biznesowego

### 1. Analiza Dokumentów: Ekstrakcja → Walidacja → Podsumowanie

```python
extractor = LlmAgent(
    instruction="Wyciągnij kluczowe dane z dokumentu",
    output_key="extracted_data"
)

validator = LlmAgent(
    instruction="Zwaliduj dane: {extracted_data}",
    output_key="validation_result"
)

summarizer = LlmAgent(
    instruction="Podsumuj: {extracted_data}, Status: {validation_result}",
    output_key="summary"
)

doc_pipeline = SequentialAgent(sub_agents=[extractor, validator, summarizer])
```

**Korzyści:** Separacja odpowiedzialności, łatwiejsze debugowanie, modularność.

### 2. Obsługa Klienta: Klasyfikacja → Routing → Odpowiedź

```python
classifier = LlmAgent(
    instruction="Sklasyfikuj zapytanie: TECH/BILLING/GENERAL",
    output_key="category"
)

specialist = LlmAgent(
    instruction="Odpowiedz na {category}: {user_query}",
    output_key="response"
)

quality_check = LlmAgent(
    instruction="Sprawdź jakość: {response}",
    output_key="final_response"
)
```

### 3. Generowanie Raportów: Dane → Analiza → Formatowanie

```python
data_collector = LlmAgent(
    instruction="Zbierz dane sprzedażowe za Q4",
    output_key="raw_data",
    tools=[get_sales_data]
)

analyzer = LlmAgent(
    instruction="Przeanalizuj trendy: {raw_data}",
    output_key="analysis"
)

formatter = LlmAgent(
    instruction="Sformatuj raport: {raw_data} + {analysis}",
    output_key="report"
)
```

---

## ✅ Najlepsze Praktyki

### 1. Nazewnictwo output_key

| ❌ Źle | ✅ Dobrze |
|--------|-----------|
| `output1` | `raport_wywiadu` |
| `data` | `extracted_customer_data` |
| `result` | `validation_result` |

### 2. Długość Pipeline

- **2-4 agentów**: Optymalne (czytelne, wydajne)
- **5-7 agentów**: Akceptowalne (złożone przypadki)
- **8+ agentów**: Rozważ podział na sub-pipelines

### 3. Obsługa Błędów

```python
validator = LlmAgent(
    instruction="""Zwaliduj dane: {extracted_data}
    
    Jeśli dane niepełne → zwróć: "ERROR: Missing fields"
    Jeśli dane poprawne → zwróć: "VALID"
    """,
    output_key="status"
)

decision_maker = LlmAgent(
    instruction="""Status: {status}
    
    Jeśli status zawiera "ERROR" → STOP, poinformuj użytkownika
    Jeśli "VALID" → kontynuuj
    """
)
```

### 4. Testowanie

```python
# Test każdego agenta osobno
test_state = {"raport_wywiadu": "Test data..."}
result = await strategist.run(state=test_state)

# Test całego pipeline
result = await pipeline.run("Zaplanuj rajd")
```

---

## ⚠️ Typowe Pułapki

### 1. Brak Walidacji Między Krokami

**Problem:** Agent 2 zakłada że Agent 1 zawsze zwraca poprawne dane.

**Rozwiązanie:** Dodaj agenta walidującego między krokami.

### 2. Zbyt Długi Pipeline

**Problem:** 10+ agentów → wolne, drogie, trudne do debugowania.

**Rozwiązanie:** Podziel na mniejsze pipelines lub użyj ParallelAgent.

### 3. Niepoprawne Odwołania do State

**Problem:** `{raport}` zamiast `{raport_wywiadu}` → agent nie widzi danych.

**Rozwiązanie:** Dokładnie dopasuj nazwy `output_key` i `{key_name}`.

### 4. Brak output_key

**Problem:** Agent nie ustawia `output_key` → następny agent nie ma danych.

**Rozwiązanie:** Każdy agent (oprócz ostatniego) MUSI mieć `output_key`.

---

## 🔗 Odniesienia ADK

- [SequentialAgent Docs](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agent/)
- [State Management](https://google.github.io/adk-docs/sessions/state/)

---

## 📝 Podsumowanie

| Koncepcja | Kluczowy Punkt |
|-----------|----------------|
| **SequentialAgent** | Uruchamia agentów po kolei |
| **output_key** | Zapisuje wynik do state |
| **{key_name}** | Odczytuje ze state |
| **Pipeline** | 2-4 agentów = optymalne |
| **Walidacja** | Sprawdzaj dane między krokami |

**Następny krok:** Module 05 - Human-in-the-Loop (zatwierdzanie przez człowieka)


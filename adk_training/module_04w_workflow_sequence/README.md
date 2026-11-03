# Moduł 4W: Workflow – Sekwencja jako graf (ADK 2)

## 📚 Przegląd

Ten sam rajd co w **Module 4** (Zwiadowca → Strateg → Kapitan), ale zbudowany na
nowym prymitywie ADK 2: `Workflow`. W ADK 2.13 `SequentialAgent` działa, ale
jest oznaczony jako **deprecated** (ostrzeżenie przy uruchomieniu).

**Czas trwania:** 30 minut
**Wymaga:** Moduł 4

## 🎯 Cele Edukacyjne

- Zbudować sekwencję agentów przez `Workflow(edges=[...])`
- Wstawić **zwykłą funkcję Pythona** jako krok grafu (bez LLM)
- Przekazywać dane przez stan: `yield Event(state=...)`, `output_key`, `{klucz}`

## 🚀 Szybki Start

```bash
cd adk_training
adk web
```

Wybierz `module_04w_workflow_sequence` i wpisz np.:
- "Zaatakuj hiszpański galeon pod Port Royal"
- "Splądruj fort w Maracaibo"

W zakładce **Events** zobaczysz kolejne węzły: `przyjmij_rozkaz → zwiadowca → strateg → kapitan`.

## 🔑 Kluczowe Koncepcje

### Module 4 (ADK 1, deprecated) vs Module 4W (ADK 2)

```python
# ADK 1
root_agent = SequentialAgent(name="pipeline", sub_agents=[zwiadowca, strateg, kapitan])

# ADK 2
root_agent = Workflow(
    name="pipeline_rajdu_v2",
    edges=[("START", przyjmij_rozkaz, zwiadowca, strateg, kapitan)],
)
```

| Element | Znaczenie |
|---|---|
| `("START", a, b, c)` | Krotka w `edges` = sekwencja a → b → c |
| `def f(node_input): yield Event(state={...})` | Funkcja-węzeł: deterministyczny krok, zapis do stanu |
| `Agent(output_key="k")` | Wynik agenta trafia do `state["k"]` |
| `{k}` / `{k?}` w `instruction` | Odczyt ze stanu (z `?` – opcjonalny) |
| parametr funkcji o nazwie klucza stanu | Wartość wstrzykiwana automatycznie, np. `def f(plan_bitwy: str)` |

**Co zyskujesz:** między agentami możesz wstawić walidację, parsowanie, wywołanie
API albo regułę biznesową – bez pisania własnego `BaseAgent`.

## 🏋️ Ćwiczenia

- **4W.1** – funkcja `ocen_ryzyko(plan_bitwy)` wyciąga z planu poziom ryzyka i zapisuje go do stanu.
- **4W.2** – nowy agent `kwatermistrz` w łańcuchu przed Kapitanem.

Szczegóły w komentarzach w `agent.py`, rozwiązanie w `agent_solution.py`.

## ❓ Częste Problemy

- **`KeyError` / brak zmiennej w instrukcji** – klucz nie istnieje jeszcze w stanie. Użyj `{klucz?}` albo ustaw go wcześniej.
- **Ostrzeżenie `SequentialAgent is deprecated`** w innych modułach – to oczekiwane w ADK 2; ten moduł pokazuje zamiennik.

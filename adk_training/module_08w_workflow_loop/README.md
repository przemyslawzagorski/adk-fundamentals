# Moduł 8W: Workflow – Pętla krytyki jako graf (ADK 2)

## 📚 Przegląd

Ta sama "Pętla Perfekcjonisty" co w **Module 8** (Pisarz → Pierwszy Oficer →
Kapitan), ale bez `LoopAgent` i bez własnej klasy `BaseAgent` z `escalate`.
Pętla to po prostu **krawędź routingu wskazująca na wcześniejszy węzeł**.

**Czas trwania:** 40 minut
**Wymaga:** Moduł 8, Moduł 4W

## 🎯 Cele Edukacyjne

- Zbudować pętlę przez routing (`yield Event(route=...)`)
- Użyć `output_schema` (Pydantic) jako wejścia do routera
- Kontrolować liczbę iteracji przez stan
- (ćwiczenie) Zatrzymać workflow i zapytać człowieka – `RequestInput`

## 🚀 Szybki Start

```bash
cd adk_training
adk web
```

Wybierz `module_08w_workflow_loop` i wpisz wydarzenia dnia, np.
"Sztorm w nocy, złamany bom, dwóch marynarzy z gorączką, kurs na Tortugę".

## 🔑 Kluczowe Koncepcje

```python
def decyzja(ctx: Context, node_input: DecyzjaWpisu):
    if node_input.decision == "valid":
        yield Event(route="gotowe")
    else:
        yield Event(route="popraw")

root_agent = Workflow(
    name="petla_dziennika_v2",
    edges=[
        ("START", start_petli, pisarz, pierwszy_oficer, kapitan, decyzja),
        (decyzja, {"popraw": pisarz, "gotowe": zapisz_w_dzienniku}),  # pętla
    ],
)
```

| Module 8 (ADK 1) | Module 8W (ADK 2) |
|---|---|
| `LoopAgent(max_iterations=5)` | licznik `iteracja` w stanie + warunek w routerze |
| `class CheckStatusAndEscalate(BaseAgent)` | zwykła funkcja `decyzja(...)` |
| `EventActions(escalate=True)` | `yield Event(route="gotowe")` |
| `before_agent_callback` do inicjalizacji stanu | funkcja-węzeł `start_petli` |

## 🏋️ Ćwiczenia

- **8W.1** – Kapitan-człowiek: `RequestInput` przed zapisem. Odpowiedź "tak" zatwierdza, inna treść wraca do Pisarza jako krytyka.
- **8W.2** – zastąp agenta `kapitan` funkcją, która sama sprawdza "No improvements needed" (mniej wywołań modelu).

Rozwiązanie: `agent_solution.py`. Więcej o HITL: Moduł 28.

## ❓ Częste Problemy

- **Pętla się nie kończy** – sprawdź limit `MAX_ITERACJI` i czy Pierwszy Oficer zwraca dokładnie "No improvements needed".
- **RequestInput w adk web** – odpowiedź wpisujesz w polu, które pojawi się pod pytaniem workflow.

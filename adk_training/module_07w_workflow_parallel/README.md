# Moduł 7W: Workflow – Równoległość fan-out / fan-in (ADK 2)

## 📚 Przegląd

Ta sama "Rada Załogi" co w **Module 7**: trzech zwiadowców pracuje równolegle,
a Szpiegmistrz łączy ich raporty. Zamiast `ParallelAgent` + `SequentialAgent`
(deprecated w ADK 2) używamy jednego `Workflow` z **fan-out** i **`JoinNode`**.

**Czas trwania:** 30 minut
**Wymaga:** Moduł 7, Moduł 4W

## 🎯 Cele Edukacyjne

- Uruchomić kilka węzłów równolegle (fan-out)
- Poczekać na wszystkie gałęzie (`JoinNode`, fan-in)
- Przetworzyć wynik `JoinNode` w zwykłej funkcji

## 🚀 Szybki Start

```bash
cd adk_training
adk web
```

Wybierz `module_07w_workflow_parallel` i wpisz np. "Szukamy okazji na łupy w pobliżu Tortugi".
W **Events** zobaczysz, że zwiadowcy kończą w różnej kolejności – działają równolegle.

## 🔑 Kluczowe Koncepcje

```python
from google.adk.workflow import JoinNode

zbiorka = JoinNode(name="zbiorka_raportow")

root_agent = Workflow(
    name="rada_zalogi_v2",
    edges=[(
        "START",
        przyjmij_rozkaz,
        (zwiadowca_polnocny, zwiadowca_poludniowy, zwiadowca_wschodni),  # fan-out
        zbiorka,                                                          # fan-in
        szpiegmistrz,
    )],
)
```

| Element | Znaczenie |
|---|---|
| krotka węzłów `(a, b, c)` w ścieżce | gałęzie uruchamiane równolegle |
| `JoinNode` | czeka na wszystkie gałęzie wchodzące |
| wynik `JoinNode` | `dict` – **klucze to nazwy węzłów**, wartości to ich wyniki |

Każdy zwiadowca dalej zapisuje raport przez `output_key`, więc Szpiegmistrz
czyta je ze stanu (`{raport_polnocny}` itd.).

## 🏋️ Ćwiczenia

- **7W.1** – czwarty zwiadowca (zachodni). Wystarczy dodać go do krotki i instrukcji.
- **7W.2** – funkcja `podsumuj_zbiorke(node_input: dict)` między `JoinNode` a Szpiegmistrzem.

Rozwiązanie: `agent_solution.py`.

## ❓ Częste Problemy

- **429 RESOURCE_EXHAUSTED** – równoległe wywołania szybciej wyczerpują limit. Odczekaj chwilę albo zmniejsz liczbę gałęzi.

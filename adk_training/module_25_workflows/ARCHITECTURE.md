# ARCHITECTURE — Module 25: ADK 2.0 Workflows

> **Cel modułu**: Zrozumieć i zastosować trzy fundamentalne typy Workflow Agents w ADK 2.0:
> `SequentialAgent`, `LoopAgent`, `ParallelAgent` — determinizm zamiast promptowania.

---

## Dlaczego Workflows zamiast jednego LlmAgent?

| Cecha                    | ADK1: LlmAgent dispatcher | ADK2: Workflow Agents       |
|--------------------------|---------------------------|-----------------------------|
| Kolejność kroków         | Zależy od LLM (prompt)    | **Gwarantowana przez kod**  |
| Testowalność węzłów      | Trudna (czarna skrzynka)  | **Każdy agent z osobna**    |
| Retry pojedynczego kroku | Niemożliwy                | **Wbudowany w LoopAgent**   |
| Równoległość             | Brak                      | **ParallelAgent natywnie**  |
| Obserwowalność           | Jeden długi span          | **Span per node**           |
| Koszt LLM                | 1 model robi wszystko     | **Tani router + specjaliści** |

---

## Diagram przepływu (Workflow A — Sequential PR Review)

```
USER INPUT (diff/PR description)
        │
        ▼
┌───────────────────┐     output_key="pr_recon_report"
│  pr_recon         │ ──────────────────────────────────────────► session.state
│  (LlmAgent)       │     Metadane PR: rozmiar, obszary ryzyka
└────────┬──────────┘
         │ (automatycznie)
         ▼
┌───────────────────┐     output_key="pr_review_result"
│  pr_reviewer      │ ──────────────────────────────────────────► session.state
│  (LlmAgent)       │     Czyta {pr_recon_report}, tworzy review
└────────┬──────────┘
         │ (automatycznie)
         ▼
┌───────────────────┐     output_key="pr_final_report"
│  pr_reporter      │ ──────────────────────────────────────────► session.state
│  (LlmAgent)       │     Czyta oba outputs → finalny raport CI
└───────────────────┘
```

**Kluczowy mechanizm**: `output_key="xxx"` w LlmAgent → wynik trafia do `session.state["xxx"]`.
Następny agent czyta go przez `{xxx}` w `instruction`.

---

## Diagram przepływu (Workflow C — Parallel Analysis)

```
USER INPUT (kod do analizy)
        │
        ├────────────────────────────────────────┐
        ▼                                        ▼
┌──────────────────┐                   ┌──────────────────────┐
│ security_scanner │                   │ performance_analyzer  │
│ (LlmAgent)       │                   │ (LlmAgent)            │
│ OWASP Top 10     │                   │ O(n²), N+1, leaks     │
└────────┬─────────┘                   └─────────┬────────────┘
         │ output_key=security_findings           │ output_key=performance_findings
         └────────────────┬───────────────────────┘
                          │ (ParallelAgent czeka na OBA)
                          ▼
               ┌──────────────────┐
               │ analysis_summary │
               │ (LlmAgent)       │
               │ Scala wyniki     │
               └──────────────────┘
```

---

## Komponenty

### `SequentialAgent` — kiedy używać
- Pipeline wieloetapowy, gdzie każdy krok wymaga wyniku poprzedniego
- Przykłady: recon → plan → execute → report, translate → validate → publish
- **ADK2 pattern**: każdy `LlmAgent` ma `output_key` → dane płyną przez `session.state`

### `LoopAgent` — kiedy używać
- Iteracyjna poprawa: "poprawiaj aż kod jest dobry"
- Walidacja z retry: "sprawdź API aż odpowiedź jest poprawna"
- Konfiguracja: `max_iterations` zapobiega nieskończonej pętli
- **ADK2 pattern**: subagent sygnalizuje koniec (np. słowo kluczowe w output)

### `ParallelAgent` — kiedy używać
- Niezależne zadania: security scan + performance scan + style check
- Agregacja wyników: każdy parallel node ma `output_key`, potem sequential summary
- **Zysk**: czas = max(t_node1, t_node2) zamiast t_node1 + t_node2

---

## Związek z Module 23 (AI Code Concierge)

Module 23 używa **jednego LlmAgent** (`ai_code_concierge`) jako dispatcher z 9 toolami.
Module 25 pokazuje jak **rozbić ten pattern** na deterministyczny workflow:

```
ADK1 (Module 23):           ADK2 (Module 25):
LlmAgent dispatcher         SequentialAgent
  → tool: code_review_pr      → pr_recon (LlmAgent)
  → tool: analyze_codebase    → pr_reviewer (LlmAgent + Auggie tool)
  → tool: security_audit      → pr_reporter (LlmAgent)
```

**Korzyść**: jeśli `pr_reviewer` (Auggie) zawiedzie, można go retry bez ponownego
uruchamiania `pr_recon`. W ADK1 cały dispatcher musiałby startować od nowa.

---

## TODO — zadania dla dewelopera

```
[ ] Uruchom: adk run adk_training/module_25_workflows --message "Review PR: dodano plik utils.py +150 linii"
[ ] Obserwuj w ADK Web UI kolejność wywołań węzłów (zakładka Events)
[ ] Zmień SequentialAgent → ParallelAgent dla pr_recon i pr_reviewer — co się zmieni?
[ ] Dodaj rzeczywiste wywołanie Auggie w pr_reviewer (zob. module_23/auggie_factory.py)
[ ] Napisz test jednostkowy dla pr_recon w izolacji (MockLlmAgent)
[ ] Zmierz czas: parallel_analysis vs. sequential (dwa osobne agenty po kolei)
[ ] Dodaj LoopAgent wokół quality_checker z prawdziwym kodem do poprawy
[ ] Porównaj koszty tokenów: ADK1 dispatcher vs. ADK2 workflow (sprawdź auggie_telemetry)
```

---

## Uruchomienie

```bash
# Upewnij się że jesteś w venv z google-adk>=2.0 (--pre)
pip install google-adk --pre

# Uruchom demo
adk run adk_training/module_25_workflows

# Lub testuj bezpośrednio
python -c "
from adk_training.module_25_workflows.agent import pr_review_pipeline
print('Pipeline załadowany:', pr_review_pipeline.name)
print('Sub-agents:', [a.name for a in pr_review_pipeline.sub_agents])
"
```

---

## Dokumentacja ADK 2.0

- [Workflow Agents](https://google.github.io/adk-docs/agents/workflow-agents/)
- [Sequential Agents](https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/)
- [Loop Agents](https://google.github.io/adk-docs/agents/workflow-agents/loop-agents/)
- [Parallel Agents](https://google.github.io/adk-docs/agents/workflow-agents/parallel-agents/)
- [ADK 2.0 Graph-based Workflows](https://adk.dev/2.0/)

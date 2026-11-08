# Bonus Topologies 02d: `BuiltInPlanner` — natywny thinking modelu

## Czego się nauczysz?

- Jak **`BuiltInPlanner`** włącza wbudowane „myślenie” modelu Gemini przez `ThinkingConfig`
  zamiast tekstowego planu w prompcie.
- Parametry `ThinkingConfig`:
  - `thinking_level` (`MINIMAL` / `LOW` / `MEDIUM` / `HIGH`) – zalecane dla Gemini 3.x,
  - `thinking_budget` – limit tokenów myślenia (starsze modele 2.5),
  - `include_thoughts=True` – podsumowania myśli trafiają do eventów (widać je w `adk web`).
- `BuiltInPlanner` ma pierwszeństwo przed `generate_content_config.thinking_config`
  (ADK loguje ostrzeżenie, jeśli ustawisz oba).

```python
planner=BuiltInPlanner(
    thinking_config=types.ThinkingConfig(
        thinking_level=types.ThinkingLevel.HIGH,
        include_thoughts=True,
    )
)
```

Porównaj z [02c – PlanReActPlanner](../adk_topologies_02c_react_planner/Readme.md):
ten sam zespół ekspertów, inny planner.

## Architektura

```
employee_assistant_thinking  (planner=BuiltInPlanner(thinking_level=HIGH))
   ├─ AgentTool(marketing_expert)
   ├─ AgentTool(legal_expert)
   └─ AgentTool(google_cloud_expert)
```

## Uruchomienie

```powershell
cd adk_training\pz_bonus
adk web .
```

Wybierz `adk_topologies_02d_builtin_planner` i zadaj to samo pytanie co w 02c:

> Wchodzimy z SaaS analitycznym na BigQuery na rynek UE. Jaki kąt marketingowy i jakie ryzyka RODO sprawdzić?

## Co zaobserwować (wynik z testu)

1. Myśli modelu pojawiają się jako osobne części *thought* (podsumowanie w stylu
   „**My Synthesis of Expert Insights**…”).
2. Model wywołał **wszystkich trzech ekspertów równolegle** w jednej turze
   (parallel function calling) – zwykle krócej niż sekwencyjny ReAct (~28 s vs ~42 s w teście).
3. Po wynikach ekspertów jest druga faza myślenia (synteza), a potem odpowiedź końcowa.

| | 02c PlanReAct | 02d BuiltIn |
|---|---|---|
| Gdzie jest plan | tekst w odpowiedzi (tagi) | natywne thoughts modelu |
| Wymaga modelu z thinkingiem | nie | tak |
| Wywołania narzędzi | zwykle sekwencyjnie | często równolegle |
| Kontrola kosztu | długość promptu | `thinking_level` / `thinking_budget` |

## Ćwiczenia

1. Zmień `thinking_level` na `LOW` i porównaj czas, jakość i liczbę wywołanych ekspertów.
2. Ustaw `include_thoughts=False` – czy zmienia się odpowiedź, czy tylko to, co widać w UI?
3. Usuń planner i ustaw ten sam `thinking_config` w
   `generate_content_config=types.GenerateContentConfig(thinking_config=...)`.
   Jaki jest efekt? (Odpowiedź: identyczny – planner to wygodny skrót.)
4. Domyślny model to `gemini-3.5-flash-lite`. Na `LOW` lite **w ogóle nie myśli**
   (0 thoughts), na `HIGH` myśli. Porównaj z `ADK_MODEL=gemini-3.5-flash`, który
   myśli już na `LOW`. Wniosek: tańszy model + wyższy `thinking_level` vs droższy
   model + niższy – policz tokeny (`thoughts_token_count` w Events).

## Odnośniki

- [ADK – LLM agents: planner](https://google.github.io/adk-docs/agents/llm-agents/#planner)
- [Gemini – Thinking](https://ai.google.dev/gemini-api/docs/thinking)

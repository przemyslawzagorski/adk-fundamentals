# D1.11a: `PlanReActPlanner` — jawny plan w tekście

## Czego się nauczysz?

- Czym jest **planner** w ADK (`Agent(planner=...)`) i kiedy go używać.
- Jak **`PlanReActPlanner`** wymusza schemat *Plan → Action → Reasoning → Final answer*
  przez instrukcję systemową i tagi (`/*PLANNING*/`, `/*ACTION*/`, `/*REASONING*/`,
  `/*FINAL_ANSWER*/`), a ADK oznacza części planu jako *thought*.
- Wzorzec **koordynator + eksperci jako `AgentTool`** (koordynator zachowuje kontrolę i sam
  składa odpowiedź – w przeciwieństwie do `sub_agents`, gdzie następuje transfer).

Porównaj z [d1_11b – BuiltInPlanner](../d1_11b_builtin_planner/Readme.md):
ten sam zespół ekspertów, inny planner.

## Architektura

```
employee_assistant_react  (planner=PlanReActPlanner())
   ├─ AgentTool(marketing_expert)
   ├─ AgentTool(legal_expert)
   └─ AgentTool(google_cloud_expert)
```

## Uruchomienie

```powershell
cd adk_training
adk web
```

Wybierz `d1_11a_react_planner` i zapytaj np.:

> Wchodzimy z SaaS analitycznym na BigQuery na rynek UE. Jaki kąt marketingowy i jakie ryzyka RODO sprawdzić?

## Co zaobserwować (wynik z testu)

1. Pierwsza część odpowiedzi to **plan w punktach** (thought) – „1. zapytam marketing_expert…,
   2. zapytam legal_expert…, 3. połączę odpowiedzi”.
2. Eksperci są wywoływani **sekwencyjnie**, po każdym wyniku pojawia się krótkie *reasoning*
   i kolejna akcja.
3. Koordynator wywołuje tylko tych ekspertów, których przewidział w planie.

Plan jest **czytelny i audytowalny** (zwykły tekst w historii), a planner działa także
z modelami **bez** natywnego thinkingu.

## Ćwiczenia

1. Zadaj pytanie dotyczące tylko jednej dziedziny („Jak nazwać kampanię?”). Czy plan
   ogranicza się do jednego eksperta?
2. Dodaj eksperta `finance_expert` (budżet, pricing) i sprawdź, kiedy trafia do planu.
3. Uruchom to samo pytanie w d1_11a i d1_11b. Porównaj: liczbę wywołań, kolejność (sekwencyjnie
   vs równolegle), czas, czytelność planu w zakładce Trace.

## Odnośniki

- [ADK – LLM agents: planner](https://google.github.io/adk-docs/agents/llm-agents/#planner)
- [ADK – Agent as a tool](https://google.github.io/adk-docs/tools-custom/function-tools/#agent-tool)

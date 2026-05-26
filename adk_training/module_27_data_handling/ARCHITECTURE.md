# ARCHITECTURE — Module 27: ADK 2.0 Data Handling

> **Cel modułu**: Zarządzanie kontekstem, stanem i przekazywaniem danych między węzłami grafu.
> Structured state flow zamiast "string ping-pong" między agentami.

---

## Modele danych w ADK 2.0

### 1. `session.state` — główny mechanizm przekazywania danych

```python
# Zapis (w LlmAgent przez output_key):
agent = LlmAgent(
    output_key="my_result"  # wynik agenta trafia do state["my_result"]
)

# Odczyt (w instruction następnego agenta):
instruction = "Poprzedni wynik: {my_result}"  # template substitution

# Bezpośredni dostęp w CallbackContext:
def my_callback(ctx: CallbackContext) -> None:
    value = ctx.state.get("my_result")   # odczyt
    ctx.state["enriched"] = True          # zapis
```

### 2. `FunctionTool` + `ToolContext` — tools z dostępem do stanu

```python
# UWAGA: w ADK 2.0 tool może pisać do state przez ToolContext
# (w ADK1 tools były stateless)
def my_tool(query: str, tool_context: ToolContext) -> str:
    # Odczyt ze state
    user_prefs = tool_context.state.get("user_preferences", {})
    # Zapis do state (persystowane między wywołaniami)
    tool_context.state["last_query"] = query
    return f"Result for {query}"
```

### 3. `Artifacts` — duże dane binarne

```python
# Zapis artefaktu (np. screenshot z Playwright, raport PDF)
async def save_report(ctx: InvocationContext, pdf_bytes: bytes):
    artifact = types.Part.from_data(data=pdf_bytes, mime_type="application/pdf")
    await ctx.save_artifact("audit_report.pdf", artifact)

# Odczyt artefaktu w następnym węźle
artifact = await ctx.load_artifact("audit_report.pdf")
```

---

## Diagram przepływu danych

```
USER: "Przeanalizuj ten kod: def foo(): pass"
              │
              ▼
    ┌─────────────────┐
    │   code_intake   │ output_key="intake_context"
    │   (LlmAgent)    │ ──────────────────────────► state["intake_context"] = {
    └────────┬────────┘                               "language": "python",
             │                                         "analysis_goal": "quality",
             ▼                                         ...
    ┌─────────────────┐                             }
    │code_enrichment  │ Reads: {intake_context}
    │(LlmAgent+Tool)  │ Calls: enrich_code_metadata()
    │                 │ output_key="code_metadata"  ──► state["code_metadata"] = {
    └────────┬────────┘                               "line_count": 1,
             │                                         "has_functions": true,
             ▼                                         ...
    ┌─────────────────┐                             }
    │  code_analysis  │ Reads: {intake_context} + {code_metadata}
    │   (LlmAgent)    │ output_key="analysis_result" ► state["analysis_result"] = {
    └────────┬────────┘                               "issues": [...],
             │                                         "severity": "low",
             ▼                                         ...
    ┌─────────────────┐                             }
    │result_validation│ Reads: {analysis_result}
    │(LlmAgent+Tool)  │ Calls: validate_analysis_result()
    │                 │ output_key="validation_status"► state["validation_status"]
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │  final_output   │ Reads: WSZYSTKIE klucze ze state
    │   (LlmAgent)    │ Agreguje pełny raport dla użytkownika
    └─────────────────┘
```

---

## Wzorce zarządzania danymi

### Pattern: Structured State (zamiast string)

```python
# ❌ ADK1 — dane jako tekst (kruche)
instruction = "Przeanalizuj: {previous_output}"
# previous_output = "Znaleziono 3 issues: SQL injection na linii 42..."

# ✅ ADK2 — dane jako JSON w state (strukturalne)
instruction = "Analiza goal: {intake_context}"
# state["intake_context"] = {"goal": "security", "priority": "high", ...}
```

### Pattern: Tool jako data enricher

```python
# Tool nie tylko ROBI coś — może też WZBOGACAĆ state
def enrich_code_metadata(code: str, language: str) -> dict:
    # Deterministyczna analiza kodu (nie LLM)
    return {"line_count": ..., "complexity": ..., "imports": [...]}
# LlmAgent wywołuje tool → wynik trafia jako output_key do state
```

### Pattern: Validation gate

```python
# Węzeł walidacji sprawdza strukturę danych PRZED finalnym outputem
# Jeśli dane są niekompletne → raport to sygnalizuje (nie blokuje, ale ostrzega)
def validate_analysis_result(analysis_json: str) -> dict:
    required = ["issues", "severity", "recommendations"]
    missing = [f for f in required if f not in json.loads(analysis_json)]
    return {"valid": len(missing) == 0, "missing_fields": missing}
```

---

## Związek z Module 23 (AI Code Concierge)

Module 23 (`agent.py`) zwraca dane jako plain text stringi:
```python
# Module 23 — tool zwraca tekst
def code_review_pr(diff, repo_context) -> str:
    return auggie_run(..., return_type=str)  # plain string
```

Module 27 pokazuje jak to zmodernizować:
```python
# Module 27 — structured data flow
output_key="review_result"  # JSON w state
# Następny węzeł czyta {"issues": [...], "severity": "high"} — nie parsuje tekstu
```

---

## TODO — zadania dla dewelopera

```
[ ] Uruchom pipeline i otwórz ADK Web UI → zakładka "State" — obserwuj jak state rośnie
[ ] Zmodyfikuj output_key="analysis_result" na inny klucz i obserwuj błąd w {analysis_result}
[ ] Dodaj CallbackContext validator między enrichment a analysis (sprawdź kod_metadata przed analizą)
[ ] Zintegruj ctx.save_artifact() — zapisz finalny raport jako HTML/PDF
[ ] Dodaj ToolContext do enrich_code_metadata: pisz statystyki do state["tool_stats"]
[ ] Przepisz Module 23 tools.py by zwracały dict zamiast str → porównaj testowalność
[ ] Sprawdź co się dzieje gdy intake_context jest None w enrichment (missing state key)
[ ] Dodaj schema validation (Pydantic) dla każdego output_key
```

---

## Dokumentacja ADK 2.0

- [Session State](https://google.github.io/adk-docs/components/sessions/state/)
- [Context & Callbacks](https://google.github.io/adk-docs/components/callbacks/)
- [Artifacts](https://google.github.io/adk-docs/components/artifacts/)
- [ADK 2.0 Data Handling](https://adk.dev/2.0/)

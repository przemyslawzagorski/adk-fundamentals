# Rozszerzanie

Trzy typowe ścieżki modyfikacji: **dodanie narzędzia** (tool), **dodanie workflow'u**, **dodanie endpointu**.

## 1. Dodanie nowego tool-a

Przykład: narzędzie `count_todos(repo_path)` zliczające `TODO:` w kodzie.

### Krok 1 — funkcja Python

W [`file_tools.py`](../architektura/komponenty.md) (lub nowym module):

```python
def count_todos(repo_path: str) -> dict:
    """Zlicz wystapienia TODO / FIXME / HACK w plikach zrodlowych."""
    counts = {"TODO": 0, "FIXME": 0, "HACK": 0}
    repo_real = os.path.realpath(repo_path)

    for root, _, files in os.walk(repo_real):
        for f in files:
            full = os.path.join(root, f)
            if is_secret_file(full):
                continue
            if os.path.getsize(full) > settings.max_file_size:
                continue
            try:
                with open(full, encoding="utf-8", errors="ignore") as fh:
                    for line in fh:
                        for key in counts:
                            if key in line:
                                counts[key] += 1
            except OSError:
                continue

    return {"ok": True, "counts": counts}
```

Reguły:

- Zawsze `{"ok": bool, ...}`.
- Waliduj ścieżki przez `safe_resolve`.
- Sprawdzaj `is_secret_file`.
- Błędy → `{"ok": False, "error": "..."}`.
- Logi przez `log.debug/info/warning/error`.

### Krok 2 — rejestracja w fabryce

W [`code_retrieval_tool.py`](../architektura/komponenty.md) albo w `_build_agent` w `web/app.py`:

```python
from google.adk.tools import FunctionTool

def count_todos_wrapper(repo_path: str) -> dict:
    return count_todos(repo_path)

tools = [
    # ...istniejące tools
    FunctionTool(count_todos_wrapper),
]
```

### Krok 3 — instrukcja agenta

Dodaj w system instruction opis kiedy wywołać:

```python
_INSTR = """
...
NARZEDZIA:
- count_todos(repo_path) -> zlicz TODO/FIXME/HACK w projekcie.
  Uzyj gdy user pyta o "dlug techniczny" / "ile TODO" / "health check".
...
"""
```

### Krok 4 — test

```python
def test_count_todos(tmp_path):
    (tmp_path / "a.py").write_text("# TODO: fix\n# FIXME later\n")
    (tmp_path / "b.py").write_text("# HACK\n# TODO")
    result = count_todos(str(tmp_path))
    assert result["ok"] is True
    assert result["counts"]["TODO"] == 2
    assert result["counts"]["FIXME"] == 1
    assert result["counts"]["HACK"] == 1
```

## 2. Dodanie nowego workflow'u

Workflow to sekwencja sub-agentów. Przykład: **Tech Debt Report** = CodeAnalyst → Summarizer.

### Krok 1 — definicja w `WORKFLOWS`

W [`web/app.py`](../architektura/komponenty.md):

```python
WORKFLOWS: dict[str, dict] = {
    # ...istniejące
    "tech_debt": {
        "label": "Tech debt report",
        "icon": "🧹",
        "description": "Znajdz TODO/FIXME/HACK i zaproponuj plan splaty.",
        "system_hint": (
            "Uzyj count_todos i search_code aby zlokalizowac dlug techniczny. "
            "Pogrupuj po module i priorytetyzuj (high/med/low). "
            "Zakoncz planem splaty na 3 sprinty."
        ),
        "agents": ["code_analyst", "summarizer"],
    },
}
```

### Krok 2 — aktualizacja UI

`templates/repo.html` renderuje workflowy z `WORKFLOWS` automatycznie — żadnej zmiany.

### Krok 3 — test manualny

```bash
curl -X POST http://localhost:8088/repos/$ID/workflow \
  -H "X-API-Key: $KEY" \
  -d "workflow_id=tech_debt&user_input=skup sie na module auth"
```

Szczegóły: [Workflows](../architektura/workflows.md).

## 3. Dodanie nowego endpointu

Przykład: `GET /repos/{id}/stats` zwracający JSON ze statystykami indeksu.

```python
@app.get(
    "/repos/{repo_id}/stats",
    dependencies=[Depends(_require_api_key)],
)
async def repo_stats(repo_id: str) -> dict:
    repo = repo_manager.get(repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")
    indexer = await _get_indexer(repo)
    return {
        "repo_id": repo_id,
        "indexed_files": indexer.indexed_files_count,
        "last_indexed_at": repo.last_indexed_at,
    }
```

Checklist:

- `dependencies=[Depends(_require_api_key)]` jeśli endpoint ma być chroniony.
- `include_in_schema=False` gdy zwraca HTML fragmenty.
- Rate limit decoratorem `@_rate_search` / `@_rate_workflow` / własny.
- Loguj błędy przez `log.exception()`.
- Metryka Prometheus jeśli endpoint "ciężki".

## 4. Dodanie nowego sub-agenta

Przykład: `SecurityReviewer` skupiony na OWASP.

### Krok 1 — instrukcja

```python
_SECURITY_INSTR_PL = """
Jestes inzynierem bezpieczenstwa (OWASP Top 10).
Twoim celem jest analiza kodu pod katem:
- injection (SQL/command/template),
- broken auth,
- sensitive data exposure,
- XXE, broken access control, misconfiguration,
- XSS, deserialization, known vulnerabilities, logging gaps.

Uzywaj search_code aby znalezc wzorce. read_project_file aby zweryfikowac.
Nie improwizuj - jesli cos wyglada OK, powiedz "OK".
"""
```

### Krok 2 — fabryka agenta

```python
def _make_security_reviewer(tools) -> LlmAgent:
    return LlmAgent(
        name="SecurityReviewer",
        model=settings.llm_model,
        instruction=_SECURITY_INSTR_PL,
        tools=tools,
    )
```

### Krok 3 — rejestracja w `AGENT_BUILDERS`

```python
AGENT_BUILDERS = {
    "code_analyst": _make_code_analyst,
    "architect": _make_architect,
    "developer": _make_developer,
    "summarizer": _make_summarizer,
    "security_reviewer": _make_security_reviewer,  # nowy
}
```

### Krok 4 — użycie w workflow'ie

```python
"security_audit": {
    "label": "Audyt bezpieczenstwa",
    "icon": "🛡️",
    "system_hint": "Wykonaj audyt OWASP Top 10. Wynik — tabela findings.",
    "agents": ["code_analyst", "security_reviewer", "summarizer"],
},
```

## Design rules — co ja zalecam

1. **Nowy tool > nowy agent** — tool jest tańszy w utrzymaniu.
2. **Nowy workflow > nowy endpoint** — workflowy są konfiguracją, endpointy kodem.
3. **Nigdy nie omijaj `safe_resolve`** — nawet w "prostym" tool-u.
4. **Zawsze `{"ok": bool}`** — agent sprawdza to pole.
5. **Limit tokenów** — agent może iterować wiele razy, twardy limit obciąża koszt.

Następnie: [Deployment](../operacje/deployment.md).

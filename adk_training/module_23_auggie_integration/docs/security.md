# Security

## Granice zaufania

| Granica | Mechanizm |
|---|---|
| Sekrety → LLM | `auth.py` `redact()` — filtruje cookies/tokeny w promptach |
| Web → backend | CORS dev-only `localhost:5173`; produkcja wymaga reverse proxy |
| Backend → LLM | TLS Anthropic API; klucz z `.env` (nie commitować) |
| LLM → workspace | Auggie ma allowlistę katalogów (`workspace-root`) |
| LLM → web (AuditOps) | `safety.py` allowlista hostów — nie audytujemy bez zgody |

## Sekrety

- `ANTHROPIC_API_KEY` w `.env` (template: `.env.template`).
- `GITHUB_TOKEN` w GH Actions — z `secrets.GITHUB_TOKEN`.
- **Nigdy** nie commituj `.env` (jest w `.gitignore`).
- Audyt zmiennych: `python -m adk_training.module_23_auggie_integration.health_check --full`.

## Logowanie

- Brak loggera per-prompt (zawiera kod użytkownika).
- Logger info-level: tool name, latency, cache hit/miss, koszt.
- Debug level (opt-in): pełny prompt — używaj tylko w developmencie.

## Path traversal (skille)

`skills_loader.load_resource()` resolve'uje ścieżkę i sprawdza prefiks vs `references/` —
patrz `module_24/skills_loader.py`. Dotyczy też dowolnego modułu, który użyje tej funkcji.

## CORS

`web/app.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Na produkcji: konkretny hostname za reverse proxy + auth.

## Audyt platformy samej w sobie

Możesz uruchomić AuditOps przeciwko własnemu Concierge UI (kontrolowany allowlist):

```powershell
python -m adk_training.module_24_audit_ops.cli audit --target http://localhost:5173 --allow localhost
```

Wynik trafia do `module_24/artifacts/wiki/localhost/index.md`.

## Roadmap

- [ ] Multi-tenant auth (SSO).
- [ ] Per-user rate limit + USD budget.
- [ ] Signed prompts (audit trail w wiki).

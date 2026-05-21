# Code Analyst

System agentowy do analizy, naprawy i rozwijania kodu zrodlowego.
9 workflowow (6 analitycznych + 3 implementacyjne), Web UI + CLI.

**Pelna dokumentacja:** [PRODUCT.md](PRODUCT.md)

## Szybki start

```bash
cd adk_training/module_13_code_analyst
cp .env.template .env        # ustaw GOOGLE_CLOUD_PROJECT

# CLI
adk web                      # -> http://localhost:8000

# Web UI (multi-repo, workflows)
cd web && python app.py      # -> http://127.0.0.1:8088
```

## Co potrafi

| Tryb | Workflow | Efekt |
|------|----------|-------|
| **Analiza** | Onboarding, impact analysis, security audit, stories, dokumentacja, debugging | Raporty, diagramy Mermaid, stories z AC/DoD |
| **Implementacja** | Napraw buga, implementuj CR, generuj testy | Kod + testy na feature branchu (nigdy push/merge) |

## Stack

Google ADK + LlamaIndex + Vertex AI (Gemini 2.0 Flash) + FastAPI + HTMX.
Opcjonalnie: GitHub MCP, Comarch MCP (Jira/GitLab/Wiki).

## Wymagania

- Python 3.11+, Git, projekt GCP z Vertex AI
- Maven/Gradle (projekty Java) - do kompilacji i testow
- `pip install -r requirements.txt`

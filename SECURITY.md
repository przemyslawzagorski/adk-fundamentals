# Bezpieczenstwo repozytorium

## Sekrety i tokeny
- `.env` jest w `.gitignore`. Wszystkie poufne wartosci (GitHub PAT, Jira/Wiki/GitLab bearer, API keys) **ida tylko do `.env` lokalnie** lub do Secret Manager (Cloud Run).
- `.env.template` zawiera wylacznie placeholdery.
- Nie wklejaj zywych tokenow do wiadomosci czatu, PR, issue, dokumentow — logi sa przechowywane po stronie dostawcow AI.

## Pre-commit
Aby zablokowac przypadkowe commity z sekretami:

```powershell
pip install pre-commit detect-secrets
pre-commit install
# jednorazowo — scan calego repo:
detect-secrets scan --baseline .secrets.baseline
```

Hooki:
- `detect-secrets` (Yelp) — skanuje wszystkie zmienione pliki.
- `tools/check_no_live_tokens.py` — dodatkowy prosty guard na wzorce
  `ghp_...`, `glpat-...`, `AIza...`, `Bearer ...`, Jira/Wiki bearer Comarch (base64:base64).
- `detect-private-key` — klucze RSA/EC/OpenSSH.
- `check-added-large-files`, `check-merge-conflict`, `check-yaml`, `check-json`.

False-positive mozna wyciszyc komentarzem na tej samej linii: `# pragma: allowlist secret`.

## Co zrobic gdy token wyciekl
1. Natychmiast uniewaznij (revoke) token w systemie zrodlowym:
   - Jira: `https://tapir.krakow.comarch/jira` -> Personal Access Tokens
   - Confluence Wiki: analogicznie
   - GitLab: Preferences -> Access Tokens
   - GitHub: `https://github.com/settings/tokens`
2. Wygeneruj nowy i zapisz tylko w `.env` lokalnym.
3. Jesli trafil do git history: `git filter-repo` lub BFG Repo-Cleaner + wymuszony push.
4. Monitoruj wykorzystanie (logi Jira/GitLab) przez najblizsze 24h.

## Redakcja logow
- `logging_config.py` musi usuwac wzorce sekretow z logow aplikacji.
- `tools/export_chat.py` ma wbudowana redakcje (`ghp_`, `glpat-`, `Bearer`, bearer Comarch) przed zapisem `.md`.
- Rozwaz dodatkowe filtry w `uvicorn` (middleware) gdy ruchem sa przesylane tokeny Jira/Wiki.

## Cloud Run / produkcja
- Tokeny przez Secret Manager, nie przez ENV plain-text.
- `NODE_TLS_REJECT_UNAUTHORIZED=0` jest **niedozwolone** w prod — uzywaj `NODE_EXTRA_CA_CERTS`.

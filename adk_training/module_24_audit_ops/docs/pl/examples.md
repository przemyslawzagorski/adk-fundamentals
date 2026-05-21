# Konkretne przykłady

Każdy przykład poniżej jest kopiuj-wklej-uruchom. Ścieżki PowerShell zakładają
root repo `c:\Users\NBPZAGORSKI\IdeaProjects\adk-fundamentals`.

> Zobacz też: `EXAMPLES.md` w korzeniu modułu — te same recipes poza MkDocs.

## 1. Pierwszy run na nowym targecie

```powershell
.venv312\Scripts\python.exe -m adk_training.module_24_audit_ops.cli `
    --url https://staging.acme.test/ `
    --allow-domain staging.acme.test `
    --fail-on high `
    --report-dir .\artifacts
```

Rezultat:

- `artifacts\<run_id>\report.md` + `report.json`
- `artifacts\wiki\staging.acme.test\index.md` (utworzony)
- `artifacts\wiki\staging.acme.test\runs\<run_id>.md`
- Po jednej stronie encji finding na każde finding.

## 2. Drugi run — zobacz, jak skill audit-history wchodzi do gry

Uruchom tę samą komendę. W tle:

1. `wiki.history_skill_text` zwraca niepuste body.
2. `_build_history_skill` opakowuje to jako syntetyczny skill `audit-history`.
3. `render_planner_context` włącza to body do prompta plannera.

Możesz to zweryfikować przez API:

```powershell
curl http://localhost:8080/api/audit/wiki/staging.acme.test/index
```

## 3. Run guided — scenariusz w naturalnym języku

```powershell
.venv312\Scripts\python.exe -m adk_training.module_24_audit_ops.cli `
    --url https://staging.acme.test/login `
    --allow-domain staging.acme.test `
    --mode guided `
    --scenario-nl "Spróbuj logowania z ' OR 1=1-- i zaraportuj, czy fingerprinty błędów SQL wyciekają w odpowiedzi." `
    --fail-on high
```

Skills loader wstrzyknie `owasp-a03-injection` (formularz POST) plus
`recon-helpers`. LLM dostaje gotowe do użycia referencje fingerprintów
błędów SQLi.

## 4. Skan autentykowany

```powershell
.venv312\Scripts\python.exe -m adk_training.module_24_audit_ops.cli `
    --url https://staging.acme.test/admin `
    --allow-domain staging.acme.test `
    --cookie "session=abc123;domain=.staging.acme.test;path=/" `
    --header "X-Audit-Run: true" `
    --fail-on high
```

## 5. Integracja CI — JUnit + wiki lint

```powershell
.venv312\Scripts\python.exe -m adk_training.module_24_audit_ops.cli `
    --url https://staging.acme.test/ `
    --allow-domain staging.acme.test `
    --fail-on high `
    --junit out\audit-junit.xml

# Następnie utrzymuj wiki w czystości:
.venv312\Scripts\python.exe -m adk_training.module_24_audit_ops.cli `
    wiki-lint --report-dir .\artifacts --json
```

Obie komendy zwracają `0` na sukces, non-zero na błąd — Twoje narzędzie CI
zajmuje się resztą.

## 6. Ack disclaimera programatycznie

```powershell
curl -X POST http://localhost:8080/api/audit/disclaimer/ack `
     -H "Content-Type: application/json" `
     -d '{ "user_id": "alice", "target_url": "https://staging.acme.test/", "statement": "Mam autoryzację do testowania tego endpointu." }'
```

Odpowiedź: `{"ack_id":"ack-..."}`. Użyj jako pole `ack_id` w
`/api/audit/start`.

## 7. Start audytu + streaming eventów

```powershell
curl -N -X POST http://localhost:8080/api/audit/start `
     -H "Content-Type: application/json" `
     -d '{
           "ack_id": "ack-...",
           "mode": "auto",
           "target_url": "https://staging.acme.test/"
         }'
```

Odpowiedź to `text/event-stream`. Przepuść przez `Select-String type`
aby śledzić run.

## 8. Diff dwóch runów

```powershell
curl "http://localhost:8080/api/audit/runs/diff?a=run-old&b=run-new&fmt=markdown"
```

## 9. Przeglądanie wiki przez API

```powershell
curl http://localhost:8080/api/audit/wiki                              # lista wszystkich targetów
curl http://localhost:8080/api/audit/wiki/staging.acme.test/index      # TOC
curl "http://localhost:8080/api/audit/wiki/staging.acme.test/file?path=findings/F-high-missing-csp.md"
curl http://localhost:8080/api/audit/wiki/staging.acme.test/lint       # lista issue w JSON
```

## 10. Autorstwo własnego skilla

Utwórz katalog i SKILL.md:

```powershell
mkdir adk_training\module_24_audit_ops\skills\owasp-a04-insecure-design
@"
---
name: owasp-a04-insecure-design
description: Wykrywa flaws logiki biznesowej i brakujące rate-limity.
triggers:
  - forms
  - auth
---

# OWASP A04 — Insecure Design

Kiedy recon pokazuje formularz logowania, preferuj scenariusze, które:
- spróbują 30 prób hasła pod rząd, by wykryć brak rate-limita;
- spróbują reset hasła z maila innego użytkownika, by wykryć przewidywalne tokeny.
"@ | Out-File adk_training\module_24_audit_ops\skills\owasp-a04-insecure-design\SKILL.md
```

Następnie zweryfikuj:

```powershell
.venv312\Scripts\python.exe -m pytest adk_training\module_24_audit_ops\tests\test_skills_loader.py -q
curl http://localhost:8080/api/audit/skills
```

Nowy skill powinien pojawić się w manifeście L1.

## 11. Programowe użycie z Pythona

```python
import asyncio
from pathlib import Path

from adk_training.module_24_audit_ops.config import AuditConfig
from adk_training.module_24_audit_ops.pentest_agent import auto_pentest
from adk_training.module_24_audit_ops.safety import DisclaimerAck
from adk_training.module_24_audit_ops import wiki

cfg = AuditConfig(
    allowed_domains=["staging.acme.test"],
    artifacts_dir=Path("./artifacts"),
)

ack = DisclaimerAck(
    acknowledged=True,
    user_id="alice",
    target_url="https://staging.acme.test/",
    timestamp=0,
    statement="Mam autoryzację do testowania tego endpointu.",
)

audit = asyncio.run(auto_pentest(
    "https://staging.acme.test/", cfg, ack=ack))

wiki.record_run(cfg.artifacts_dir, audit.to_dict())
print(wiki.lint_wiki(cfg.artifacts_dir, audit.target_url))
```

## 12. Synthesis raportu kwartalnego (HITL)

```powershell
# Krok 1 — sam preview
curl -X POST http://localhost:8080/api/audit/wiki/synthesize `
     -H "Content-Type: application/json" `
     -d '{ "slug": "staging.acme.test", "question": "Jakie jest nasze największe ryzyko regresji?", "accept": false }'

# Krok 2 — przejrzyj preview, następnie wyślij ponownie z accept=true, aby zapersystować
curl -X POST http://localhost:8080/api/audit/wiki/synthesize `
     -H "Content-Type: application/json" `
     -d '{ "slug": "staging.acme.test", "question": "Jakie jest nasze największe ryzyko regresji?", "accept": true }'
```

Output trafia do `artifacts\wiki\staging.acme.test\synthesis\<UTC_TIMESTAMP>.md`.

# EXAMPLES — module_24_audit_ops

Quick recipes for the common workflows. The same content is rendered with
nicer navigation in the MkDocs site (`mkdocs serve`).

## 1. First CLI run

```powershell
.venv312\Scripts\python.exe -m adk_training.module_24_audit_ops.cli `
    --url https://staging.acme.test/ `
    --allow-domain staging.acme.test `
    --fail-on high `
    --report-dir .\artifacts
```

Produces `artifacts\<run_id>\report.md` + per-target wiki under
`artifacts\wiki\staging.acme.test\`.

## 2. Guided run with NL scenario

```powershell
.venv312\Scripts\python.exe -m adk_training.module_24_audit_ops.cli `
    --url https://staging.acme.test/login `
    --allow-domain staging.acme.test `
    --mode guided `
    --scenario-nl "Test the login form for SQL error fingerprints with a quoted payload." `
    --fail-on high
```

## 3. Authenticated scan

```powershell
.venv312\Scripts\python.exe -m adk_training.module_24_audit_ops.cli `
    --url https://staging.acme.test/admin `
    --allow-domain staging.acme.test `
    --cookie "session=abc123;domain=.staging.acme.test;path=/" `
    --header "X-Audit-Run: true" `
    --fail-on high
```

## 4. CI mode — JUnit + wiki lint

```powershell
.venv312\Scripts\python.exe -m adk_training.module_24_audit_ops.cli `
    --url https://staging.acme.test/ `
    --allow-domain staging.acme.test `
    --fail-on high `
    --junit out\audit-junit.xml

.venv312\Scripts\python.exe -m adk_training.module_24_audit_ops.cli `
    wiki-lint --report-dir .\artifacts --json
```

## 5. Disclaimer ack via REST

```powershell
curl -X POST http://localhost:8080/api/audit/disclaimer/ack `
     -H "Content-Type: application/json" `
     -d '{ "user_id": "alice", "target_url": "https://staging.acme.test/", "statement": "I am authorized to test this endpoint." }'
```

## 6. Start an audit + stream SSE

```powershell
curl -N -X POST http://localhost:8080/api/audit/start `
     -H "Content-Type: application/json" `
     -d '{
           "ack_id": "ack-...",
           "mode": "auto",
           "target_url": "https://staging.acme.test/"
         }'
```

## 7. Browse skills via REST

```powershell
curl http://localhost:8080/api/audit/skills
curl http://localhost:8080/api/audit/skills/owasp-a01-access-control
curl "http://localhost:8080/api/audit/skills/owasp-a01-access-control/resource?path=idor-templates.md"
```

## 8. Browse the wiki via REST

```powershell
curl http://localhost:8080/api/audit/wiki
curl http://localhost:8080/api/audit/wiki/staging.acme.test/index
curl "http://localhost:8080/api/audit/wiki/staging.acme.test/file?path=findings/F-high-missing-csp.md"
curl http://localhost:8080/api/audit/wiki/staging.acme.test/lint
```

## 9. Synthesize (HITL-gated)

```powershell
# preview
curl -X POST http://localhost:8080/api/audit/wiki/synthesize `
     -H "Content-Type: application/json" `
     -d '{ "slug": "staging.acme.test", "question": "Top regressions this quarter?", "accept": false }'

# persist after human review
curl -X POST http://localhost:8080/api/audit/wiki/synthesize `
     -H "Content-Type: application/json" `
     -d '{ "slug": "staging.acme.test", "question": "Top regressions this quarter?", "accept": true }'
```

## 10. Author a new skill

```powershell
mkdir adk_training\module_24_audit_ops\skills\owasp-a04-insecure-design
@"
---
name: owasp-a04-insecure-design
description: Spot business-logic flaws and missing rate-limits.
triggers:
  - forms
  - auth
---

# OWASP A04 — Insecure Design

Prefer scenarios that detect missing rate-limits or predictable tokens.
"@ | Out-File adk_training\module_24_audit_ops\skills\owasp-a04-insecure-design\SKILL.md
```

Verify:

```powershell
.venv312\Scripts\python.exe -m pytest adk_training\module_24_audit_ops\tests\test_skills_loader.py -q
```

## 11. Programmatic Python use

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
    statement="I am authorized to test this endpoint.",
)

audit = asyncio.run(auto_pentest(
    "https://staging.acme.test/", cfg, ack=ack))

wiki.record_run(cfg.artifacts_dir, audit.to_dict())
print(wiki.lint_wiki(cfg.artifacts_dir, audit.target_url))
```

## 12. Diff two runs

```powershell
curl "http://localhost:8080/api/audit/runs/diff?a=run-old&b=run-new&fmt=markdown"
```

## 13. Run the test suite

```powershell
.venv312\Scripts\python.exe -m pytest adk_training\module_24_audit_ops\tests -q
```

Expect `124 passed`.

## 14. Serve the docs

```powershell
.venv312\Scripts\python.exe -m pip install mkdocs-material
.venv312\Scripts\python.exe -m mkdocs serve `
    -f adk_training\module_24_audit_ops\mkdocs.yml
```

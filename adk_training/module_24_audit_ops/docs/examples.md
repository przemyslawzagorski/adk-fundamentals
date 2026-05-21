# Concrete Examples

Every example below is copy-paste runnable. PowerShell paths assume the
repo root `c:\Users\NBPZAGORSKI\IdeaProjects\adk-fundamentals`.

> See also: `EXAMPLES.md` at the module root for the same recipes outside MkDocs.

## 1. First run on a brand-new target

```powershell
.venv312\Scripts\python.exe -m adk_training.module_24_audit_ops.cli `
    --url https://staging.acme.test/ `
    --allow-domain staging.acme.test `
    --fail-on high `
    --report-dir .\artifacts
```

Result:

- `artifacts\<run_id>\report.md` + `report.json`
- `artifacts\wiki\staging.acme.test\index.md` (created)
- `artifacts\wiki\staging.acme.test\runs\<run_id>.md`
- One finding entity page per finding emitted.

## 2. Second run — see the audit-history skill kick in

Run the same command. Behind the scenes:

1. `wiki.history_skill_text` returns a non-empty body.
2. `_build_history_skill` wraps it as a synthetic skill named `audit-history`.
3. `render_planner_context` includes that body in the planner prompt.

You can verify by hitting the API:

```powershell
curl http://localhost:8080/api/audit/wiki/staging.acme.test/index
```

## 3. Guided run — natural-language scenario

```powershell
.venv312\Scripts\python.exe -m adk_training.module_24_audit_ops.cli `
    --url https://staging.acme.test/login `
    --allow-domain staging.acme.test `
    --mode guided `
    --scenario-nl "Try a login with ' OR 1=1-- and report whether SQL error fingerprints leak in the response." `
    --fail-on high
```

The skills loader injects `owasp-a03-injection` (POST form) and
`recon-helpers`. The LLM gets the SQLi error fingerprint reference content
ready to use.

## 4. Authenticated scan

```powershell
.venv312\Scripts\python.exe -m adk_training.module_24_audit_ops.cli `
    --url https://staging.acme.test/admin `
    --allow-domain staging.acme.test `
    --cookie "session=abc123;domain=.staging.acme.test;path=/" `
    --header "X-Audit-Run: true" `
    --fail-on high
```

## 5. CI integration — JUnit + wiki lint

```powershell
.venv312\Scripts\python.exe -m adk_training.module_24_audit_ops.cli `
    --url https://staging.acme.test/ `
    --allow-domain staging.acme.test `
    --fail-on high `
    --junit out\audit-junit.xml

# Then keep the wiki tidy:
.venv312\Scripts\python.exe -m adk_training.module_24_audit_ops.cli `
    wiki-lint --report-dir .\artifacts --json
```

Both commands return `0` on success, non-zero on failure — your CI tool
handles the rest.

## 6. Ack a disclaimer programmatically

```powershell
curl -X POST http://localhost:8080/api/audit/disclaimer/ack `
     -H "Content-Type: application/json" `
     -d '{ "user_id": "alice", "target_url": "https://staging.acme.test/", "statement": "I am authorized to test this endpoint." }'
```

Response: `{"ack_id":"ack-..."}`. Use it as the `ack_id` field on
`/api/audit/start`.

## 7. Start an audit + stream events

```powershell
curl -N -X POST http://localhost:8080/api/audit/start `
     -H "Content-Type: application/json" `
     -d '{
           "ack_id": "ack-...",
           "mode": "auto",
           "target_url": "https://staging.acme.test/"
         }'
```

The response is a `text/event-stream`. Pipe it through `Select-String type`
to follow the run.

## 8. Diff two runs

```powershell
curl "http://localhost:8080/api/audit/runs/diff?a=run-old&b=run-new&fmt=markdown"
```

## 9. Browse the wiki via API

```powershell
curl http://localhost:8080/api/audit/wiki                              # list all targets
curl http://localhost:8080/api/audit/wiki/staging.acme.test/index      # TOC
curl "http://localhost:8080/api/audit/wiki/staging.acme.test/file?path=findings/F-high-missing-csp.md"
curl http://localhost:8080/api/audit/wiki/staging.acme.test/lint       # JSON list of issues
```

## 10. Author a custom skill

Create the directory and SKILL.md:

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

When the recon shows a login form, prefer scenarios that:
- attempt 30 password tries in a row to detect missing rate-limit;
- attempt password reset from another user's email to detect predictable tokens.
"@ | Out-File adk_training\module_24_audit_ops\skills\owasp-a04-insecure-design\SKILL.md
```

Then verify:

```powershell
.venv312\Scripts\python.exe -m pytest adk_training\module_24_audit_ops\tests\test_skills_loader.py -q
curl http://localhost:8080/api/audit/skills
```

The new skill should appear in the L1 manifest.

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

## 12. Synthesize a quarterly report (HITL)

```powershell
# Step 1 — preview only
curl -X POST http://localhost:8080/api/audit/wiki/synthesize `
     -H "Content-Type: application/json" `
     -d '{ "slug": "staging.acme.test", "question": "What is our top regression risk?", "accept": false }'

# Step 2 — review the preview text, then re-submit with accept=true to persist
curl -X POST http://localhost:8080/api/audit/wiki/synthesize `
     -H "Content-Type: application/json" `
     -d '{ "slug": "staging.acme.test", "question": "What is our top regression risk?", "accept": true }'
```

Output goes to `artifacts\wiki\staging.acme.test\synthesis\<UTC_TIMESTAMP>.md`.

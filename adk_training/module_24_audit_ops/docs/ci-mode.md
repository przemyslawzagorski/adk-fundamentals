# CI Mode — `auditops` CLI

The CLI is a thin wrapper on the FastAPI orchestrator that:

- skips the disclaimer UI (CLI invocation is treated as implicit ack),
- writes Markdown + JSON reports to `--report-dir`,
- updates the per-target wiki,
- optionally emits JUnit XML for your CI report viewer,
- exits 0 / 1 / 2 with conventional semantics.

## Quickstart

```powershell
.venv312\Scripts\python.exe -m adk_training.module_24_audit_ops.cli `
    --url https://staging.acme.test/login `
    --allow-domain staging.acme.test `
    --fail-on high `
    --junit out/junit.xml `
    --report-dir out
```

## All flags

```text
auditops --url URL [--mode auto|guided] [--scenario-nl "..."]
         [--allow-domain DOMAIN ...] [--fail-on info|low|medium|high|critical]
         [--report-dir DIR] [--cookie "name=value;domain=.x.com" ...]
         [--header "Name: value" ...] [--junit FILE] [--user-id ID]
```

| Flag | Meaning |
|------|---------|
| `--url` | Target URL. Must match an entry in `--allow-domain`. |
| `--mode` | `auto` (default — uses the deterministic attack library) or `guided` (LLM translates `--scenario-nl`). |
| `--scenario-nl` | Required when `--mode guided`. Free text describing what to test. |
| `--allow-domain` | Allow-list (repeatable). Without this, the runtime guard refuses to start. |
| `--fail-on` | Severity threshold. `high` (default) means any high or critical finding fails the build. |
| `--report-dir` | Where to write artifacts. Sets `AUDITOPS_ARTIFACTS_DIR`. |
| `--cookie` / `--header` | Authenticated scans. Repeatable. |
| `--junit` | Write a JUnit XML file (one `<testcase>` per scenario). |

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Run completed; no findings at or above `--fail-on`. |
| 1 | Run completed; at least one finding ≥ `--fail-on`. |
| 2 | Configuration error (bad flags, missing allow-list, invalid auth spec). |
| 130 | Interrupted (Ctrl-C). |

## `auditops wiki-lint`

A separate subcommand for CI to keep the wiki tidy:

```powershell
.venv312\Scripts\python.exe -m adk_training.module_24_audit_ops.cli wiki-lint `
    --report-dir .\artifacts `
    --json
```

| Flag | Meaning |
|------|---------|
| `--report-dir` | Override `AUDITOPS_ARTIFACTS_DIR`. |
| `--target` | Limit lint to one target (slug like `acme.test` or full URL). |
| `--json` | Emit machine-readable JSON instead of the human report. |

Exit 0 = clean, 1 = at least one issue.

## CI pipeline example (Azure DevOps)

```yaml
- task: UsePythonVersion@0
  inputs: { versionSpec: '3.12' }

- script: |
    pip install -r requirements.txt
  displayName: install

- script: |
    python -m adk_training.module_24_audit_ops.cli `
      --url $(STAGING_URL) `
      --allow-domain $(STAGING_DOMAIN) `
      --fail-on high `
      --junit $(Build.ArtifactStagingDirectory)/junit.xml `
      --report-dir $(Build.ArtifactStagingDirectory)/audit
  displayName: AuditOps scan

- task: PublishTestResults@2
  inputs:
    testResultsFormat: JUnit
    testResultsFiles: '$(Build.ArtifactStagingDirectory)/junit.xml'
  condition: always()

- script: |
    python -m adk_training.module_24_audit_ops.cli wiki-lint `
      --report-dir $(Build.ArtifactStagingDirectory)/audit
  displayName: Wiki lint
```

## Environment variables

| Variable | Purpose |
|----------|---------|
| `AUDITOPS_ALLOWED_DOMAINS` | Comma-separated allow-list (alternative to `--allow-domain`). |
| `AUDITOPS_ARTIFACTS_DIR` | Where to write reports + wiki. |
| `AUDITOPS_REQUIRE_DISCLAIMER` | `1` (UI flow) / `0` (CLI implicit). The CLI sets `0` automatically. |
| `ANTHROPIC_API_KEY` | Forwarded to `module_23_auggie_integration` for the planner LLM. |

# Module 24 — AuditOps (Web Pentest Agent)

> **Authorized targets only.** This module performs *active* security testing.
> You **must** have explicit written authorization from the system owner.
> The included disclaimer flow is enforced by default; do not disable it on
> production targets.

## What this is

A small but real penetration-testing co-pilot that combines:

- **Recon** — `httpx` passive profiling (security headers, forms, tech stack, exposed paths).
- **Plan** — either a built-in OWASP scenario pack (Mode A) or LLM-translated NL scenario (Mode B).
- **Execute** — `Playwright` async with **video recording**, HAR, screenshots and a tiny declarative DSL.
- **Report** — Markdown + JSON + per-finding evidence + risk score (0–100).

It plugs into the existing **Module 23** Concierge UI as a new `/audit` tab.

## Architecture

```
┌──────────────────┐   recon (httpx)
│  pentest_agent   │──────────────┐
│ (orchestrator)   │              ▼
└────┬─────────────┘    ┌──────────────────┐
     │ plan             │      recon       │
     ▼                  └──────────────────┘
┌──────────────────┐    ┌──────────────────┐
│  attack_library  │ or │   LLM (Auggie)   │  ← Mode B
│ (OWASP defaults) │    │  NL → DSL JSON   │
└────┬─────────────┘    └──────────────────┘
     ▼
┌──────────────────┐  video / HAR / screenshots
│ playwright_runner│ ─────────────────────────► artifacts/<run_id>/
└────┬─────────────┘
     ▼
┌──────────────────┐
│     reporter     │ → report.md + report.json
└──────────────────┘
```

The pipeline is intentionally a linear async flow that mirrors an ADK
`SequentialAgent`. Each phase is a pure async function so it can be wrapped in
an `LlmAgent.run()` if/when you want full ADK orchestration, but it does not
require ADK at runtime.

## Files

| File | Purpose |
|------|---------|
| `config.py` | `AuditConfig` env-driven settings (allowlist, rate limit, paths) |
| `safety.py` | `SafetyError`, `DisclaimerAck`, token-bucket `RateLimiter`, `runtime_guard` |
| `recon.py` | `passive_recon()` — httpx fingerprint + path probing |
| `attack_library.py` | Built-in OWASP scenario pack (DSL JSON) |
| `playwright_runner.py` | `run_scenario()` — executes DSL with video + screenshots |
| `pentest_agent.py` | `auto_pentest()` (Mode A) and `guided_pentest()` (Mode B) |
| `reporter.py` | Markdown/JSON renderer, severity scoring |
| `api.py` | FastAPI router mounted under `/api/audit` |

## Install

```powershell
# repo root, with .venv312 activated
pip install -r adk_training\module_24_audit_ops\requirements.txt
playwright install chromium
```

## Environment variables

| Variable | Default | Notes |
|----------|---------|-------|
| `AUDITOPS_ALLOWED_DOMAINS` | *(empty)* | CSV list. Empty = allow all (do NOT use in prod). |
| `AUDITOPS_REQUIRE_DISCLAIMER` | `1` | Set to `0` only in CI/sandbox. |
| `AUDITOPS_RATE_LIMIT_RPS` | `1.0` | Global rate limit across all browser actions. |
| `AUDITOPS_HEADLESS` | `1` | Set to `0` to watch the browser locally. |
| `AUDITOPS_RECORD_VIDEO` | `1` | WebM video per scenario in `artifacts/`. |
| `AUDITOPS_BROWSER` | `chromium` | `chromium` / `firefox` / `webkit`. |
| `AUDITOPS_MAX_SCENARIOS` | `8` | Hard cap on default pack. |
| `AUDITOPS_MAX_STEPS_PER_SCENARIO` | `20` | Hard cap per scenario. |
| `AUDITOPS_TOTAL_BUDGET_SECONDS` | `600` | Wall-clock cap per run. |
| `AUDITOPS_ARTIFACTS_DIR` | `module_24_audit_ops/artifacts` | Where videos/HAR/reports go. |
| `AUDITOPS_LLM_MODEL` | `claude-sonnet-4-5` | Auggie model tag for Mode B. |

## Run

```powershell
# from repo root, after activating .venv312
$env:AUDITOPS_ALLOWED_DOMAINS = "example.com,localhost"
python -m adk_training.module_23_auggie_integration.web.app
```

Then open <http://localhost:8770/audit> (or the Vite dev server on `:5173`).

Mode A (Auto-Pentest) needs no LLM; Mode B uses Auggie via the same factory as
Module 23 (`auggie_run`), so the same env (`AUGGIE_USE_CLI`, etc.) applies.

## API

| Method | Path | Description |
|--------|------|-------------|
| `GET`  | `/api/audit/config` | Safe view of runtime config (allowlist, playwright). |
| `POST` | `/api/audit/disclaimer/ack` | `{target_url, user_id, accepted}` → `{token}`. |
| `POST` | `/api/audit/start` | SSE stream. Body `{url, mode, scenario_nl?, ack_token?}`. |
| `GET`  | `/api/audit/runs` | Recent runs from `artifacts/`. |
| `GET`  | `/api/audit/runs/{run_id}` | Full audit JSON. |
| `GET`  | `/api/audit/artifact/{run_id}/{path}` | Artifact passthrough (video, screenshot, report.md). |

Static artifacts are also mounted at `/artifacts/<run_id>/...` for easy embedding.

## Safety

- **Disclaimer enforced** — `runtime_guard()` raises `SafetyError` if no ack.
- **Domain allowlist** — hostname suffix match against `AUDITOPS_ALLOWED_DOMAINS`.
- **Rate limited** — token-bucket gate before every browser action.
- **Read-mostly defaults** — built-in pack does not perform credential stuffing,
  brute force, SQLi destructive payloads or DoS. XSS uses a **non-executing canary** detected by string match.
- **Path traversal blocked** in artifact handler.

## OWASP coverage (built-in pack)

| Scenario | OWASP |
|----------|-------|
| `smoke_navigation` | (meta) |
| `headers_baseline` | A05 — Security Misconfiguration |
| `cookie_flags` | A05 — Security Misconfiguration |
| `clickjacking` | A05 — Security Misconfiguration |
| `exposed_files` | A05/A06 |
| `open_redirect` | A01 — Broken Access Control |
| `xss_reflected` | A03 — Injection |

Mode B can produce arbitrary scenarios within the same DSL; the LLM is
restricted to the verbs documented in `pentest_agent._DSL_REFERENCE`.

## Roadmap

- AuthN scenarios (login bruteforce **with** rate-limit detection only).
- IDOR probes between two known sessions.
- Trace.zip viewer integration.
- Per-finding remediation hints from a small RAG corpus.

## Tests

```powershell
& .\.venv312\Scripts\python.exe -m pytest adk_training/module_24_audit_ops/tests -q
```

**94 unit tests** cover: env-driven config, safety guards (disclaimer /
allowlist / rate limiter), the SQLite ack store (persistence + TTL), the auth
vault (secret redaction), strict DSL validation, all attack-library scenario
factories (including the four new ones — CORS, SQLi sniff, mixed content,
sensitive storage), the LLM scenario parser (rejects unknown actions), run‑to‑run
diff classification, the CI runner (exit codes + JUnit + cookie parsing),
reporter, and the full FastAPI surface (config, disclaimer, auth, compare, junit).

The Playwright executor itself is not unit‑tested (would require a real browser
+ a fixture HTTP server). See `CRITICAL_REVIEW.md` for the gap analysis.

## Auth context (for pages behind a login)

Register cookies / extra headers / HTTP Basic once, then reference by id:

```bash
# 1) Register
curl -X POST http://localhost:8000/api/audit/auth -H 'Content-Type: application/json' -d '{
  "label": "staging",
  "cookies": [{"name":"sid","value":"...","domain":".staging.acme.test","secure":true,"httpOnly":true}],
  "headers": {"Authorization":"Bearer ..."}
}'
# -> { "id": "abc...", ... }

# 2) Use
curl -X POST http://localhost:8000/api/audit/start -H 'Content-Type: application/json' -d '{
  "url":"https://staging.acme.test/admin",
  "ack_token":"...",
  "auth_id":"abc..."
}'
```

Secrets stay server‑side: they never appear in run JSON, SSE events, or report
markdown. `GET /api/audit/auth` returns only fingerprints (cookie *names* and
header *names*, not values).

## Run‑to‑run diff (regression security)

```
GET /api/audit/compare?a=<baseline_run_id>&b=<current_run_id>
GET /api/audit/compare?a=<a>&b=<b>&fmt=markdown
```

Findings are classified into `new` / `fixed` / `unchanged` using a normalized
identity (scenario id + severity + numeric‑normalized title) so cosmetic drift
("Found 3 issues" → "Found 5 issues") is not flagged. Scenario‑level pass/fail
transitions (`regressed` / `recovered`) are reported separately.

This is the wedge that makes AuditOps something Burp/ZAP/Nuclei don't do well.

## CI mode (headless, exit‑code‑driven)

```powershell
& .\.venv312\Scripts\python.exe -m adk_training.module_24_audit_ops.cli `
  --url https://staging.acme.test `
  --allow-domain acme.test `
  --fail-on high `
  --report-dir ./audit_artifacts `
  --junit ./audit_artifacts/junit.xml `
  --cookie "sid=ABC;domain=.staging.acme.test"
```

Exit codes: `0` no findings ≥ threshold, `1` threshold exceeded, `2` config
error. The JUnit XML drops directly into GitLab/Jenkins/GitHub test reporters.

You can also fetch JUnit for any prior run:

```
GET /api/audit/runs/{run_id}/junit?fail_on=high
```

## OWASP scenario coverage

| Scenario | OWASP | Mode |
|---|---|---|
| `smoke_navigation`     | (meta)                              | passive |
| `security_headers`     | A05 — Security Misconfiguration     | passive |
| `cookie_flags`         | A05 — Security Misconfiguration     | passive |
| `clickjacking`         | A05 — Security Misconfiguration     | passive |
| `exposed_files`        | A05 / A06                           | passive |
| `open_redirect`        | A01 — Broken Access Control         | active  |
| `xss_reflected`        | A03 — Injection                     | active  |
| `cors_misconfig`       | A05 — Security Misconfiguration     | passive |
| `sqli_sniff`           | A03 — Injection (error‑string only) | active  |
| `mixed_content`        | A02 — Cryptographic Failures        | passive |
| `sensitive_storage`    | A02 — Cryptographic Failures        | passive |

## Critical review

For an honest assessment of bugs found, residual risks, and commercial
potential, see [CRITICAL_REVIEW.md](./CRITICAL_REVIEW.md).

# Stakeholder Overview

This page is written for product owners, security leads, and engineering
managers who need to decide whether AuditOps belongs in the company's
toolchain. **No code required.**

## The pitch in one paragraph

AuditOps gives a security engineer the ability to say _"go test the new login
page on `staging.acme.test` for OWASP Top 10 issues"_ in plain English and get
back a reproducible, auditable Markdown report with a CI-friendly exit code.
Every run feeds an institutional memory wiki, so the second run on the same
target is informed by the first — without anyone manually copy-pasting
findings into a Confluence page.

## What AuditOps is _not_

| It is not | Because |
|---|---|
| A replacement for a human pentester | Adversarial creativity is not in scope. |
| A scanner you run against arbitrary URLs | Allow-list is enforced. |
| A vulnerability database | Findings link to OWASP, not CVE. |
| A WAF or runtime defence tool | It generates reports, not blocks traffic. |

## Day-1 value

- **Security regression tests in CI**: Same way unit tests catch broken code,
  AuditOps catches when someone removes the CSP header from a deploy. The
  `--fail-on high` flag breaks the build on regressions.
- **Documented evidence**: Every run produces a Markdown + JSON report that
  can be attached to Jira tickets and PR reviews.
- **Reduced "did we already test this?" thrash**: The per-target wiki shows
  every prior run, every prior finding, and how often each one has been seen.

## Day-30 value

- **Compounding insight**: After a few weeks, the audit wiki has a
  battle-tested catalogue of how the application *actually* fails — which
  is more valuable than a generic OWASP checklist.
- **LLM gets smarter per target, not in general**: We do not train any model.
  The "audit-history" skill (V3) is just the wiki summarized into the planner
  prompt. Memory lives on disk in markdown — it can be backed up, audited,
  diff'd, even reviewed by a human before reuse (HITL).

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| LLM tries to test out-of-scope target | Allow-list domain enforced by `safety.runtime_guard`. |
| LLM goes off-script with destructive payloads | DSL only allows curated actions (see `dsl.ALLOWED_ACTIONS`). |
| Operator forgets they are running an active scan | Per-user disclaimer ack required, persisted in sqlite. |
| Wiki gets out of sync / corrupted | Python (not the LLM) writes the wiki. `auditops wiki-lint` runs in CI. |
| LLM hallucinates findings | Findings are produced only by Playwright-asserted DSL steps; LLM only translates the *plan*. |
| Cost runs away | Rate limiter caps runs per user per hour. |

## What we promise

1. The LLM never edits report files, wiki index, log, or finding pages.
2. Run artefacts (`runs/<id>.md`, `report.md`, `report.json`) are immutable.
3. Wiki updates are idempotent — running a finished audit through the
   recorder twice does not duplicate occurrences.
4. The CLI returns non-zero when the configured severity threshold is met,
   which is what your CI pipeline already understands.

## What we do not promise

1. Coverage of OWASP categories beyond A01, A02, A03, and A05 (others rely on
   recon-only heuristics).
2. Authenticated scans for arbitrary auth flows beyond cookie + header
   injection (OAuth, OIDC, SAML need extra plumbing).
3. Comparable behaviour across Playwright browser versions.

## Compliance notes

- All runs require an explicit `DisclaimerAck` recording user id, target URL,
  timestamp, and a free-text statement. The ack store is a sqlite file —
  your auditors can grep it.
- Reports are local files; nothing is uploaded anywhere by default.
- The LLM call goes to whichever provider `module_23_auggie_integration`
  is configured for (default: Anthropic). Disable network egress in CI if
  you need air-gapped operation.

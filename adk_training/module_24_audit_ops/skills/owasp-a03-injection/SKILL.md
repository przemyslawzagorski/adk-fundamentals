---
name: owasp-a03-injection
description: Injection — SQLi sniff, reflected XSS detection. Triggers when POST forms exist. Single-quote sniff only — never destructive payloads.
triggers: [injection, forms]
---
# OWASP A03:2021 — Injection

This skill is **detection-only**. We never attempt destructive payloads
(no `OR 1=1`, no `; DROP`, no time-based blind). The DSL `expect_no_sql_error`
action looks for engine error fingerprints in the response body — that is
sufficient for a black-box smoke test, and the operator can escalate to a
specialist tool if the sniff trips.

## What to test

1. **SQLi sniff** — submit a single quote into a recon-discovered text input
   and assert no SQL-engine error string appears
   (see `references/sqli-error-fingerprints.md`).
2. **Reflected XSS smoke** — submit `aud1tops_xss_probe` (a literal benign
   token) and `expect_text` it back in the next page. If reflected, emit a
   medium finding; if not, no false-positive.

## What NOT to do

- Do not chain payloads. One submission per scenario.
- Do not target login forms with this — credential prompts are out of scope
  (A01 covers that separately).
- Do not encode the payload (no `%27`, no double encoding) — recon-supplied
  inputs accept literal characters; encoding noise pollutes evidence.

## DSL skeleton

See `attack_library.scenario_sqli_sniff()`. Keep `severity: medium` even on a
positive sniff — it is a *signal*, not a proof of exploitable injection.

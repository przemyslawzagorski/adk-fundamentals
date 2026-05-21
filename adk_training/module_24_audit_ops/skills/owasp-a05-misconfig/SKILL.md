---
name: owasp-a05-misconfig
description: Security misconfiguration — CORS, missing security headers, default error pages. Triggers when CSP/headers missing.
triggers: [misconfig, missing:content-security-policy, missing:x-frame-options]
---
# OWASP A05:2021 — Security Misconfiguration

Almost everything in this category is **passive** — header presence, CORS
preflight, leaked tech versions. That is exactly what `expect_header` and
`expect_cors_open` are for.

## What to test

1. **CORS too permissive** — bundled `expect_cors_open` action sends a
   preflight `OPTIONS` from a synthetic origin and reports if
   `Access-Control-Allow-Origin: *` is reflected together with
   `Access-Control-Allow-Credentials: true`. Severity: `high` (auth +
   wildcard origin).

2. **Missing security headers** — `Content-Security-Policy`,
   `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`.
   Use `expect_header` per header. Keep these as separate findings; the
   report aggregates them.

3. **Server banner leak** — `Server: nginx/1.18.0` is informational, never
   emit higher than `info`. Operators need this to plan upgrades, not as a
   blocking finding.

## What NOT to do

- Do not probe `/.git/HEAD` or `/.env` without explicit operator request — the
  safety guard rejects most of these and a CI run failing on path-traversal
  noise is annoying.
- Do not chase "server header missing" findings; absence of a banner is a
  hardening *win*, not a finding.

## Severity guidance

| Symptom                                            | Severity |
|----------------------------------------------------|----------|
| `ACAO: *` with `ACAC: true`                        | high     |
| `Content-Security-Policy` missing                  | medium   |
| `X-Frame-Options` missing                          | low      |
| `Server` banner discloses minor version            | info     |

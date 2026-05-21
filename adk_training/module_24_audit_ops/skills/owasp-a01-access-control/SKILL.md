---
name: owasp-a01-access-control
description: Broken access control — authn/authz scenarios (IDOR, missing auth, session fixation). Triggers when forms with passwords or auth headers exist.
triggers: [forms, auth, access-control]
---
# OWASP A01:2021 — Broken Access Control

Use this skill when the target exposes login forms, authenticated endpoints,
or session cookies. Otherwise skip — A01 probes against an unauthenticated
landing page produce noise, not findings.

## What to test

1. **Missing authentication** on private-looking paths
   (`/admin`, `/dashboard`, `/api/users`). Probe with `goto` + `expect_status`
   for 200 (bad) vs 401/403 (good). See `references/idor-templates.md`.

2. **Session fixation / weak session cookies** — the `recon.cookies` block
   tells you if `Secure`/`HttpOnly` are set. Use `expect_header` on
   `Set-Cookie` only on a fresh login flow; otherwise leave to manual audit.

3. **CSRF on state-changing forms** — if the recon shows POST forms and no
   `csrf-token` input, emit a `note` finding rather than a click flow
   (we are not authorized to mutate state in a black-box scan).

## What NOT to do

- Do not attempt brute-force or credential-stuffing — out of scope, see
  `safety.runtime_guard`.
- Do not click "delete" / "logout" / "submit" buttons in production targets;
  the safety guard rejects this anyway.
- Do not invent IDs (`/api/users/42`) without recon evidence — emit a `note`
  finding hinting at IDOR rather than fabricating a probe.

## Severity guidance

| Symptom                                        | Severity |
|-----------------------------------------------|----------|
| Missing auth on documented private endpoint   | high     |
| `Secure` flag missing on session cookie       | medium   |
| `HttpOnly` flag missing on session cookie     | medium   |
| Suspected IDOR (no proof)                     | info     |

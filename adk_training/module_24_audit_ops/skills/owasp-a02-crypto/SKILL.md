---
name: owasp-a02-crypto
description: Cryptographic failures — TLS/HSTS, mixed content, sensitive data in storage. Triggers when crypto headers missing or HTTP scheme detected.
triggers: [crypto, missing:strict-transport-security]
---
# OWASP A02:2021 — Cryptographic Failures

Focus on **passive** evidence here: header presence, scheme, mixed-content
HTML, and what the page leaks into `localStorage` / `sessionStorage`.

## What to test

1. **HSTS missing** on HTTPS targets — `expect_header` for
   `Strict-Transport-Security`. Severity: `medium` if scheme is HTTPS,
   `high` if site appears to handle credentials.

2. **Mixed content** — page served over HTTPS but loads `http://...` resources.
   Use the bundled `expect_no_mixed_content` action; never roll your own regex
   walker.

3. **Sensitive data in client-side storage** — the `expect_storage_clean`
   action evaluates `localStorage` + `sessionStorage` and matches against a
   regex list. Default patterns (token, secret, jwt) live in
   `attack_library.scenario_sensitive_storage`. Do not invent your own
   credential regexes — false-positive risk is high.

## What NOT to do

- Do not run TLS-cipher probing through Playwright — wrong tool.
  Recommend `testssl.sh` in the report instead.
- Do not request known sensitive endpoints (`/.git`, `/.env`) without
  explicit user permission; safety guard rejects most of these.

## Severity guidance

| Symptom                                          | Severity |
|--------------------------------------------------|----------|
| HSTS missing, HTTPS site                         | medium   |
| Mixed-content `<script src="http://...">`        | high     |
| Mixed-content `<img>` only                       | low      |
| `localStorage` contains `token`/`jwt`/`secret`   | medium   |

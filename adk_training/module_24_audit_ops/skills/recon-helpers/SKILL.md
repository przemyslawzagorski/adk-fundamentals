---
name: recon-helpers
description: Heuristics for turning passive recon (headers, forms, tech) into useful planning hints. Always include when planning.
triggers: [baseline]
---
# Recon helpers

Use the recon summary to ground every scenario you plan. Concretely:

- If `security_headers` shows missing `Content-Security-Policy`, `X-Frame-Options`,
  `Strict-Transport-Security` or `Referrer-Policy`, prefer `expect_header` probes
  over click-flows — they are passive and cheap.
- If `forms` is empty, do **not** invent fake selectors (e.g. `[name="username"]`).
  Stick to passive header/CORS/storage probes.
- `final_url` is what the browser actually landed on after redirects. Use it as
  the `goto.url` in the first step rather than the original `target_url`.
- If `technologies` mentions `nginx`/`Apache`/etc., that hints at default error
  pages — combine with `expect_no_sql_error` only when a form actually exists.

## Selector hygiene

If you must interact with a form:

- prefer `[name="<input_name>"]` from the recon `forms[*].inputs[*].name`,
- prefer `[type="submit"]` for the submit button when the recon does not
  list a stable selector,
- never use index-based selectors like `:nth-child(3)` — they break on
  cosmetic re-orderings between runs.

## DSL hygiene

- Always start with a `goto` step.
- Always end with a `screenshot` step (the operator needs visible proof).
- Keep step counts ≤ 6 unless the scenario is genuinely multi-step.
- Severity for *missing-header* findings should be `low` unless the header is
  `Content-Security-Policy` (then `medium`).

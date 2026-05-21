# IDOR & missing-auth templates (DSL fragments)

These are copy-paste DSL skeletons. Adjust the URL and severity per recon.

## Probe a private-looking path for missing auth

```json
{
  "id": "missing_auth_admin",
  "name": "Admin path reachable without auth",
  "owasp": "A01:2021-Broken Access Control",
  "severity": "high",
  "passive": true,
  "steps": [
    {"action": "goto", "url": "{{TARGET}}/admin", "wait_until": "load"},
    {"action": "expect_status", "equals_any": [401, 403, 404],
      "fail_finding": {
        "title": "Admin page reachable without authentication",
        "severity": "high"
      }},
    {"action": "screenshot", "name": "admin_probe"}
  ]
}
```

## CSRF advisory (note-only — no mutation)

```json
{
  "id": "csrf_advisory",
  "name": "POST form lacks CSRF token",
  "owasp": "A01:2021-Broken Access Control",
  "severity": "info",
  "passive": true,
  "steps": [
    {"action": "goto", "url": "{{FORM_URL}}", "wait_until": "load"},
    {"action": "note", "message": "Form action accepts POST and contains no csrf-token / authenticity-token input — manual review recommended."},
    {"action": "screenshot", "name": "csrf_advisory"}
  ]
}
```

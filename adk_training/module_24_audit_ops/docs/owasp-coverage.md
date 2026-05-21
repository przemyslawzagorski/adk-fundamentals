# OWASP Top 10 (2021) — Coverage Matrix

| OWASP Category | Skill bundled? | Recon-detected? | Notes |
|----------------|----------------|-----------------|-------|
| **A01 — Broken Access Control** | ✅ `owasp-a01-access-control` | login forms detected | IDOR / missing-auth / CSRF templates in `references/idor-templates.md`. |
| **A02 — Cryptographic Failures** | ✅ `owasp-a02-crypto` | HSTS missing → triggered | Mixed-content + sensitive-storage guidance. |
| **A03 — Injection** | ✅ `owasp-a03-injection` | POST/PUT/PATCH forms → triggered | SQLi error fingerprints in `references/sqli-error-fingerprints.md`. |
| **A04 — Insecure Design** | ⚠️ heuristic only | n/a | Belongs to attack_library; LLM uses generic prompt guidance. |
| **A05 — Security Misconfiguration** | ✅ `owasp-a05-misconfig` | CSP/X-Frame/etc. missing → triggered | Severity table for missing headers. |
| **A06 — Vulnerable Components** | ❌ | technologies recon | Surfaces tech stack; CVE matching is out of scope. |
| **A07 — Identification & Auth Failures** | ⚠️ folded into A01 | login forms detected | Covered through access-control + injection skills. |
| **A08 — Software & Data Integrity** | ❌ | n/a | Out of scope (CI/CD pipeline integrity). |
| **A09 — Logging & Monitoring** | ❌ | n/a | Out of scope (target-side logging). |
| **A10 — SSRF** | ❌ | n/a | Roadmap. |

## Why partial coverage is honest

An LLM-driven web pentester cannot meaningfully test A08 (CI/CD pipeline
integrity) or A09 (target-side logging) without privileged access to the
target's deployment infrastructure. We surface what passive HTTP recon +
declarative DSL execution can confirm; everything else is explicitly
labelled out-of-scope.

## How to add a new category

See [Skills Pack](skills-pack.md#how-to-author-a-new-skill).

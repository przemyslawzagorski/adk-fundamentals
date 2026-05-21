# AuditOps Report — `https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f`

- **Run ID:** `1777469436_4d14920e`
- **Duration:** 5.6s
- **Risk score:** **0.0/100**

## Severity breakdown
| Severity | Count |
|----------|-------|

## Target profile
- **Final URL:** https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- **Status:** 200
- **Server:** `github.com`
- **Technologies:** (none detected)
- **Forms:** 32
- **Missing security headers:** Permissions-Policy, Cross-Origin-Opener-Policy

## Findings
> ✅ No security findings detected. (This does NOT mean the target is secure — only that built-in probes did not trigger.)

## Scenarios executed
- ❌ **Smoke navigation** (info) — 0.84s 
  - error: `runner failed: `
- ❌ **Security headers baseline** (medium) — 0.01s 
  - error: `runner failed: `
- ❌ **Cookie security flags** (medium) — 0.01s 
  - error: `runner failed: `
- ❌ **Clickjacking via missing X-Frame-Options / frame-ancestors** (low) — 0.02s 
  - error: `runner failed: `
- ❌ **Exposed sensitive files** (high) — 0.02s 
  - error: `runner failed: `
- ❌ **Open redirect probe** (medium) — 0.05s 
  - error: `runner failed: `
- ❌ **Reflected XSS canary in detected forms** (high) — 0.06s 
  - error: `runner failed: `
- ❌ **CORS misconfiguration probe** (high) — 0.03s 
  - error: `runner failed: `

---
*AuditOps — module_24, prototype. Use only on authorized targets.*
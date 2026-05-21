# AuditOps Report — `https://pypi.org/project/auggie-sdk/`

- **Run ID:** `1777150913_00de8e30`
- **Duration:** 89.4s
- **Risk score:** **46.2/100**

## Severity breakdown
| Severity | Count |
|----------|-------|
| 🟧 HIGH | 1 |
| 🟨 MEDIUM | 1 |
| 🟦 LOW | 2 |

## Target profile
- **Final URL:** https://pypi.org/project/auggie-sdk/
- **Status:** 200
- **Server:** `gunicorn`
- **Technologies:** (none detected)
- **Forms:** 3
- **Missing security headers:** Cross-Origin-Opener-Policy

## Findings

### 1. Sensitive path exposed: /.well-known/security.txt — 🟧 HIGH
- **Scenario:** `exposed_files`
- **OWASP:** A05:2021-Security Misconfiguration
- **Evidence:**
  ```json
  {
    "url": "https://pypi.org/.well-known/security.txt",
    "status": 200
  }
  ```

### 2. Missing Content-Security-Policy — 🟨 MEDIUM
- **Scenario:** `headers_baseline`
- **OWASP:** A05:2021-Security Misconfiguration
- **Evidence:**
  ```json
  {
    "header": "Content-Security-Policy",
    "present": false
  }
  ```

### 3. Missing X-Frame-Options (clickjacking risk) — 🟦 LOW
- **Scenario:** `headers_baseline`
- **OWASP:** A05:2021-Security Misconfiguration
- **Evidence:**
  ```json
  {
    "header": "X-Frame-Options",
    "present": false
  }
  ```

### 4. Page can be framed (clickjacking risk) — 🟦 LOW
- **Scenario:** `clickjacking`
- **OWASP:** A05:2021-Security Misconfiguration
- **Evidence:**
  ```json
  {
    "x-frame-options": "",
    "csp_has_fa": false
  }
  ```

## Scenarios executed
- ✅ **Smoke navigation** (info) — 6.44s · [video](/artifacts/1777150913_00de8e30/smoke_navigation/video/3c0200784eae2a6fd685c6f5d0c26f6a.webm)
- ❌ **Security headers baseline** (medium) — 10.66s · [video](/artifacts/1777150913_00de8e30/headers_baseline/video/e7c2681101b2793ed8284847eaf67edb.webm)
- ✅ **Cookie security flags** (medium) — 5.39s · [video](/artifacts/1777150913_00de8e30/cookie_flags/video/7c4d8b6691b96a602afba677f8a30022.webm)
- ❌ **Clickjacking via missing X-Frame-Options / frame-ancestors** (low) — 7.82s · [video](/artifacts/1777150913_00de8e30/clickjacking/video/64c4481730462bee8f7499b3169dd4d7.webm)
- ❌ **Exposed sensitive files** (high) — 7.27s · [video](/artifacts/1777150913_00de8e30/exposed_files/video/b8b264279035cab82432985118751d53.webm)
- ✅ **Open redirect probe** (medium) — 10.38s · [video](/artifacts/1777150913_00de8e30/open_redirect/video/9b56d4090d9f116a7001d627d7940351.webm)
- ✅ **Reflected XSS canary in detected forms** (high) — 32.92s · [video](/artifacts/1777150913_00de8e30/xss_reflected/video/419d00861f9e771beeeab90c44ae2112.webm)
- ✅ **CORS misconfiguration probe** (high) — 6.95s · [video](/artifacts/1777150913_00de8e30/cors_misconfig/video/dc258f2754fd6242a82aa62052842687.webm)

---
*AuditOps — module_24, prototype. Use only on authorized targets.*
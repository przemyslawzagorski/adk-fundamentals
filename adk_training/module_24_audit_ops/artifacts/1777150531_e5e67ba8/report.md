# AuditOps Report — `https://pypi.org/project/auggie-sdk/`

- **Run ID:** `1777150531_e5e67ba8`
- **Duration:** 61.5s
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
- **Server:** ``
- **Technologies:** (none detected)
- **Forms:** 0
- **Missing security headers:** Content-Security-Policy, Referrer-Policy, Cross-Origin-Opener-Policy
- **Notes:**
  - No CSP — XSS impact will be higher.
  - Cookies without Secure flag: _fs_ch_st_FSBmUei20MqUiJb9

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
- ✅ **Smoke navigation** (info) — 16.56s · [video](/artifacts/1777150531_e5e67ba8/smoke_navigation/video/79a7e1e62bbe47a6ed5feb52cd355758.webm)
- ❌ **Security headers baseline** (medium) — 9.29s · [video](/artifacts/1777150531_e5e67ba8/headers_baseline/video/29f32ac47dffbbdf0f412f9c11056d75.webm)
- ✅ **Cookie security flags** (medium) — 4.79s · [video](/artifacts/1777150531_e5e67ba8/cookie_flags/video/1dad73a490cd386a539a383bb6760248.webm)
- ❌ **Clickjacking via missing X-Frame-Options / frame-ancestors** (low) — 4.86s · [video](/artifacts/1777150531_e5e67ba8/clickjacking/video/be82b172595c7b99f1d2ee997a88fbbc.webm)
- ❌ **Exposed sensitive files** (high) — 4.88s · [video](/artifacts/1777150531_e5e67ba8/exposed_files/video/18f4a3d8ded25535c92d94fd41e20a79.webm)
- ✅ **Open redirect probe** (medium) — 8.03s · [video](/artifacts/1777150531_e5e67ba8/open_redirect/video/0667e517d04ece0df1a8af759755132c.webm)
- ✅ **Reflected XSS probe (skipped — no forms)** (info) — 5.18s · [video](/artifacts/1777150531_e5e67ba8/xss_reflected/video/46e93afe0ebd627da6fd06b7c35b7240.webm)
- ✅ **CORS misconfiguration probe** (high) — 6.02s · [video](/artifacts/1777150531_e5e67ba8/cors_misconfig/video/bd5065cb685e1063c3902688516f5a47.webm)

---
*AuditOps — module_24, prototype. Use only on authorized targets.*
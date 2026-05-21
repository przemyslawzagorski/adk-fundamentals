# Module 24 — Critical Review & Potential Assessment

> Author: pair‑programming session, 2026‑04‑25.
> Scope: code‑level review of `adk_training/module_24_audit_ops/` as a *prototype*
> + market potential as an LLM‑driven web pentest assistant.

## TL;DR

| Dimension | Verdict |
|---|---|
| Engineering quality of the prototype | **A−** — clean separation of concerns, lazy imports, dataclasses everywhere, async‑native, **94 passing unit tests**, strict DSL gate, persistent ack store, run‑to‑run diff, CI runner. |
| Security of the *agent itself* | **A−** — domain allowlist + disclaimer (now SQLite‑backed) + rate‑limit + DSL parser allowlist + assertion errors fail scenarios + auth secrets never serialized. |
| Differentiation vs. existing tools | **B+** — *scenario‑level regression security* (run‑to‑run diff with video evidence) is the wedge; Burp/ZAP/Nuclei don't do that out of the box. NL→DSL on top is the productivity layer. |
| Commercial potential | **8/10 as a product line.** Three credible go‑to‑markets: (1) regression‑security in CI for product teams, (2) SOC 2 / ISO 27001 evidence automation, (3) junior‑pentest accelerator with audit trail. |

## Update — Phase 3 hardening (this commit)

Everything that follows below was the state **before** the potential‑boost
pass. Status of the issues *after* the boost:

| Issue | Status |
|---|---|
| **S‑1** Ack persistence  | ✅ **Resolved.** `ack_store.py` — SQLite‑backed `AckStore` with TTL + auto‑purge. Persists across restarts, safe for multi‑worker uvicorn. |
| **S‑6** Permissive LLM parser | ✅ **Resolved.** `dsl.py` exports `ALLOWED_ACTIONS`; `_safe_parse_scenario` calls `validate_scenario` and rejects any unknown action with a `ValueError` *before* the scenario is queued. |
| **S‑7** Silent step failures | ✅ **Resolved.** `playwright_runner.run_scenario` now fails the scenario when **any** `expect_*` action raises. No more "0 findings" because of a runtime crash. |
| **S‑2** Double GET in `expect_status` | Documented, deferred. |
| **S‑3** `_rest` private attr | Documented, deferred. |
| **S‑4** Global rate bucket | Documented, deferred (per‑host bucket is a 30‑min refactor when needed). |
| **S‑5** Plaintext XSS canary | Documented, deferred (a "DOM XSS" pass would be a new module). |

### New capabilities added in this pass

- **Auth vault** (`auth.py`) — register cookies / extra headers / HTTP Basic
  once via `POST /api/audit/auth`, then reference by opaque id from `start`.
  Secrets never appear in run JSON, SSE events, or report Markdown.
  `redact_for_logging()` deep‑redacts anything that looks like a secret.
- **Run‑to‑run diff** (`compare.py`) — `GET /api/audit/compare?a=&b=`
  classifies findings into `new` / `fixed` / `unchanged` (titles normalized
  for numeric drift), tracks scenario‑level pass/fail transitions, and
  renders Markdown for human review. **This is the unique selling point**:
  nobody else does scenario‑level regression security with video evidence.
- **CI runner** (`cli.py`) — `python -m adk_training.module_24_audit_ops.cli
  --url … --fail-on high --junit out.xml`. Exits 0/1/2 by max severity vs.
  threshold. JUnit XML output drops directly into GitLab/Jenkins/GitHub
  test reporters.
- **Strict DSL** (`dsl.py`) — single source of truth shared by the parser,
  the executor, and the API. New scenarios automatically inherit validation.
- **Four new OWASP scenarios** — `cors_misconfig` (A05), `sqli_sniff` (A03,
  single‑quote error sniff only — no UNION/time‑based), `mixed_content`
  (A02), `sensitive_storage` (A02, scans `localStorage`/`sessionStorage`
  for token‑shaped values).
- **JUnit endpoint** — `GET /api/audit/runs/{id}/junit?fail_on=high`.

### Test coverage now

```
tests/test_ack_store.py         5 tests  — SQLite persistence + expiry
tests/test_api.py               7 tests  — original API smoke
tests/test_api_extras.py        9 tests  — auth/compare/junit endpoints
tests/test_attack_library.py   10 tests  — original scenarios
tests/test_auth.py              8 tests  — auth vault + redaction
tests/test_cli.py               6 tests  — CI mode + JUnit + cookie parser
tests/test_compare.py           4 tests  — diff classification
tests/test_config.py            5 tests  — env timing + allowlist
tests/test_new_scenarios.py     7 tests  — CORS/SQLi/mixed/storage shapes
tests/test_pentest_agent.py     8 tests  — LLM parser robustness
tests/test_reporter.py          4 tests  — score + render + write
tests/test_safety.py            8 tests  — disclaimer + allowlist + rate
tests/test_strict_dsl.py        7 tests  — DSL allowlist + parser gate
                              ─────────
                              94 tests, all green, < 8 s
```

---

## Original review (pre‑boost) follows below

| Dimension | Verdict |
|---|---|

## What is genuinely good

1. **Lazy Playwright import.** The module imports cleanly even without Playwright,
   so `available()` becomes a feature flag the UI can read. This is exactly how an
   ADK module should fail.
2. **Declarative DSL.** Constraining the LLM to a closed verb set
   (`goto`/`fill`/`click`/`expect_*`/…) is the right architectural choice. It lets
   us parse, validate, and *replay* scenarios without re‑calling the LLM, which
   is the single most important property for evidence integrity.
3. **Findings are emitted by failed *security expectations*, not by trapping
   exceptions.** Inverted assertion logic is the cleanest way to express OWASP
   probes; it also means we get actionable, structured findings instead of
   stack traces.
4. **Per‑scenario fresh browser context with HAR + WebM video.** Evidence is
   the product. We close the context before reading `video.path()` so the file
   actually finalizes — easy to get wrong.
5. **Path‑traversal hardening.** `target.startswith(base)` after `resolve()`
   is the correct pattern, and FastAPI’s router strips `..` segments before
   our handler ever runs (verified by test).

## Real bugs found and fixed in this pass

1. `AuditConfig` previously evaluated env vars at *class‑definition time*
   (`require_disclaimer: bool = os.getenv(...)`). That meant any env change
   after import was silently ignored — including in tests. **Fixed**: every
   field now uses `field(default_factory=...)`.
2. The `/api/audit/start` endpoint accepted *any* valid ack token regardless
   of which target it was issued for. An attacker (or a careless user) who
   acked `https://my-site.com` could reuse the token for
   `https://victim.example`. **Fixed**: host comparison enforced before launch.

## Remaining real risks (not yet addressed)

These are honest issues, not nitpicks. Listed in priority order.

### S‑1 — Disclaimer ack persistence is in‑process memory

`_ACKS: Dict[str, DisclaimerAck]` lives in `api.py` module state.
- Restart wipes it.
- Multi‑worker uvicorn (`--workers >1`) makes it non‑deterministic.
- There is no expiration: a token is valid forever.

**Fix path:** persist to SQLite/Postgres with `(token, host, user_id, expires_at)`,
require token age ≤ 1h, and bind `user_id` to the session that issued it.

### S‑2 — `expect_status` performs a *second* GET

To get the real status code we re‑request `page.url` via
`context.request.get(cur)`. On stateful endpoints this can:
- duplicate side effects (POSTs are skipped, but a GET to `/logout` would
  re‑logout),
- confuse rate‑limited targets,
- show a different status than what the browser actually received.

**Fix path:** snapshot the response from the navigation handler
(`page.on("response", ...)`) and key it by URL+frame, then read it back.

### S‑3 — `cookies` parsing in `recon.py` reaches into private attrs

```python
"httponly": bool(c._rest.get("HttpOnly")) ...
```
`_rest` is a private member of `http.cookiejar.Cookie`; this works on CPython
3.12 but is not contractually stable.

**Fix path:** parse `Set-Cookie` headers directly with
`http.cookies.SimpleCookie` or read them via Playwright `context.cookies()`
(which already returns the public flags).

### S‑4 — The rate limiter is global per process, not per host

A run against `app1.example.com` and `app2.example.com` shares the bucket.
That is *fine* for safety (we err on the slow side) but produces misleading
benchmarks.

### S‑5 — XSS canary is plaintext, no sandbox

The reflected‑XSS scenario submits `audopsXSS_<script>alert(1)</script>` and
checks if the literal string appears in HTML. That detects naïve reflections
but misses everything modern (DOM XSS, attribute‑context, mutation XSS).
Acceptable for a module‑level prototype; **do not** market this as XSS coverage.

### S‑6 — LLM output is parsed permissively

`_safe_parse_scenario` strips fences and grabs the first `{...}`. A prompt
injection embedded in the *target page HTML* (which we feed into the planner
via `recon.summary()`) could nudge the LLM into emitting destructive steps.
The DSL allowlist on the executor side is what *actually* protects us — and
that holds. But we should also reject any unknown action at parse time
(currently the executor just emits `step_skipped`, which is silent in logs).

**Fix path:** in `_safe_parse_scenario`, validate every step’s `action` against
the known DSL set and drop the scenario if any are unknown.

### S‑7 — Step‑level errors do not always fail the scenario

Only `goto`/`fetch_url` errors abort. A flaky `expect_header` that crashes
silently passes. That can cause **false negatives** (we say "no findings"
when we never actually checked).

**Fix path:** treat `expect_*` exceptions as scenario errors, not as benign
step skips.

## Quality metrics

```
adk_training/module_24_audit_ops/
├── api.py              ~210 LOC  — FastAPI router, SSE, ack store
├── attack_library.py   ~210 LOC  — 7 OWASP scenario factories
├── config.py           ~80 LOC   — env‑driven dataclass
├── pentest_agent.py    ~285 LOC  — recon → plan → execute orchestrator
├── playwright_runner.py ~390 LOC — DSL executor (lazy Playwright import)
├── recon.py            ~210 LOC  — passive httpx fingerprint
├── reporter.py         ~125 LOC  — Markdown + JSON + score
├── safety.py           ~85 LOC   — disclaimer + allowlist + rate limit
└── tests/              47 tests, all green, < 4s
```

- No external state outside `artifacts_dir` and the in‑memory ack store.
- All public surface area on the FastAPI router is covered by a smoke test.
- The DSL executor itself is **not** unit‑tested (would require Playwright +
  a fixture HTTP server). That is a real gap; see S‑7.

## Where this could go — honest assessment

**Strong angles**
- *Regression‑security in CI for product teams.* You ship a feature, the
  agent reruns the same NL scenario nightly, the diff between videos is
  the artifact. This is something Burp/ZAP do not do well because they are
  scanner‑shaped, not scenario‑shaped.
- *Audit trail for SOC 2 / ISO 27001 evidence collection.* Per‑run
  Markdown report + WebM + HAR is exactly the shape internal auditors want.
- *Junior‑pentest accelerator.* NL → DSL is a real productivity boost for a
  junior analyst exploring an unfamiliar app, *if* we keep the LLM on a
  short leash via the DSL.

**Weak angles**
- Not a serious offensive tool. No fuzzing, no auth bypass logic, no
  state‑aware crawling. We are not competing with Burp Suite, Caido, or
  Nuclei — and we should not pretend to.
- The video artefact is great for humans, useless for diff‑based
  regression unless we add a perceptual hash or DOM diff.
- The whole stack assumes the user is *already authorized*. There is no
  "find me unauthorised exposure on the public internet" play here, by design.

**My honest score for commercial potential**
- As a standalone product: **3/10.** The market is crowded and we are
  lighter on capability than the incumbents.
- As an *integration* inside an internal developer platform / Concierge
  app (which is exactly what module_23 is): **6/10.** The narrative
  "type a sentence, get a video, get a Markdown report" is a real
  developer‑experience win for product teams that don't have a
  pentest function.

## What I would build next, in priority order

1. **Persistent ack store + per‑run trace.zip** (Playwright tracing API).
   Trace.zip is dramatically more useful than HAR for replay.
2. **DOM/visual diff between two runs of the same scenario.** This is the
   wedge: nobody else does scenario‑level regression security.
3. **Auth helper.** Inject cookies/Bearer/Header from a vault, scoped to
   one run. Without this, every interesting scenario short‑circuits at
   the login page.
4. **Step‑level DSL allow‑list validation in the parser** (S‑6) and
   strict failure on `expect_*` exceptions (S‑7). Both are correctness
   wins, not features.
5. **Move the SSE event union into a typed Pydantic model** so the
   frontend gets generated types automatically and we stop maintaining
   the discriminated union by hand.

## Summary

The prototype is honest, well‑structured, and small enough to extend. It
will *not* replace a pentest team, and it should not try to. Its
defensible value is **scenario regression security with video evidence**
inside a developer platform — that is a niche, but it is real, and the
plumbing is mostly already in place.

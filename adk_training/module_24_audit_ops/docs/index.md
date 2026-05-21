<div class="auditops-hero" markdown>

<div class="badges">
  <span class="badge">module_24</span>
  <span class="badge">OWASP Top 10 (2021)</span>
  <span class="badge">124 tests · ~8s</span>
  <span class="badge">CI ready</span>
</div>

# AuditOps

<p class="tagline">
LLM-driven web pentest platform z deterministycznymi guardrails, raportami przyjaznymi dla
decydentów i pamięcią instytucjonalną, która rośnie z każdym audytem.
</p>

<a href="stakeholder-overview/" class="cta">📊 Dla decydentów →</a>
<a href="architecture/" class="cta secondary">🏗 Architektura</a>
<a href="../patterns/" class="cta secondary">🧩 Platform patterns</a>
<a href="../features-catalog/" class="cta secondary">⚙️ All features</a>

</div>

!!! info "Część większej platformy"
    AuditOps to jeden z dwóch produktów platformy.
    [Platform Patterns](../patterns/index.md) pokazuje jak przenieść skille i wiki
    do innych modułów; [Features Catalog](../features-catalog.md) listuje wszystkie
    funkcje (Concierge web, MCP, ACP, cache, cost tracking, resilience, AuditOps).

<div class="auditops-grid" markdown>

<div class="card" markdown>
<span class="ico">🧠</span>
### Progressive-disclosure Skills (V1)
Planner widzi tylko skill potrzebny do bieżącego recon-u — A01/A02/A03/A05 + recon-helpers.
Zero vector-store, jeden plik na skill.
</div>

<div class="card" markdown>
<span class="ico">📚</span>
### Audit Wiki (V2)
Per-target Markdown wiki, deterministycznie pisana przez Pythona. Każde finding ląduje
w pamięci instytucjonalnej i jest dostępne dla kolejnego runu.
</div>

<div class="card" markdown>
<span class="ico">🔁</span>
### Audit-History Skill (V3)
Wiki streszczone do plannera: "CSP missing potwierdzone 3×, nie odkrywaj od zera".
Deduplikacja efortu w prawdziwym czasie.
</div>

<div class="card" markdown>
<span class="ico">🛡️</span>
### Safety net
Disclaimer ack, allow-listed domains, runtime guard, rate-limit, passive-recon-first.
Tylko autoryzowane targety.
</div>

<div class="card" markdown>
<span class="ico">🎬</span>
### Video evidence
Każdy krok scenariusza w Playwright — wideo, screenshoty, request log. Reproducible
bug reports zamiast "trust me bro".
</div>

<div class="card" markdown>
<span class="ico">⚙️</span>
### CI native
`auditops` CLI breakuje pipeline przy severity ≥ HIGH. Wiki-lint blokuje merge przy
broken_link albo missing_run_stub.
</div>

</div>

# AuditOps — `module_24_audit_ops`

> **LLM-driven web application security testing**, with deterministic guardrails,
> a stakeholder-friendly reporting story, and an institutional memory that
> grows with every run.

AuditOps is the production-ready capstone of the ADK training: it takes the
naïve "let the agent click around your site" demo and hardens it into a tool
that an actual security team — or a CI pipeline — can trust to operate against
authorized targets.

## TL;DR for stakeholders

- **What it does**: Runs an LLM-planned, Playwright-executed offensive-security
  test against a single authorized target and produces a Markdown + JSON
  report scored against the OWASP Top 10 (2021). Failures break the CI build.
- **What stops it from doing harm**: A multi-layer safety net — explicit
  per-user disclaimer ack, allow-listed domains, runtime guard, rate limiter,
  passive-recon-before-active-probes — and an exhaustive audit log.
- **What makes it smart**: Progressive-disclosure **skills pack** (V1) gives
  the planner only the knowledge it needs for the recon at hand, plus a
  per-target **audit wiki** (V2) that turns every finding into searchable
  institutional memory, plus an automatic **audit-history skill** (V3) that
  tells the planner "you already found CSP missing twice — confirm or refute,
  don't re-discover".

## TL;DR for developers

```text
adk_training/module_24_audit_ops/
├── api.py                 ← FastAPI router, /api/audit/*
├── cli.py                 ← CI runner ("auditops ..." + "auditops wiki-lint")
├── pentest_agent.py       ← orchestrator: recon → plan → execute → report
├── skills_loader.py       ← V1: progressive-disclosure skills (L1/L2/L3)
├── wiki.py                ← V2: deterministic Python wiki writer + linter
├── skills/
│   ├── recon-helpers/SKILL.md
│   ├── owasp-a01-access-control/SKILL.md  + references/
│   ├── owasp-a02-crypto/SKILL.md
│   ├── owasp-a03-injection/SKILL.md       + references/
│   └── owasp-a05-misconfig/SKILL.md
├── tests/                 ← 124 unit + integration tests, ~8s wall
├── docs/                  ← this MkDocs site
└── EXAMPLES.md            ← copy-paste recipes for every workflow
```

Run the docs locally:

```powershell
.venv312\Scripts\python.exe -m pip install mkdocs-material
.venv312\Scripts\python.exe -m mkdocs serve -f adk_training\module_24_audit_ops\mkdocs.yml
```

Run the tests:

```powershell
.venv312\Scripts\python.exe -m pytest adk_training\module_24_audit_ops\tests -q
```

## Reading order

1. [Stakeholder Overview](stakeholder-overview.md) — non-technical brief.
2. [Architecture](architecture.md) — how recon → plan → execute → report fit
   together, plus the V1+V2+V3 wiring.
3. [Skills Pack](skills-pack.md) — why we copied the Karpathy LLM-Wiki and
   ADK Skills patterns instead of building a vector store.
4. [Audit Wiki](wiki-pattern.md) — the deterministic, idempotent
   institutional memory.
5. [Examples](examples.md) — concrete copy-paste workflows.

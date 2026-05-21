<div class="auditops-hero" markdown>

<div class="badges">
  <span class="badge">module_24</span>
  <span class="badge">OWASP Top 10 (2021)</span>
  <span class="badge">124 testy · ~8s</span>
  <span class="badge">Gotowe do CI</span>
</div>

# AuditOps

<p class="tagline">
Platforma audytu webowego sterowana LLM, z deterministycznymi guardrails, raportami
zrozumiałymi dla decydentów i pamięcią instytucjonalną rosnącą z każdym audytem.
</p>

<a href="stakeholder-overview/" class="cta">📊 Dla decydentów →</a>
<a href="architecture/" class="cta secondary">🏗 Architektura</a>

</div>

> **Web pentest sterowany LLM** z deterministycznymi guardrails, raportowaniem
> przyjaznym dla decydentów i pamięcią instytucjonalną, która rośnie z każdym
> kolejnym audytem.

AuditOps to capstone szkolenia ADK przeniesiony na poziom produkcyjny:
przekształca naiwne demo "niech agent klika po stronie" w narzędzie, któremu
realny zespół security — albo CI pipeline — może zaufać przy operowaniu na
autoryzowanych targetach.

## TL;DR dla decydentów

- **Co robi**: Uruchamia ofensywny test LLM-planowany i wykonywany przez
  Playwright na pojedynczym, autoryzowanym celu i produkuje raport
  Markdown + JSON oceniony pod kątem OWASP Top 10 (2021). Failures łamią
  build CI.
- **Co go zatrzymuje przed wyrządzeniem szkody**: Wielowarstwowy bezpiecznik
  — jawne potwierdzenie disclaimer per użytkownik, allowlista domen,
  runtime guard, rate-limiter, recon pasywny przed aktywnym sondowaniem —
  oraz wyczerpujący audit log.
- **Co czyni go inteligentnym**: Pakiet **skills z progresywnym ujawnianiem**
  (V1) daje plannerowi tylko wiedzę potrzebną do aktualnego reconu, plus
  per-target **wiki audytów** (V2), która zamienia każde finding
  w przeszukiwalną pamięć instytucjonalną, plus automatyczny
  **skill audit-history** (V3) który mówi plannerowi "znalazłeś już CSP
  missing dwukrotnie — potwierdź lub zaprzecz, nie odkrywaj od zera".

## TL;DR dla deweloperów

```text
adk_training/module_24_audit_ops/
├── api.py                 ← FastAPI router, /api/audit/*
├── cli.py                 ← runner CI ("auditops ..." + "auditops wiki-lint")
├── pentest_agent.py       ← orchestrator: recon → plan → execute → report
├── skills_loader.py       ← V1: skills z progresywnym ujawnianiem (L1/L2/L3)
├── wiki.py                ← V2: deterministyczny pythonowy writer wiki + lint
├── skills/
│   ├── recon-helpers/SKILL.md
│   ├── owasp-a01-access-control/SKILL.md  + references/
│   ├── owasp-a02-crypto/SKILL.md
│   ├── owasp-a03-injection/SKILL.md       + references/
│   └── owasp-a05-misconfig/SKILL.md
├── tests/                 ← 124 testów unit + integration, ~8s wall
├── docs/                  ← ten serwis MkDocs
└── EXAMPLES.md            ← gotowe recipes dla każdego workflow
```

Uruchom dokumentację lokalnie:

```powershell
.venv312\Scripts\python.exe -m pip install mkdocs-material
.venv312\Scripts\python.exe -m mkdocs serve -f adk_training\module_24_audit_ops\mkdocs.yml
```

Uruchom testy:

```powershell
.venv312\Scripts\python.exe -m pytest adk_training\module_24_audit_ops\tests -q
```

## Kolejność czytania

1. [Dla decydentów](stakeholder-overview.md) — brief nietechniczny.
2. [Architektura](architecture.md) — jak recon → plan → execute → report łączą
   się w jedną całość, plus wiring V1+V2+V3.
3. [Przykłady](examples.md) — konkretne workflowy do skopiowania.

> 📘 Pełna dokumentacja techniczna (Skills Pack, Wiki, OWASP Coverage,
> CI Mode, REST API, Security) dostępna jest w [wersji angielskiej](../index.md).

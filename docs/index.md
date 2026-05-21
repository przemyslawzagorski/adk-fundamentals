<div class="platform-hero" markdown>

<div class="badges">
  <span class="badge">ADK + Auggie</span>
  <span class="badge">Two-tier orchestration</span>
  <span class="badge">OWASP Top 10 audit guardrails</span>
  <span class="badge">CI ready</span>
</div>

# ADK Fundamentals — Platform

<p class="tagline">
Jeden produkt, dwie warstwy: <b>AI Code Concierge</b> kieruje ruchem (Gemini Flash — tani dispatcher),
<b>Auggie/Claude</b> robi ciężką robotę kodu i bezpieczeństwa, a <b>AuditOps</b> dorzuca skille,
audyt OWASP i pamięć instytucjonalną. Wszystko orkiestrowane przez Google ADK.
</p>

<a href="quick-start/" class="cta">⚡ Quick start</a>
<a href="architecture/" class="cta secondary">🏗 Architecture</a>
<a href="patterns/" class="cta secondary">🧩 Patterns</a>
<a href="features-catalog/" class="cta secondary">⚙️ Features</a>

</div>

## What's inside

<div class="product-grid" markdown>

<div class="product-card" markdown>
<span class="pill">module_23</span>
### 🤖 AI Code Concierge
Two-tier dispatcher: ADK Gemini routes intents → Auggie/Claude executes. Cache (LRU+TTL),
cost tracker (USD/tool), retry+circuit-breaker, ACP pool, MCP server, GitHub Action for PR review.

[Explore Concierge →](ai-code-concierge/index.md)
</div>

<div class="product-card" markdown>
<span class="pill">module_24</span>
### 🛡 AuditOps
LLM-driven web pentest with deterministic guardrails. Progressive-disclosure skills
(L1/L2/L3), per-target audit wiki, Playwright PoCs, OWASP Top 10 (2021) coverage,
124 tests in ~8s.

[Explore AuditOps →](AuditOps/index.md)
</div>

<div class="product-card" markdown>
<span class="pill">cross-cutting</span>
### 🧩 Reusable patterns
The skills, wiki, recon→trigger and progressive-disclosure ideas are **module-agnostic**.
This site documents how to drop them into module_13 (Code Analyst), module_22 (Spec Generator),
module_09 (DB agents) and beyond.

[See patterns →](patterns/)
</div>

</div>

## Two-tier orchestration in 30 seconds

```mermaid
flowchart LR
    U[User / IDE / CI] -->|prompt| C[ADK Gemini 2.5 Flash<br/>dispatcher]
    C -->|simple Q&A| C
    C -->|delegate| A[Auggie + Claude Sonnet 4.5<br/>workspace + tools]
    A --> CACHE[(LRU+TTL cache)]
    A --> COST[(Cost tracker USD)]
    A --> RES[Retry + circuit breaker]
    A -->|skill triggered| S[AuditOps skill<br/>L2 instructions]
    S --> W[(Per-target wiki)]
    A --> R[Result + audit trail]
```

You only pay the expensive specialist when you actually need it. Everything is observable
(`/api/cost`, `/api/telemetry`, `/api/health`) and deterministic where it matters.

## Reading order

1. [Quick start](quick-start.md) — uruchom backend + frontend + docs.
2. [Architecture](architecture.md) — schemat dwuwarstwowy, granice odpowiedzialności.
3. [Patterns](patterns/index.md) — co i jak przenieść do innych modułów.
4. [Features catalog](features-catalog.md) — pełna lista funkcji platformy.
5. [AI Code Concierge](ai-code-concierge/index.md) lub [AuditOps](AuditOps/index.md) — deep-dive.
6. [Decision guide](decision-guide.md) — kiedy Concierge, kiedy AuditOps, kiedy oba.

!!! tip "Polish & English"
    AuditOps ma pełne tłumaczenie 🇵🇱 w sekcji *AuditOps → Polski*.
    Concierge i strony platformowe są dwujęzyczne (PL w treści, EN w nagłówkach).

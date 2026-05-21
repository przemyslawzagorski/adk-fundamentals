# Decision guide

Kiedy używać czego — bez gadania.

## Wybór warstwy

```mermaid
flowchart TD
    Q[Co masz zrobić?] --> CL{Klasyfikacja /<br/>FAQ / krótka odp.}
    CL -- tak --> T1[Tier 1 — ADK Gemini Flash]
    CL -- nie --> CO{Edycja kodu /<br/>workspace search / refactor}
    CO -- tak --> T2[Tier 2 — Auggie + Claude]
    CO -- nie --> AU{Audyt web /<br/>OWASP / pentest}
    AU -- tak --> AOPS[AuditOps planner]
    AU -- nie --> CR{Cross-module<br/>(skills · wiki · disclosure)}
    CR -- tak --> P[Patterns — copy-paste z module_24]
    CR -- nie --> META[Otwórz issue, brak ścieżki]
```

## Macierz produktów

| Scenariusz | Concierge | AuditOps | Bezpośrednio Auggie |
|---|---|---|---|
| "Wygeneruj testy do `foo.py`" | ✅ ADK routuje do `RUN_AUGGIE` | — | opcjonalnie |
| "Czy ten kod ma OWASP A01?" | ❌ za drogie | ✅ skill `owasp-a01-access-control` | — |
| "Streszcz pliki w `module_07/`" | ✅ tier-1 wystarczy | — | — |
| "Pentest `https://staging.local`" | — | ✅ planner + Playwright | — |
| Ręczna debug-sesja Auggie | — | — | ✅ `auggie --print` |
| PR review w GitHub Action | ✅ `ci_review.py` | — | — |

## Macierz wzorców (do innych modułów)

| Wzorzec | Z czego | Dla kogo | Wysiłek |
|---|---|---|---|
| Progressive disclosure (skills L1/L2/L3) | `module_24/skills_loader.py` | `module_13` Code Analyst, `module_22` Spec Generator | XS (drop-in) |
| Per-target wiki (append-only) | `module_24/wiki.py` (już agnostyczny) | `module_09` DB agents (per-schema), `module_15` Gmail (per-thread) | S (zmiana `artifacts_dir`) |
| Recon → trigger → skill | `module_24/recon.py` + `skills_loader.recon_signals` | każdy moduł z fazą *probe* | M (mapowanie sygnałów) |
| MkDocs monorepo | ten plik (`mkdocs.yml` w roocie) | wszystkie moduły | XS (dodanie subordinate `mkdocs.yml`) |

Szczegóły: [Patterns / Progressive disclosure](patterns/progressive-disclosure.md),
[Audit wiki](patterns/audit-wiki.md), [Recon → skill](patterns/recon-to-skill.md),
[MkDocs monorepo](patterns/mkdocs-monorepo.md).

## Kiedy NIE używać Concierge

- **Real-time UI events** — to nie jest websocket bus, użyj dedykowanego serwera.
- **Multi-tenant SaaS** — auth jest dev-grade (single-user). Patrz `auth.py`.
- **Long-running jobs (> 5 min)** — circuit breaker wytnie. Użyj kolejki + worker.

## Kiedy NIE używać AuditOps

- **Czarna skrzynka bez allowlisty** — `safety.py` zablokuje. Dodaj host świadomie.
- **Audyt aplikacji innych niż HTTP** — Playwright runner zakłada przeglądarkę.
- **Compliance reporting (SOC2/PCI)** — to wsparcie inżynierskie, nie raport audytowy.

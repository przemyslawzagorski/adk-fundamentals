# Patterns

Reużywalne wzorce wyciągnięte z `module_24` i `module_23`. Każdy ma sekcję
*Co skopiować* + *Estymata* + *Anti-patterns*.

| Wzorzec | Estymata per moduł | Strona |
|---|---|---|
| Progressive disclosure (skille L1/L2/L3) | XS — drop-in `skills/*/SKILL.md` | [→](progressive-disclosure.md) |
| Per-target wiki (append-only, lint) | S — zmiana `artifacts_dir` | [→](audit-wiki.md) |
| Recon → trigger → skill | M — mapowanie sygnałów na triggery | [→](recon-to-skill.md) |
| MkDocs jako monorepo | XS — subordinate `mkdocs.yml` | [→](mkdocs-monorepo.md) |

## Wybór

```mermaid
flowchart LR
    Q{Twój moduł ma...} -->|wiele small system promptów<br/>do różnych sytuacji| PD[Progressive disclosure]
    Q -->|powtarzalny target<br/>(URL, schemat, użytkownik)| WIKI[Per-target wiki]
    Q -->|fazę probe →<br/>wybór scenariusza| RT[Recon → skill]
    Q -->|własne docs/<br/>do zaprezentowania| MD[MkDocs monorepo]
```

Wszystkie cztery są kompatybilne. Najmocniejszy efekt: użyj wszystkich w nowym module
(`module_25_xyz` jako szablon).

# MkDocs jako monorepo

Każdy moduł ma swoje `docs/` + lekkie `mkdocs.yml`. Root `mkdocs.yml` używa
[`mkdocs-monorepo-plugin`](https://github.com/backstage/mkdocs-monorepo-plugin)
i scala wszystko w jeden site. Jeden `mkdocs serve` na porcie 8765.

## Struktura

```text
mkdocs.yml                                       # ROOT — theme + plugins + nav
docs/                                             # platform-level
  index.md
  quick-start.md
  patterns/
adk_training/
  module_23_auggie_integration/
    mkdocs.yml                                   # subordinate (site_name + nav)
    docs/
      index.md
      architecture.md
      ...
  module_24_audit_ops/
    mkdocs.yml                                   # subordinate
    docs/
      index.md
      pl/
      ...
```

## Root `mkdocs.yml` (skrót)

```yaml
plugins:
  - search
  - monorepo

nav:
  - Home: index.md
  - Patterns: patterns/index.md
  - AI Code Concierge: '!include ./adk_training/module_23_auggie_integration/mkdocs.yml'
  - AuditOps:          '!include ./adk_training/module_24_audit_ops/mkdocs.yml'
```

## Subordinate `mkdocs.yml`

Tylko `site_name` + `nav`. **Brak** `theme`, `docs_dir`, `plugins` (dziedziczone z roota).

```yaml
site_name: AI Code Concierge
nav:
  - Home: index.md
  - Architecture: architecture.md
  - ...
```

## Jak dodać nowy moduł

1. Stwórz `adk_training/module_XX/docs/index.md`.
2. Stwórz `adk_training/module_XX/mkdocs.yml`:
    ```yaml
    site_name: Module XX — <name>
    nav:
      - Home: index.md
    ```
3. Dodaj do roota `mkdocs.yml`:
    ```yaml
    nav:
      - Module XX: '!include ./adk_training/module_XX/mkdocs.yml'
    ```
4. `mkdocs build --strict` — koniec.

Estymata: **~15 minut** per moduł (z napisaniem treści: pół dnia).

## Cross-linki

Wewnątrz subordinate możesz linkować do roota i innych subordinate przez ścieżkę
względną od `site_url` (po merge):

```markdown
Patrz [Patterns](../patterns/index.md) i [AuditOps skills](../AuditOps/skills-pack.md).
```

`mkdocs build --strict` zweryfikuje.

## Anti-patterns

- ❌ **`theme` w subordinate** — overrideuje root, nie nadpisuj.
- ❌ **`docs_dir: ../../something`** — łamie rebase plugin, trzymaj `docs/` lokalnie.
- ❌ **Strony PL i EN w jednym folderze bez prefiksu** — skończysz z konfliktem nazw,
  użyj `pl/` (jak module_24).

## Bonus: i18n bez pluginu

Drugi język = osobny folder `pl/` w subordinate `docs/`. Nawigacja roota wpina
go jako sekcję 🇵🇱. Jeśli kiedyś chcesz pełne i18n (URL `/pl/...`),
przejdź na `mkdocs-static-i18n` — kontrakt nawigacji nie zmienia się.

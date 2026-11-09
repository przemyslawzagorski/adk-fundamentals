---
name: changelog-generator
description: >
  Generowanie changelogów z historii commitów Git.
  Automatycznie analizuje commity, kategoryzuje zmiany
  (features, fixes, breaking changes, improvements),
  tłumaczy techniczny język na czytelny dla użytkowników.
  Używaj gdy pytanie dotyczy release notes, changelogów,
  dokumentowania zmian w projekcie lub przygotowania notatek do wydania.
  Źródło: awesome-claude-skills (ComposioHQ) — prawdziwy external skill.
---

# Changelog Generator

> Skill zaadaptowany z repozytorium
> [awesome-claude-skills](https://github.com/ComposioHQ/awesome-claude-skills/tree/master/changelog-generator)
> jako przykład **real external skill** w szkoleniu ADK.

## Kiedy używać tego skilla
- Przygotowanie release notes dla nowej wersji
- Tworzenie tygodniowych/miesięcznych podsumowań zmian
- Dokumentowanie zmian dla klientów/użytkowników
- Generowanie wpisów do app store (What's New)
- Utrzymanie pliku CHANGELOG.md

## Krok 1: Zbierz informacje o commitach
Zapytaj użytkownika o:
- Zakres: od/do (tagi, daty, branch)
- Format commitów (Conventional Commits? free-form?)
- Grupę docelową (deweloperzy? użytkownicy końcowi? stakeholders?)

## Krok 2: Kategoryzuj zmiany
Pogrupuj commity w sekcje:

| Prefix commita | Kategoria changeloga | Emoji |
|----------------|---------------------|-------|
| `feat:` | New Features | ✨ |
| `fix:` | Bug Fixes | 🐛 |
| `perf:` | Performance | ⚡ |
| `BREAKING CHANGE:` | Breaking Changes | 🚨 |
| `docs:` | Documentation | 📝 |
| `refactor:`, `chore:`, `test:`, `ci:` | Internal (ukryj domyślnie) | 🔧 |

## Krok 3: Przetłumacz na język użytkownika
Zasady:
1. **Zamieniaj technikalia na korzyści**: `fix: null pointer in UserService` → `Fixed crash when opening profile`
2. **Zaczynaj od czasownika**: Added, Fixed, Improved, Removed
3. **Konkretnie**: nie "Various improvements" ale "Search results now load 2x faster"
4. **Grupuj powiązane**: 5 commitów o search → 1 wpis "Completely redesigned search"

## Krok 4: Format wyjściowy
Załaduj `references/changelog-format.md` po szczegółowe szablony formatów
(Keep a Changelog, GitHub Releases, Slack announcement).

## Przykład

**Input** (commity):
```
feat: add team workspaces
feat: add keyboard shortcuts (? for help)
fix: large images fail to upload
fix: timezone bug in scheduled posts
perf: improve file sync speed 2x
refactor: extract search module
```

**Output** (changelog):
```markdown
# v2.5.0 — 2026-04-12

## ✨ New Features
- **Team Workspaces**: Twórz oddzielne przestrzenie dla różnych projektów,
  zapraszaj członków zespołu
- **Keyboard Shortcuts**: Naciśnij `?` aby zobaczyć wszystkie skróty

## ⚡ Improvements
- **Szybsza synchronizacja**: Pliki synchronizują się 2× szybciej

## 🐛 Bug Fixes
- Naprawiono problem z przesyłaniem dużych obrazów
- Naprawiono błąd stref czasowych w zaplanowanych postach
```

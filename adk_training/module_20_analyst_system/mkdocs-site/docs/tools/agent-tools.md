# Narzędzia agentów

## Przegląd

Narzędzia (tools) to funkcje Python automatycznie opakowywane przez ADK w `FunctionTool`. Agenci wywołują je jako narzędzia — ADK zarządza serializacją argumentów i wyniku.

---

## file_tools — operacje na plikach

Operacje wejścia/wyjścia dla generowanych dokumentów.

| Funkcja | Argumenty | Wynik | Zastosowanie |
|---------|----------|-------|-------------|
| `read_file` | `file_path: str` | `{status, content, path}` | Wczytanie istniejącego dokumentu |
| `write_document` | `file_name: str, content: str, subdirectory: str = ""` | `{status, path}` | Zapis wygenerowanego dokumentu |
| `list_files` | `directory: str = ".", pattern: str = "*"` | `{status, files, count}` | Lista plików w katalogu |

```python
# Przykład użycia przez agenta
result = read_file("docs/architecture.md")
# → {"status": "success", "content": "# Architecture\n...", "path": "docs/architecture.md"}
```

---

## template_tools — szablony dokumentów

Zarządzanie szablonami HLD, LLD, epiców i planów testów.

| Funkcja | Argumenty | Wynik | Zastosowanie |
|---------|----------|-------|-------------|
| `list_templates` | — | `{status, templates}` | Lista dostępnych szablonów |
| `load_template` | `template_name: str` | `{status, content}` | Wczytanie szablonu |

### Dostępne szablony

| Szablon | Plik | Sekcje |
|---------|------|--------|
| HLD | `hld_template.md` | Kontekst, założenia, architektura, komponenty, integracje |
| LLD | `lld_template.md` | Modele danych, API, sekwencje, testy, migracja |
| Epik | `epic_template.md` | User stories, acceptance criteria, definicja "done" |
| Plan testów | `test_plan_template.md` | Strategia, scenariusze, edge cases, środowiska |

!!! info "Szablony zawierają `[TODO:]` markery"
    Każdy szablon ma placeholder'y `[TODO: ...]` wskazujące agentom, co należy wygenerować. Agent zachowuje strukturę szablonu, wypełniając sekcje kontekstem projektu.

---

## skill_tools — zarządzanie umiejętnościami

Najrozbudowanszy zestaw narzędzi — zarządza repozytorium skilli zgodnym ze specyfikacją [agentskills.io](https://agentskills.io).

| Funkcja | Argumenty | Wynik | Zastosowanie |
|---------|----------|-------|-------------|
| `validate_skill_name` | `name: str` | `{valid, issues}` | Walidacja nazwy (lowercase-hyphen, max 50 znaków) |
| `list_skills` | — | `{status, skills, count}` | Lista skilli z metadanymi |
| `get_skill_metadata` | `skill_name: str` | `{status, metadata}` | Frontmatter skilla (YAML) |
| `read_skill` | `skill_name: str` | `{status, content, references, assets}` | Pełna treść + załączniki |
| `write_skill_draft` | `skill_name: str, skill_md_content: str, references: list = [], assets: list = []` | `{status, path}` | Zapis nowego skilla z załącznikami |

```python
# Walidacja nazwy skilla
validate_skill_name("graphql-naming")
# → {"valid": true, "issues": []}

validate_skill_name("GraphQL Naming!!")
# → {"valid": false, "issues": ["must use lowercase-hyphen", "no special chars"]}
```

### Format skilla (agentskills.io)

```yaml
---
name: diataxis-writing
version: "1.0"
description: "Write documentation following the Diátaxis framework"
globs:
  - "docs/**/*.md"
  - "**/*documentation*"
tags:
  - documentation
  - diataxis
  - writing
---

# Diátaxis Writing Skill

## Purpose
Apply the Diátaxis framework to all documentation...

## Rules
1. Classify every document into one of 4 types...
```

!!! warning "Limit rozmiaru"
    Specyfikacja agentskills.io ogranicza body skilla do **500 linii**. `skill_reviewer` w Knowledge Loop weryfikuje ten limit.

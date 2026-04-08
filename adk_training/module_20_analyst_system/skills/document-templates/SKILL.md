---
name: document-templates
description: >-
  Provide reusable document templates for HLD, LLD, epics, and test plans.
  Templates define required sections, structure, and content expectations.
  Use when creating a new document from scratch. Do not use for reviewing
  or editing existing documents.
metadata:
  author: manual
  version: "1.0"
  skill_type: template-pattern
compatibility:
  - augment
  - copilot
  - adk
---

# Document Templates

## When to use

- Starting a new HLD, LLD, epic, or test plan from scratch
- Need the canonical section structure for a document type
- Unsure what sections are required vs optional

## Available templates

Templates are in the `assets/` directory of this skill.

| Template | File | Use case |
|----------|------|----------|
| HLD | `hld_template.md` | High-Level Design document |
| LLD | `lld_template.md` | Low-Level Design / detailed design |
| Epic | `epic_template.md` | Jira Epic with user stories |
| Test Plan | `test_plan_template.md` | Test plan with scenarios |

## How to use templates

1. Load the template using `load_template(template_name)`
2. Fill in all sections marked with `[TODO: ...]`
3. Remove optional sections that don't apply
4. Add project-specific sections as needed

## Template conventions

- `[TODO: ...]` — must be replaced with actual content
- `[OPTIONAL]` — section can be removed if not applicable
- `[CONDITIONAL: ...]` — include only when condition applies
- Section comments describe what content goes there

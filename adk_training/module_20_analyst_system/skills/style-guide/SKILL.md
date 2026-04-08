---
name: style-guide
description: >-
  Apply enterprise documentation style conventions inspired by Microsoft Writing
  Style Guide. Covers tone, formatting, terminology, structure, and visual elements.
  Use when writing, editing, or reviewing any document for style compliance.
  Do not use for code style or linting rules.
metadata:
  author: manual
  version: "1.0"
  skill_type: quality-standard
compatibility:
  - augment
  - copilot
  - adk
---

# Style Guide

## When to use

- Writing any documentation (product, internal, technical)
- Reviewing document quality and consistency
- Establishing tone and formatting for new documents

## Core principles

1. **Be concise** — short sentences, simple words
2. **Be specific** — examples, values, details (not vague statements)
3. **Be consistent** — one term per concept, one style throughout
4. **Be helpful** — explain, link, show examples
5. **Be accessible** — alt text, hierarchy, sufficient contrast

## Tone rules

| Rule | Example |
|------|---------|
| Active voice | ✅ "System sends email" / ❌ "Email is sent by system" |
| Address user directly | ✅ "Click **Save**" / ❌ "The user should click Save" |
| Be positive | ✅ "Use API v2" / ❌ "Do not use API v1" |
| Present tense | ✅ "The page displays" / ❌ "The page will display" |

## Formatting

| Element | Format | Example |
|---------|--------|---------|
| UI elements | **Bold** | Click **Create New** |
| Technical values | `Code` | Set type to `Organization` |
| File paths | `Code` | Edit `config/settings.yaml` |
| First acronym use | Spell out | Call Detail Record (CDR) |
| Sequential steps | Numbered list | 1. Open... 2. Click... |
| Non-sequential items | Bullet list | - Option A / - Option B |

## Visual elements

- ❌ NEVER use emoji (🚀 📊 ✅) — unprofessional in enterprise docs
- ✅ Use text markers: "NOTE:", "WARNING:", "CRITICAL:"
- ✅ Use admonitions (Docusaurus `:::note`, `:::warning`) when available

## Heading rules

- H1 (`#`) — document title, exactly one per document
- H2 (`##`) — main sections
- H3 (`###`) — subsections
- H4 (`####`) — details (use sparingly)
- Never skip levels (H2 → H4 without H3)

## Polish language conventions

When writing in Polish:
- Headers: only first letter capitalized (NOT English Title Case)
  - ✅ `## Cykl życia` / ❌ `## Cykl Życia`
- Exceptions: acronyms (UI, API), product names (Customer Support Application)
- Code terms stay in English: `BusinessPartner`, `StateInfo`

## Code blocks

- Always specify language: ` ```scala `, ` ```graphql `, ` ```bash `
- Show both request and response for API examples
- Use realistic but fictional values
- Keep examples minimal but complete

## Terminology consistency

- Pick ONE term for each concept and use it everywhere
- Document chosen terms in a glossary
- Common mistake: alternating between "Partner" / "BP" / "Kontrahent"

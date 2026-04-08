---
name: diataxis-writing
description: >-
  Write documentation following the Diátaxis framework (tutorials, how-to guides,
  reference, explanation). Use when creating or reviewing product documentation,
  choosing document type, or structuring content sections.
  Do not use for internal/code documentation or README files.
metadata:
  author: manual
  version: "1.0"
  skill_type: quality-standard
compatibility:
  - augment
  - copilot
  - adk
---

# Diátaxis Writing

## When to use

- Creating new product documentation
- Choosing between tutorial, how-to, reference, or explanation
- Structuring document sections
- Reviewing documentation for type correctness

## Decision matrix

| Question 1: Learning or solving? | Question 2: Practical or theoretical? | → Type |
|----------------------------------|---------------------------------------|--------|
| Learning | Practical | **Tutorial** |
| Learning | Theoretical | **Explanation** |
| Solving | Practical | **How-to** |
| Solving | Theoretical | **Reference** |

## Type characteristics

### Tutorial

- Step-by-step, one scenario (happy path only)
- Concrete values, not placeholders
- Friendly, encouraging tone
- "Follow along and learn"
- Location: `tutorials/`

### How-to

- Problem-oriented, multiple scenarios
- General instructions (not one concrete case)
- Neutral, professional tone
- Edge cases and troubleshooting
- Location: `how-to/`

### Reference

- Information-oriented, complete coverage
- Tables, all fields, all values
- Dry, precise, austere tone
- No instructions or explanations
- Location: `reference/`

### Explanation

- Understanding-oriented, concepts and context
- Business rationale, "why it works this way"
- Educational, discursive tone
- Examples, analogies, comparisons
- Location: `explanation/`

## Anti-patterns

| ❌ Avoid | ✅ Instead |
|----------|-----------|
| Tutorial with multiple scenarios | One happy path per tutorial |
| How-to with business explanations | Move explanations to Explanation doc |
| Reference with step-by-step instructions | Move instructions to How-to |
| Explanation with technical field details | Move field lists to Reference |

## Frontmatter template

```yaml
---
title: "Document Title"
sidebar_position: 1
description: "Short description for SEO"
tags:
  - type-tag  # tutorial, how-to, reference, explanation
  - domain-tag
---
```

## Category structure

Every category needs BOTH files:

1. `_category_.json` — sidebar ordering with `"type": "doc"` (not `generated-index`)
2. `index.md` — manually curated landing page with logical grouping

## Internal links

Use paths without `/docs/` prefix:
- ✅ `[Tutorials](/tutorials/)`
- ❌ `[Tutorials](/docs/tutorials/)`

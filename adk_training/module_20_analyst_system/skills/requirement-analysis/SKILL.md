---
name: requirement-analysis
description: >-
  Analyze requirements for clarity, completeness, feasibility, and risks.
  Covers requirement decomposition, acceptance criteria validation, scope
  assessment, and dependency identification. Use when analyzing Jira tickets,
  user stories, feature requests, or initiative proposals. Do not use for
  code review or test generation.
metadata:
  author: manual
  version: "1.0"
  skill_type: process-workflow
compatibility:
  - augment
  - copilot
  - adk
---

# Requirement Analysis

## When to use

- Analyzing a new Jira ticket or feature request
- Reviewing initiative proposal for feasibility
- Decomposing high-level requirement into stories
- Validating acceptance criteria completeness

## Analysis dimensions

Evaluate every requirement across these dimensions:

| Dimension | Key questions |
|-----------|--------------|
| **Clarity** | Is the requirement unambiguous? Can two people interpret it the same way? |
| **Completeness** | Are all scenarios covered? Edge cases? Error cases? |
| **Feasibility** | Can it be implemented with current architecture? Tech constraints? |
| **Scope** | What's in scope? What's explicitly out of scope? Hidden scope? |
| **Dependencies** | What must exist before this can be built? What blocks on this? |
| **Risks** | What could go wrong? Performance? Security? Data migration? |
| **Testability** | Can acceptance criteria be verified? How? |

## Clarity assessment checklist

- [ ] No ambiguous pronouns ("it", "this", "the system" without antecedent)
- [ ] Quantities specified (not "many", "several", "some")
- [ ] Timeframes explicit (not "quickly", "in real-time" without definition)
- [ ] Roles identified (who does what)
- [ ] Success criteria measurable

## Acceptance criteria pattern

Each acceptance criterion should follow Given/When/Then:

```
Given [precondition]
When [action]
Then [expected result]
```

Bad: "System should handle errors properly"
Good: "Given a network timeout after 30s, when the user retries, then the system resumes from the last checkpoint"

## Scope assessment

For each requirement, identify:

1. **Explicit scope** — what the requirement says
2. **Implicit scope** — what's assumed but not written (migration? backward compatibility?)
3. **Out of scope** — what is explicitly excluded
4. **Hidden scope** — what becomes visible only during implementation

## Risk classification

| Severity | Description | Action |
|----------|-------------|--------|
| **Blocker** | Cannot proceed without resolution | Must resolve before implementation |
| **High** | Significant impact, workaround possible | Plan mitigation before sprint |
| **Medium** | Moderate impact, manageable | Document and monitor |
| **Low** | Minor impact | Note for awareness |

## Output structure

Analysis report should contain:
1. **Summary** — one paragraph understanding of the requirement
2. **Clarity issues** — list of ambiguities with suggested clarifications
3. **Completeness gaps** — missing scenarios, edge cases
4. **Scope assessment** — explicit / implicit / out of scope / hidden
5. **Dependencies** — upstream and downstream
6. **Risks** — classified with mitigation suggestions
7. **Recommendation** — ready for implementation / needs refinement / needs spike

# V1 — Skills Pack (Progressive Disclosure)

## The problem

Without skills, the planner prompt would either:

- contain *zero* OWASP guidance — and the LLM would invent generic
  selectors, miss obvious checks, and produce inconsistent severity ratings, or
- contain *all* OWASP guidance — and we'd burn token budget on irrelevant
  categories every single run, plus increase the chance of the model
  conflating unrelated checks.

## The pattern

We adopted Andrej Karpathy's [LLM-Wiki schema][karpathy] of three layers
plus the [`SkillToolset`][adk-skills] contract from `module_14`:

| Layer | Always loaded? | Cost | Contents |
|-------|----------------|------|----------|
| **L1** manifest  | yes | cheap | name + 1-line description of every skill |
| **L2** instructions | only when triggered | medium | full SKILL.md body |
| **L3** references | only when explicitly fetched | high | code samples, payload templates, fingerprint tables |

[karpathy]: https://karpathy.bearblog.dev/the-art-of-the-llm-wiki/
[adk-skills]: https://google.github.io/adk-docs/skills/

## How a skill is structured

```
skills/owasp-a01-access-control/
├── SKILL.md            ← YAML frontmatter + instructions body
└── references/
    └── idor-templates.md
```

The frontmatter is a tiny YAML subset (no PyYAML dependency):

```yaml
---
name: owasp-a01-access-control
description: Detect broken access control issues — IDOR, missing auth, CSRF.
triggers:
  - forms
  - auth
  - access-control
---
```

## How skills get selected

`skills_loader.recon_signals(recon)` is a pure function from a recon dict to
a list of trigger keywords:

| Recon observation | Triggers added |
|-------------------|----------------|
| (always) | `baseline` |
| `security_headers["Strict-Transport-Security"]` is None | `missing:strict-transport-security`, `crypto` |
| `security_headers["Content-Security-Policy"]` is None | `missing:content-security-policy`, `misconfig` |
| Any form with `<input type="password">` | `forms`, `auth`, `access-control` |
| Any form with method POST/PUT/PATCH | `injection` |
| `technologies` is non-empty | `misconfig` |

`select_skills_for_recon(recon)` then matches triggers against
`skill.triggers` and always includes `recon-helpers`.

## Why deterministic selection (not tool-calls)?

Module_24 uses `auggie_run` (single-shot) — there is no `Agent`/`Runner`
loop, so we cannot rely on the model calling `load_skill(name)` mid-prompt.
Instead, Python decides up front which L2 bodies to inject. This:

- keeps prompt construction reproducible (testable!);
- removes a class of LLM failure modes (model "forgets" to load a skill);
- lets us pre-compute the prompt size before we send it.

When we eventually wire this into an ADK `Agent` runtime, we expose
`consult_skill_resource(skill_name, rel_path)` as the L3 fetch tool — but
that's optional; today's flow works without it.

## Bundled skills

| Skill | OWASP category | Trigger keywords |
|-------|----------------|-----------------|
| `recon-helpers` | n/a — selector hygiene | `baseline` |
| `owasp-a01-access-control` | A01 — Broken Access Control | `forms`, `auth`, `access-control` |
| `owasp-a02-crypto` | A02 — Cryptographic Failures | `crypto`, `missing:strict-transport-security` |
| `owasp-a03-injection` | A03 — Injection | `injection`, `forms` |
| `owasp-a05-misconfig` | A05 — Security Misconfiguration | `misconfig`, `missing:content-security-policy`, `missing:x-frame-options` |

## How to author a new skill

1. Create `skills/<your-skill>/SKILL.md` with frontmatter + body.
2. Pick triggers that map to recon signals listed above.
3. (Optional) Add reference files under `skills/<your-skill>/references/`.
4. Run `pytest tests/test_skills_loader.py` — no test changes required, the
   loader auto-discovers your skill.

```yaml
---
name: owasp-a04-insecure-design
description: Spot business-logic flaws and missing rate-limits.
triggers:
  - forms
  - auth
---

# OWASP A04:2021 — Insecure Design

[your guidance here ...]
```

## Failure modes prevented

| Failure | How L1/L2/L3 prevents it |
|---------|-------------------------|
| Token budget blow-up | L2 only loaded when triggered. |
| Stale guidance | Skills are markdown files in git — code review is the gate. |
| Model can't tell which categories apply | Triggers are explicit; selection is deterministic. |
| New skills require code changes | Loader auto-discovers; only directory + SKILL.md needed. |

# Module 20: Analyst System

Multi-agent system for analyst support — requirement analysis, epic creation,
document generation, test planning, document review, and skill generation.

## Architecture

```
agent.py (root — captain router)
├── orchestrators/
│   ├── analyze_requirement.py    (ParallelAgent + SequentialAgent)
│   ├── create_epic.py            (SequentialAgent)
│   ├── generate_document.py      (SequentialAgent, dynamic skills)
│   ├── generate_test_plan.py     (SequentialAgent)
│   ├── review_document.py        (SequentialAgent)
│   └── generate_skill.py         (SequentialAgent, 6-step pipeline)
├── agents/                        (shared agent instructions)
├── tools/                         (FunctionTools + MCP)
├── skills/                        (Agent Skills — SKILL.md files)
├── contract/                      (ProjectKnowledgeContract)
└── prompts/                       (dynamic instruction builder)
```

## Setup

```bash
cd module_20_analyst_system
cp .env.template .env
# Fill in .env with your values
pip install -r requirements.txt
```

## Running

```bash
adk web .
```

## Orchestrators

| Orchestrator | Pattern | Purpose |
|-------------|---------|---------|
| **analyze_requirement** | Sequential → Parallel → Sequential | Multi-dimensional requirement analysis |
| **create_epic** | Sequential (4 steps) | Jira Epic with user stories |
| **generate_document** | Sequential (5 steps) | HLD, LLD, tutorials, how-to, reference |
| **generate_test_plan** | Sequential (4 steps) | Test plan with scenarios |
| **review_document** | Sequential (3 steps) | Quality review of existing docs |
| **generate_skill** | Sequential (6 steps) | Agent Skill generation from knowledge |

## Skills

Built-in skills in `skills/`:

- `diataxis-writing` — Diátaxis documentation framework
- `style-guide` — Enterprise writing style conventions
- `document-templates` — Document template catalog
- `requirement-analysis` — Requirement analysis methodology

New skills can be generated using the `generate_skill` orchestrator.

## Contract

`contract/sample_contract.json` — example for IoT Connect project.
Create your own contract JSON for other projects.

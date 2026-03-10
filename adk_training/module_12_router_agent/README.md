# Module 12: Router Agent - The Captain's Command 🏴‍☠️

## Overview

Master multi-agent routing patterns! Learn how to create a Captain agent that intelligently routes questions to specialist crew members.

## Learning Objectives

By the end of this module, you will:
- Create a root agent with multiple sub_agents
- Understand agent routing and transfer patterns
- Use LlmAgent's built-in transfer_to_agent capability
- Design specialist agents for different domains

## Key Concepts

### 1. Router Pattern Architecture

```
                    ┌─────────────────┐
                    │    Captain      │
                    │  (Root Agent)   │
                    └────────┬────────┘
                             │
         ┌───────────┬───────┴───────┬───────────┐
         ▼           ▼               ▼           ▼
    ┌─────────┐ ┌──────────┐ ┌─────────┐ ┌──────────┐
    │Navigator│ │Quartermaster│ │ Gunner │ │   Cook   │
    └─────────┘ └──────────┘ └─────────┘ └──────────┘
```

### 2. Setting Up Sub-Agents

```python
from google.adk.agents import LlmAgent

# Create specialist agents
navigator = LlmAgent(
    model="gemini-2.5-flash",
    name="navigator",
    description="Expert in navigation and routes",
    instruction="Handle navigation questions..."
)

quartermaster = LlmAgent(
    model="gemini-2.5-flash",
    name="quartermaster",
    description="Expert in inventory and supplies",
    instruction="Handle supply questions..."
)

# Root agent with sub_agents
captain = LlmAgent(
    model="gemini-2.5-flash",
    name="captain",
    instruction="Route questions to specialists...",
    sub_agents=[navigator, quartermaster]  # Key!
)
```

### 3. How Routing Works

The root agent's LLM decides which sub-agent should handle a query based on:
- The `description` of each sub-agent
- The content of the user's question
- The `instruction` in the root agent

The LLM uses `transfer_to_agent` to hand off to specialists.

## Files in This Module

| File | Purpose |
|------|---------|
| `agent.py` | Captain router with 4 specialist agents |
| `.env.template` | Environment configuration |
| `requirements.txt` | Python dependencies |

## Running the Module

### Step 1: Setup
```bash
cd adk_training/module_12_router_agent
cp .env.template .env
```

### Step 2: Run the Agent
```bash
adk web
```

### Step 3: Test Routing
Try different questions and observe which specialist responds!

## Example Interactions

```
You: What's the best route to Tortuga?

Captain: Aye, that be a question for me Navigator! 
*transfers to Navigator*

Navigator: Ahoy! The bearing to Tortuga be 45 degrees southwest. 
At current winds, expect a voyage of 3 days. I recommend hugging 
the coastline to avoid the open sea storms this time of year.
```

```
You: How much rum do we have left?

Captain: That be the Quartermaster's domain!
*transfers to Quartermaster*

Quartermaster: We have 30 barrels of rum in hold B. At current 
ration rates, this be enough for 60 days. I recommend restocking 
at the next port - Tortuga has the best prices.
```

## Exercise: Add a New Specialist

Add a "Doctor" agent to handle health questions:

```python
doctor_agent = LlmAgent(
    model=MODEL,
    name="doctor",
    description="Expert in crew health and medicine",
    instruction="""Ye be the Ship's Doctor...
    
    Handle questions about:
    - Injuries and treatments
    - Diseases and prevention
    - Medicine supplies
    - Crew fitness
    """
)

# Add to captain's sub_agents
root_agent = LlmAgent(
    ...,
    sub_agents=[
        navigator_agent,
        quartermaster_agent,
        gunner_agent,
        cook_agent,
        doctor_agent  # New!
    ]
)
```

## Alternative: AgentTool Pattern

Instead of sub_agents, you can wrap agents as tools:

```python
from google.adk.tools import agent_tool

nav_tool = agent_tool.AgentTool(agent=navigator_agent)

captain = LlmAgent(
    model=MODEL,
    name="captain",
    tools=[nav_tool]  # Agent as tool
)
```

## Routing Best Practices

| Practice | Reason |
|----------|--------|
| Clear descriptions | Helps LLM route correctly |
| Non-overlapping domains | Avoids confusion |
| Fallback in root | Handle edge cases |
| Specialist instructions | Each agent knows its role |

## Common Issues

| Issue | Solution |
|-------|----------|
| Wrong specialist chosen | Improve descriptions |
| Root answers instead | Strengthen delegation instruction |
| Specialist too narrow | Broaden scope or add agents |
| Slow responses | Consider parallel sub-agents |

---
*"A good Captain knows when to delegate!"* 🏴‍☠️


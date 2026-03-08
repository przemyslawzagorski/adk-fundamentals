# Module 05: Human-in-the-Loop 🏴‍☠️
## "The Admiral's Approval"

**Duration:** 45 minutes
**Difficulty:** ⭐⭐⭐ Intermediate-Advanced

---

## 🎯 Learning Objectives

By the end of this module, you will be able to:
1. Implement `before_model_callback` to gate LLM execution
2. Use `before_agent_callback` to initialize state
3. Create approval workflows using ADK callbacks
4. Understand when and why to add human oversight to agents

---

## 🏴‍☠️ The Pirate Story

> *The Quartermaster manages all the ship's doubloons, but the Admiral
> doesn't trust anyone with large sums. Any expenditure over 100 doubloons
> must be personally approved by the Admiral before it can proceed!*

This module demonstrates the **Human-in-the-Loop** pattern where:
- Small transactions (≤100 doubloons) are auto-approved
- Large transactions (>100 doubloons) require human approval
- The agent pauses and waits for approval before proceeding

**In this example, YOU are the Admiral!** When the agent requests approval, you approve or reject by typing a simple message. This demonstrates how callbacks can pause agent execution and wait for human input.

---

## 📚 Theory: Callbacks in ADK

### Callback Types

| Callback | When It Runs | Can Block? | Use Case |
|----------|--------------|------------|----------|
| `before_agent_callback` | Before agent starts | Yes | Initialize state, validate inputs |
| `after_agent_callback` | After agent completes | No | Cleanup, logging, save results |
| `before_model_callback` | Before each LLM call | Yes | Approval gates, caching, validation |
| `after_model_callback` | After each LLM call | No | Response filtering, logging |
| `before_tool_callback` | Before tool execution | Yes | Parameter validation |
| `after_tool_callback` | After tool execution | No | Result modification |

### Key Concept: Blocking Callbacks

When a callback returns a value (instead of `None`), it **blocks** normal execution:

```python
def before_model_callback(ctx, llm_request) -> Optional[LlmResponse]:
    if not approved:
        # Return a response to SKIP the LLM call
        return LlmResponse(content=types.Content(...))
    # Return None to PROCEED with normal LLM call
    return None
```

---

## 🔧 Setup

1. **Navigate to the module directory:**
   ```bash
   cd adk_training/module_05_human_in_loop
   ```

2. **Create your environment file:**
   ```bash
   cp .env.template .env
   # Edit .env with your project details
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the agent:**
   ```bash
   adk web
   ```

---

## 🧪 Exercises

### Exercise 1: Test the Approval Flow (10 min)

1. Start the agent with `adk web`
2. Ask: "Check the treasury balance"
3. Ask: "I need 50 doubloons for rum" (should auto-approve)
4. Ask: "I need 500 doubloons for new cannons" (should require approval)
5. Observe how the agent responds differently

### Exercise 2: Simulate Approval (10 min)

After requesting a large expenditure:

1. Request a large expenditure:
   ```
   I need 500 doubloons for new cannons
   ```

2. Agent will respond asking for approval. **You are the Admiral!**

3. To approve, type one of:
   ```
   approve
   approved
   yes
   ```

4. To reject, type one of:
   ```
   reject
   rejected
   no
   ```

5. Observe how the agent processes your decision

**Note:** Keep your approval/rejection message short to avoid the agent misinterpreting it as a new request.

### Exercise 3: Lower the Threshold (10 min)

Modify `agent.py` to change the approval threshold:
1. Find the line `if pending_amount > 100:`
2. Change it to `if pending_amount > 50:`
3. Restart the agent and test with 75 doubloons

### Exercise 4: Add Logging Callback (Bonus - 15 min)

Add an `after_agent_callback` that logs all treasury interactions:

```python
def log_treasury_activity(callback_context: CallbackContext) -> None:
    """After Agent Callback: Log completed treasury operations."""
    print(f"📝 [Log] Treasury activity completed")
    print(f"    Balance: {callback_context.state.get('treasury_balance')}")
    print(f"    Pending: {callback_context.state.get('pending_amount', 0)}")
    return None

# Add to root_agent:
root_agent = LlmAgent(
    ...
    after_agent_callback=log_treasury_activity
)
```

---

## 🎓 Key Takeaways

1. **`before_model_callback`** runs before every LLM call and can block it
2. **Return `None`** to allow normal execution
3. **Return `LlmResponse`** to skip the LLM and use your response instead
4. **State** is the key to tracking approval status between turns
5. **Human-in-the-loop** is essential for high-stakes operations

---

## 🌊 Real-World Applications

- **Financial transactions** requiring manager approval
- **Data deletion** operations needing confirmation
- **External communications** (emails, messages) requiring review
- **Production deployments** with manual gate checks
- **Content moderation** with human review

---

## 📖 Further Reading

- [ADK Callbacks Documentation](https://google.github.io/adk-docs/callbacks)
- [State Management in ADK](https://google.github.io/adk-docs/state)

---

*"The Admiral's word be law, matey! No doubloons leave this ship without proper approval!"* 🏴‍☠️


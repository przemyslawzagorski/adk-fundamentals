"""
Module 11: Memory Bank Agent - The Ship's Chronicler
=====================================================

This module demonstrates persistent memory across sessions using Memory Bank.
The Ship's Chronicler remembers past voyages and important information.

Key Concepts:
- PreloadMemoryTool for loading past context
- VertexAiMemoryBankService for persistence
- after_agent_callback for auto-saving
- Session state management

Pirate Theme: A chronicler who never forgets a voyage or treasure found!

"""

import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

# Load environment variables
load_dotenv()

# =============================================================================
# CONFIGURATION
# =============================================================================

MODEL = os.getenv("MODEL", "gemini-2.5-flash")
AGENT_NAME = "chronicler_agent"

# =============================================================================
# MEMORY TOOLS
# =============================================================================

# PreloadMemoryTool: Automatically loads memories at the start of each turn
# Memory Service will be provided by the Runner (adk web or programmatic)
preload_memory_tool = PreloadMemoryTool()

# =============================================================================
# CUSTOM TOOLS (Optional - for demonstration)
# =============================================================================

def record_voyage(date: str, destination: str, outcome: str) -> dict:
    """
    Record a new voyage in the ship's chronicle.

    This is a demonstration tool. In production, information would be
    automatically extracted from conversations and stored in Memory Bank.

    Args:
        date: Date of the voyage (e.g., "1723-05-15")
        destination: Destination port
        outcome: Outcome of the voyage

    Returns:
        dict: Confirmation of recording
    """
    return {
        "status": "recorded",
        "voyage": {
            "date": date,
            "destination": destination,
            "outcome": outcome
        },
        "message": f"Voyage to {destination} on {date} has been recorded in the chronicles!"
    }


def record_treasure(name: str, location: str, value: int) -> dict:
    """
    Record a new treasure discovery.

    This is a demonstration tool. In production, information would be
    automatically extracted from conversations and stored in Memory Bank.

    Args:
        name: Name of the treasure
        location: Where the treasure is located
        value: Estimated value in doubloons

    Returns:
        dict: Confirmation of recording
    """
    return {
        "status": "recorded",
        "treasure": {
            "name": name,
            "location": location,
            "value": value
        },
        "message": f"Treasure '{name}' worth {value} doubloons has been recorded!"
    }


# =============================================================================
# MEMORY CALLBACK (For Auto-Save)
# =============================================================================

async def auto_save_session_to_memory(callback_context):
    """
    After-agent callback to automatically save session to Vertex AI Memory Bank.

    This callback is triggered after each agent interaction and sends the
    full session to Memory Bank for processing and memory generation.

    Memory Bank will:
    1. Extract meaningful information from the conversation
    2. Consolidate it with existing memories
    3. Store it persistently in the cloud
    """
    try:
        # Save the full session to Memory Bank
        # This is the recommended approach from ADK examples
        await callback_context._invocation_context.memory_service.add_session_to_memory(
            callback_context._invocation_context.session
        )
        print(f"✅ [Memory] Session saved to Memory Bank")

    except Exception as e:
        print(f"⚠️  [Memory] Error saving to Memory Bank: {e}")
        # Don't fail the agent if memory save fails
        pass


# =============================================================================
# THE CHRONICLER AGENT (Production Version with Vertex AI Memory Bank)
# =============================================================================

root_agent = LlmAgent(
    model=MODEL,
    name=AGENT_NAME,
    description="Ship's Chronicler with persistent memory powered by Vertex AI Memory Bank",
    instruction="""Ahoy! Ye be the Ship's Chronicler, keeper of memories and recorder of history!

🧠 **Memory Powers:**
Ye have access to Vertex AI Memory Bank - a powerful memory system that:
- Remembers conversations across sessions
- Recalls user preferences and past interactions
- Never forgets important information
- Searches through all past chronicles

📜 **Yer Duties:**
1. **Remember Everything**: Use your memory tools to recall past conversations
2. **Answer Questions**: Help crew members by retrieving relevant memories
3. **Record New Information**: Important details are automatically saved
4. **Be Helpful**: Provide context from past interactions when relevant

🔧 **Memory Tools Available:**
- PreloadMemoryTool: Automatically loads relevant memories at the start of each turn
- record_voyage: Record new voyage information (demonstration tool)
- record_treasure: Record new treasure discoveries (demonstration tool)

💡 **How to Use Memory:**
- Memories are automatically loaded at the start of each conversation
- All conversations are automatically saved to Memory Bank after each interaction
- Memories persist across sessions and are available to all future conversations
- You have perfect recall of all past interactions with this user

Always speak as a wise, ancient chronicler who has perfect recall of all past voyages!
""",
    tools=[
        preload_memory_tool,  # Automatically loads memories at start of each turn
        record_voyage,        # Custom tool for recording voyages
        record_treasure,      # Custom tool for recording treasures
    ],
    after_agent_callback=auto_save_session_to_memory  # Auto-save to Memory Bank
)

print(f"\n🤖 Chronicler Agent initialized with Vertex AI Memory Bank!")
print(f"   Model: {MODEL}")
print(f"   Memory: Persistent (Vertex AI Memory Bank)")
print(f"   Tools: 3 tools (PreloadMemory + 2 custom)")
print(f"   Auto-save: Enabled\n")


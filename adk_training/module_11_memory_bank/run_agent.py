"""
Runner script for Memory Bank Agent with Vertex AI.

This script demonstrates how to run the Chronicler Agent with persistent
memory using Vertex AI Memory Bank.

Usage:
    python run_agent.py
"""

import os
import asyncio
from dotenv import load_dotenv
from google.adk.sessions import VertexAiSessionService
from google.adk.runners import Runner
from google.adk.memory import VertexAiMemoryBankService
from google.genai import types

# Import our agent
from agent.agent import root_agent

# Load environment variables
load_dotenv()

# Configuration
PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT')
REGION = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
AGENT_ENGINE_ID = os.getenv('AGENT_ENGINE_ID')

if not all([PROJECT_ID, REGION, AGENT_ENGINE_ID]):
    print("❌ Error: Missing required environment variables")
    print("   Please check your .env file for:")
    print("   - GOOGLE_CLOUD_PROJECT")
    print("   - GOOGLE_CLOUD_LOCATION")
    print("   - AGENT_ENGINE_ID")
    exit(1)

# Construct resource name
AGENT_ENGINE_RESOURCE_NAME = f"projects/{PROJECT_ID}/locations/{REGION}/reasoningEngines/{AGENT_ENGINE_ID}"

APP_NAME = "pirate_chronicles"
USER_ID = "captain_jack"

print("=" * 70)
print("🏴‍☠️ CHRONICLER AGENT - MEMORY BANK TEST")
print("=" * 70)
print(f"Project: {PROJECT_ID}")
print(f"Region: {REGION}")
print(f"Agent Engine ID: {AGENT_ENGINE_ID}")
print(f"User: {USER_ID}")
print()

# Initialize services
session_service = VertexAiSessionService(PROJECT_ID, REGION)
memory_service = VertexAiMemoryBankService(
    project=PROJECT_ID,
    location=REGION,
    agent_engine_id=AGENT_ENGINE_ID
)

# Create runner with Memory Service
runner = Runner(
    agent=root_agent,
    app_name=AGENT_ENGINE_RESOURCE_NAME,
    session_service=session_service,
    memory_service=memory_service
)


def call_agent(query, session_id, user_id):
    """Call the agent with a query and print the response."""
    print(f"\n👤 User: {query}")
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run(user_id=user_id, session_id=session_id, new_message=content)

    final_response = None
    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print(f"🏴‍☠️ Chronicler: {final_response}\n")
    return final_response


async def main():
    print("📝 SESSION 1: Teaching the Chronicler about a treasure...")
    print("-" * 70)
    
    # Session 1: Tell the agent about a treasure
    session1 = await session_service.create_session(
        app_name=AGENT_ENGINE_RESOURCE_NAME,
        user_id=USER_ID
    )

    call_agent("Znaleźliśmy złoty skarb na Skull Island w 1723 roku!", session1.id, USER_ID)
    call_agent("Skarb był wart 10000 doublonów!", session1.id, USER_ID)
    
    # Save session to Memory Bank
    print("💾 Saving session to Memory Bank...")
    await memory_service.add_session_to_memory(session1)
    print("✅ Session saved!\n")

    print("=" * 70)
    print("🔍 SESSION 2: Testing if Chronicler remembers...")
    print("-" * 70)
    
    # Session 2: Ask the agent to recall
    session2 = await session_service.create_session(
        app_name=AGENT_ENGINE_RESOURCE_NAME,
        user_id=USER_ID
    )

    response = call_agent("Gdzie znaleźliśmy skarb?", session2.id, USER_ID)
    
    # Check if agent remembered
    print("=" * 70)
    if response and "skull island" in response.lower():
        print("✅ SUCCESS: Chronicler remembered the treasure location!")
        print("   Memory Bank is working correctly! 🎉")
    else:
        print("⚠️  WARNING: Chronicler didn't mention Skull Island")
        print("   Memory Bank might need more time or configuration")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())


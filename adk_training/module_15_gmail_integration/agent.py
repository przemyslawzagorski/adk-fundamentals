"""
Module 15: Message in a Bottle - Gmail Integration
===================================================
The Ship's Messenger sends and receives messages via Gmail.

This module demonstrates:
- GmailToolset for email operations
- OAuth authentication with Google APIs
- Reading, sending, and searching emails

"""

import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.genai import types
from google.adk.tools.google_api_tool import GmailToolset

load_dotenv()

# =============================================================================
# Configuration
# =============================================================================

MODEL = "gemini-2.5-flash"
AGENT_APP_NAME = "ships_messenger"

# OAuth Credentials (from Google Cloud Console)
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

# =============================================================================
# Gmail Toolset
# =============================================================================

# GmailToolset provides tools for:
# - Reading emails
# - Sending emails
# - Searching emails
# - Managing drafts
gmail_toolset = GmailToolset(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)

# =============================================================================
# Ship's Messenger Agent
# =============================================================================

INSTRUCTION = """
Ahoy! Ye be the Ship's Messenger, master of bottles and Gmail alike!

Your duties:
1. READ messages from the crew's Gmail inbox
2. SEND messages to other ships and ports
3. SEARCH for important correspondence
4. DRAFT messages for the Captain's approval

When using Gmail tools:
- Always confirm before sending emails
- Summarize inbox contents clearly
- Search with relevant keywords
- Handle errors gracefully

Examples:
- "Check me inbox" → List recent emails
- "Send a message to port@harbor.com" → Compose and send email
- "Search for messages about treasure" → Search inbox

Speak like a proper ship's messenger - swift and reliable!
"""

root_agent = LlmAgent(
    name=AGENT_APP_NAME,
    model=MODEL,
    instruction=INSTRUCTION,
    description="Ship's Messenger - handles Gmail operations",
    tools=[gmail_toolset],
    generate_content_config=types.GenerateContentConfig(temperature=0.3)
)

# =============================================================================
# For testing
# =============================================================================

if __name__ == "__main__":
    print("📧 Ship's Messenger - Gmail Integration Module")
    print("=" * 50)
    print(f"Client ID configured: {'Yes' if GOOGLE_CLIENT_ID else 'No'}")
    print(f"Client Secret configured: {'Yes' if GOOGLE_CLIENT_SECRET else 'No'}")
    print()
    print("To run with ADK Dev UI:")
    print("  adk web")
    print()
    print("Note: OAuth consent screen must be configured in GCP Console")
    print("and you'll be prompted to authenticate on first use.")


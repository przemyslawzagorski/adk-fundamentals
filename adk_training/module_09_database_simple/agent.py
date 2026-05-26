"""
Simple Database Agent - SQLite Example (WITHOUT MCP)

This example shows how to use ADK with a local SQLite database.
No external services required - perfect for learning!

Key concepts:
- Using Python functions as tools
- Direct database access with SQLite
- No MCP, no Docker, no cloud services

Usage:
    # Run with ADK web interface:
    adk web adkagents/00-adk-intro/adk04-simple-database

    # Or programmatically (see README.md for examples)
"""

import os
import sys
from dotenv import load_dotenv
from google.adk.agents import Agent

# Add current directory to Python path to ensure imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import our database tools
from database_tools import (
    search_hotels_by_name,
    search_hotels_by_location,
    search_hotels_by_price_range,
    get_hotel_by_id
)

load_dotenv()

# =============================================================================
# CONFIGURATION
# =============================================================================

# Try different models if you hit rate limits:
# - gemini-2.5-flash-exp (experimental, may have lower quota)
# - gemini-2.5-flash (stable, higher quota)
# - gemini-1.5-flash (older, usually higher quota)
MODEL = "gemini-2.5-flash"  # Changed from gemini-2.5-flash-exp
AGENT_APP_NAME = 'hotel_expert_simple'

instruction_prompt = """
You are a helpful hotel search assistant for Poland.

You can help users:
- Find hotels by name
- Find hotels in specific cities
- Find hotels within a price range
- Get detailed information about specific hotels

Always provide clear, friendly responses with relevant details like:
- Hotel name and location
- Rating (out of 5)
- Price per night
- Brief description

If multiple hotels match, show the top results sorted by rating.
"""

# =============================================================================
# CREATE AGENT
# =============================================================================

root_agent = Agent(
    model=MODEL,
    name=AGENT_APP_NAME,
    description="Agent to help users find hotels in Poland using a local SQLite database.",
    instruction=instruction_prompt,
    tools=[
        search_hotels_by_name,
        search_hotels_by_location,
        search_hotels_by_price_range,
        get_hotel_by_id
    ]
)



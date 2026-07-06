# =============================================================================
# Module 6: Cloud Run Deployment - "Launching the Ship"
# =============================================================================
# A deployable pirate navigation agent for Cloud Run
# =============================================================================

import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent

# Load environment variables (for local development)
load_dotenv()

# =============================================================================
# DEPLOYABLE PIRATE AGENT
# =============================================================================
# This agent is designed to be deployed to Cloud Run.
# Key requirements for deployment:
# 1. Must have a `root_agent` variable
# 2. Must be in an `agent.py` file
# 3. Requirements must be in `requirements.txt`
# =============================================================================


def get_current_weather(location: str) -> dict:
    """
    Get current weather conditions for sailing.
    
    Args:
        location: The port or sea location to check weather for.
        
    Returns:
        Weather conditions for the specified location.
    """
    # Simulated weather data for demonstration
    weather_data = {
        "Caribbean": {
            "temperature": "28°C",
            "conditions": "Sunny with light trade winds",
            "wind_speed": "15 knots",
            "wave_height": "1-2 meters",
            "sailing_advisory": "Excellent conditions for sailing!"
        },
        "Atlantic": {
            "temperature": "22°C",
            "conditions": "Partly cloudy",
            "wind_speed": "20 knots",
            "wave_height": "2-3 meters",
            "sailing_advisory": "Good sailing conditions, watch for swells."
        },
        "Mediterranean": {
            "temperature": "25°C",
            "conditions": "Clear skies",
            "wind_speed": "10 knots",
            "wave_height": "0.5-1 meters",
            "sailing_advisory": "Calm waters, perfect for coastal navigation."
        }
    }
    
    # Match location or return default
    for region, data in weather_data.items():
        if region.lower() in location.lower():
            return {"location": location, **data}
    
    return {
        "location": location,
        "temperature": "24°C",
        "conditions": "Variable",
        "wind_speed": "12 knots",
        "wave_height": "1-2 meters",
        "sailing_advisory": "Standard sailing conditions."
    }


def calculate_voyage_time(
    origin: str,
    destination: str,
    ship_speed_knots: int = 10
) -> dict:
    """
    Calculate estimated voyage time between ports.
    
    Args:
        origin: Starting port name.
        destination: Destination port name.
        ship_speed_knots: Ship speed in knots (default: 10).
        
    Returns:
        Voyage time estimation with details.
    """
    # Simulated distances (nautical miles)
    route_distances = {
        ("port royal", "tortuga"): 150,
        ("tortuga", "havana"): 200,
        ("havana", "nassau"): 350,
        ("nassau", "port royal"): 400,
    }
    
    # Normalize input
    origin_lower = origin.lower().strip()
    dest_lower = destination.lower().strip()
    
    # Find distance
    distance = route_distances.get(
        (origin_lower, dest_lower),
        route_distances.get((dest_lower, origin_lower), 250)  # Default
    )
    
    # Calculate time
    hours = distance / ship_speed_knots
    days = hours / 24
    
    return {
        "origin": origin,
        "destination": destination,
        "distance_nautical_miles": distance,
        "ship_speed_knots": ship_speed_knots,
        "estimated_hours": round(hours, 1),
        "estimated_days": round(days, 2),
        "recommendation": f"Set sail at dawn for optimal conditions!"
    }


# =============================================================================
# ROOT AGENT - Required for ADK deployment
# =============================================================================
# The agent MUST be named `root_agent` for ADK to discover it.
# =============================================================================

root_agent = LlmAgent(
    name="pirate_navigator",
    model="gemini-2.5-flash",
    description="A pirate navigation agent deployed to the cloud.",
    instruction="""You are Captain Cloudbeard, an expert pirate navigator 
deployed to the high seas of Google Cloud!

Your expertise includes:
- Weather forecasting for sailing conditions
- Voyage planning and time estimation
- Navigation advice for Caribbean waters

Always respond in a friendly pirate manner, using nautical terms.
Use your tools to provide accurate information about:
- Current weather conditions for sailing
- Voyage time calculations between ports

Start conversations with "Ahoy, cloud sailor!" and sign off with 
"Fair winds and following seas from the cloud!"

Remember: You're running on Cloud Run - the most reliable ship in the fleet!
""",
    tools=[get_current_weather, calculate_voyage_time],
)


"""
real_estate_app/services.py - Business logic for Real Estate Property Management.
Domain: Real Estate / Property Management
"""

from typing import List, Optional, Dict
from .models import Property, Agent, Listing
from datetime import datetime

class PropertyService:
    """Manages business operations related to properties, agents, and listings."""

    def __init__(self):
        self._properties: Dict[str, Property] = {}
        self._agents: Dict[str, Agent] = {}
        self._listings: Dict[str, Listing] = {}

    def add_property(self, property: Property) -> Property:
        if property.property_id in self._properties:
            raise ValueError(f"Property with ID {property.property_id} already exists.")
        self._properties[property.property_id] = property
        return property

    def get_property(self, property_id: str) -> Optional[Property]:
        return self._properties.get(property_id)

    def update_property(self, property_id: str, updates: Dict) -> Optional[Property]:
        property = self.get_property(property_id)
        if not property:
            return None
        
        for key, value in updates.items():
            if hasattr(property, key):
                setattr(property, key, value)
        property.updated_at = datetime.now()
        return property

    def delete_property(self, property_id: str) -> bool:
        if property_id in self._properties:
            del self._properties[property_id]
            # TODO: Ensure that deleting a property also removes associated listings.
            # TODO: Use Copilot Agent Mode to refactor this method to handle cascading deletes for related listings.
            return True
        return False

    def list_all_properties(self) -> List[Property]:
        return list(self._properties.values())

    def add_agent(self, agent: Agent) -> Agent:
        if agent.agent_id in self._agents:
            raise ValueError(f"Agent with ID {agent.agent_id} already exists.")
        self._agents[agent.agent_id] = agent
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        return self._agents.get(agent_id)

    # TODO: Implement update_agent and delete_agent methods using similar patterns.
    # TODO: Use Copilot Agent Mode to implement full CRUD operations for the Agent entity.

    def create_listing(self, property_id: str, agent_id: str, list_price: float, status: str = "Active") -> Optional[Listing]:
        if property_id not in self._properties:
            print(f"Error: Property with ID {property_id} not found.")
            return None
        if agent_id not in self._agents:
            print(f"Error: Agent with ID {agent_id} not found.")
            return None
        
        listing = Listing(property_id=property_id, agent_id=agent_id, list_price=list_price, status=status)
        self._listings[listing.listing_id] = listing
        return listing

    def get_listing(self, listing_id: str) -> Optional[Listing]:
        return self._listings.get(listing_id)

    # TODO: Implement update_listing and delete_listing methods.
    # TODO: Use Copilot Agent Mode to ensure all updates to listings properly timestamp `updated_at`.
    # TODO: Refactor the `PropertyService` to use a more persistent storage mechanism (e.g., a simple JSON file or a lightweight database) instead of in-memory dictionaries.
    # TODO: Apply a self-correction loop with Agent Mode to handle potential data inconsistencies after changing storage.

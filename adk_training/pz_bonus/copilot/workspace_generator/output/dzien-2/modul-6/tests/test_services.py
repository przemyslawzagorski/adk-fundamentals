"""
tests/test_services.py - Unit tests for the PropertyService.
Domain: Real Estate / Property Management
"""

import pytest
from datetime import datetime
from real_estate_app.services import PropertyService
from real_estate_app.models import Property, Agent, Listing

@pytest.fixture
def property_service():
    """Provides a fresh PropertyService instance for each test."""
    return PropertyService()

@pytest.fixture
def sample_property():
    """Provides a sample Property object."""
    return Property(
        address="789 Pine Rd", city="Villagetown", state="TX", zip_code="77001",
        property_type="House", square_footage=2000, number_of_bedrooms=4,
        number_of_bathrooms=3.0, price=650000.0, description="Spacious family home"
    )

@pytest.fixture
def sample_agent():
    """Provides a sample Agent object."""
    return Agent(
        first_name="Jane", last_name="Smith", email="jane.smith@example.com",
        phone="555-5678", license_number="TX987654"
    )

def test_add_property(property_service, sample_property):
    """Test adding a property."""
    added_property = property_service.add_property(sample_property)
    assert added_property.property_id == sample_property.property_id
    assert property_service.get_property(sample_property.property_id) is not None
    # TODO: Use Copilot to write an assertion that verifies the property details are correctly stored.

def test_get_property_not_found(property_service):
    """Test getting a non-existent property."""
    assert property_service.get_property("non-existent-id") is None

def test_update_property(property_service, sample_property):
    """Test updating an existing property."""
    property_service.add_property(sample_property)
    updates = {"price": 700000.0, "description": "Updated description"}
    updated_property = property_service.update_property(sample_property.property_id, updates)
    
    assert updated_property is not None
    assert updated_property.price == 700000.0
    assert updated_property.description == "Updated description"
    assert updated_property.updated_at > sample_property.updated_at
    # TODO: Use Copilot Agent Mode to generate more comprehensive tests for property updates, including invalid fields.

def test_delete_property(property_service, sample_property):
    """Test deleting a property."""
    property_service.add_property(sample_property)
    assert property_service.delete_property(sample_property.property_id) is True
    assert property_service.get_property(sample_property.property_id) is None

def test_add_agent(property_service, sample_agent):
    """Test adding an agent."""
    added_agent = property_service.add_agent(sample_agent)
    assert added_agent.agent_id == sample_agent.agent_id
    assert property_service.get_agent(sample_agent.agent_id) is not None
    # TODO: Use Copilot to verify agent details are correctly stored.

def test_create_listing(property_service, sample_property, sample_agent):
    """Test creating a listing."""
    property_service.add_property(sample_property)
    property_service.add_agent(sample_agent)
    
    listing = property_service.create_listing(
        property_id=sample_property.property_id,
        agent_id=sample_agent.agent_id,
        list_price=sample_property.price + 50000
    )
    
    assert listing is not None
    assert listing.property_id == sample_property.property_id
    assert listing.agent_id == sample_agent.agent_id
    assert property_service.get_listing(listing.listing_id) is not None
    # TODO: Use Copilot Agent Mode to generate tests for listing updates and deletion, and edge cases like invalid property/agent IDs.

# TODO: Use Copilot Agent Mode to create a new test file, `test_cli.py`, to test the command-line interface directly.
# TODO: Leverage Copilot's self-correction loop to ensure all tests pass after refactoring the storage mechanism in `PropertyService`.

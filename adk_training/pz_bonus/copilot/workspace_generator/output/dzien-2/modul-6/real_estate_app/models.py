"""
real_estate_app/models.py - Data models for the Real Estate Property Management System.
Domain: Real Estate / Property Management
"""

import uuid
from datetime import datetime
from typing import Optional, List

class Property:
    """Represents a real estate property."""
    def __init__(
        self,
        address: str,
        city: str,
        state: str,
        zip_code: str,
        property_type: str,  # e.g., 'House', 'Apartment', 'Land'
        square_footage: int,
        number_of_bedrooms: int,
        number_of_bathrooms: float,
        price: float,
        description: Optional[str] = None,
        property_id: Optional[str] = None
    ):
        self.property_id = property_id if property_id else str(uuid.uuid4())
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.property_type = property_type
        self.square_footage = square_footage
        self.number_of_bedrooms = number_of_bedrooms
        self.number_of_bathrooms = number_of_bathrooms
        self.price = price
        self.description = description
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def to_dict(self):
        return {
            "property_id": self.property_id,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
            "property_type": self.property_type,
            "square_footage": self.square_footage,
            "number_of_bedrooms": self.number_of_bedrooms,
            "number_of_bathrooms": self.number_of_bathrooms,
            "price": self.price,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            property_id=data.get("property_id"),
            address=data["address"],
            city=data["city"],
            state=data["state"],
            zip_code=data["zip_code"],
            property_type=data["property_type"],
            square_footage=data["square_footage"],
            number_of_bedrooms=data["number_of_bedrooms"],
            number_of_bathrooms=data["number_of_bathrooms"],
            price=data["price"],
            description=data.get("description"),
        )

class Agent:
    """Represents a real estate agent."""
    def __init__(
        self,
        first_name: str,
        last_name: str,
        email: str,
        phone: str,
        license_number: str,
        agent_id: Optional[str] = None
    ):
        self.agent_id = agent_id if agent_id else str(uuid.uuid4())
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.license_number = license_number
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def to_dict(self):
        return {
            "agent_id": self.agent_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "license_number": self.license_number,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            agent_id=data.get("agent_id"),
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            phone=data["phone"],
            license_number=data["license_number"],
        )

class Listing:
    """Represents a property listing."""
    def __init__(
        self,
        property_id: str,
        agent_id: str,
        status: str,  # e.g., 'Active', 'Pending', 'Sold'
        list_price: float,
        listing_date: Optional[datetime] = None,
        listing_id: Optional[str] = None
    ):
        self.listing_id = listing_id if listing_id else str(uuid.uuid4())
        self.property_id = property_id
        self.agent_id = agent_id
        self.status = status
        self.list_price = list_price
        self.listing_date = listing_date if listing_date else datetime.now()
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def to_dict(self):
        return {
            "listing_id": self.listing_id,
            "property_id": self.property_id,
            "agent_id": self.agent_id,
            "status": self.status,
            "list_price": self.list_price,
            "listing_date": self.listing_date.isoformat(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            listing_id=data.get("listing_id"),
            property_id=data["property_id"],
            agent_id=data["agent_id"],
            status=data["status"],
            list_price=data["list_price"],
            listing_date=datetime.fromisoformat(data["listing_date"]) if "listing_date" in data else None,
        )

# TODO: Add a `Client` model to represent potential buyers or renters.
# TODO: Use Copilot Agent Mode to automatically generate getters and setters for all model attributes across the file.
# TODO: Create a custom Copilot command to validate all `to_dict` and `from_dict` methods for data integrity.

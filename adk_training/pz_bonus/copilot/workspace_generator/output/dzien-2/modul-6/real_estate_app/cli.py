"""
real_estate_app/cli.py - Command Line Interface for the Real Estate Property Management System.
Demonstrates interaction via Copilot CLI.
Domain: Real Estate / Property Management
"""

import argparse
from typing import List
from .services import PropertyService
from .models import Property, Agent, Listing

# Global service instance for the CLI
property_service = PropertyService()

def init_sample_data():
    """Initializes some sample data for demonstration."""
    print("Initializing sample data...")
    prop1 = Property("123 Main St", "Anytown", "CA", "90210", "House", 1500, 3, 2.5, 500000.0)
    prop2 = Property("456 Oak Ave", "Someton", "NY", "10001", "Apartment", 800, 1, 1.0, 300000.0)
    agent1 = Agent("John", "Doe", "john.doe@example.com", "555-1234", "CA123456")
    
    property_service.add_property(prop1)
    property_service.add_property(prop2)
    property_service.add_agent(agent1)
    
    property_service.create_listing(prop1.property_id, agent1.agent_id, 510000.0, "Active")
    property_service.create_listing(prop2.property_id, agent1.agent_id, 320000.0, "Pending")
    print("Sample data initialized.")

def add_property_command(args):
    """Handles adding a property via CLI."""
    try:
        new_property = Property(
            address=args.address,
            city=args.city,
            state=args.state,
            zip_code=args.zip_code,
            property_type=args.type,
            square_footage=args.sqft,
            number_of_bedrooms=args.beds,
            number_of_bathrooms=args.baths,
            price=args.price,
            description=args.description
        )
        property_service.add_property(new_property)
        print(f"Property added: {new_property.address} (ID: {new_property.property_id})")
    except ValueError as e:
        print(f"Error adding property: {e}")

# TODO: Use Copilot CLI custom command creation to define a 'list-properties' command.
# TODO: The 'list-properties' command should display all properties with key details.
# Example usage: `copilot-cli real-estate list-properties`

# TODO: Implement a 'get-property <id>' command.
def get_property_command(args):
    """Handles getting a property by ID via CLI."""
    prop = property_service.get_property(args.property_id)
    if prop:
        print("Property Details:")
        for key, value in prop.to_dict().items():
            print(f"  {key}: {value}")
    else:
        print(f"Property with ID {args.property_id} not found.")

# TODO: Use Copilot Agent Mode to generate a 'add-agent' command similar to 'add-property'.
# TODO: Define a custom Copilot command to generate sample data if the service is empty, leveraging the `init_sample_data` function.

def main():
    parser = argparse.ArgumentParser(description="Real Estate Property Management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Initialize command
    init_parser = subparsers.add_parser("init", help="Initialize sample data")
    init_parser.set_defaults(func=lambda _: init_sample_data())

    # Add Property command
    add_prop_parser = subparsers.add_parser("add-property", help="Add a new property")
    add_prop_parser.add_argument("--address", required=True, help="Property address")
    add_prop_parser.add_argument("--city", required=True, help="City")
    add_prop_parser.add_argument("--state", required=True, help="State (e.g., CA)")
    add_prop_parser.add_argument("--zip_code", required=True, help="Zip Code")
    add_prop_parser.add_argument("--type", required=True, choices=["House", "Apartment", "Land"], help="Property type")
    add_prop_parser.add_argument("--sqft", type=int, required=True, help="Square footage")
    add_prop_parser.add_argument("--beds", type=int, required=True, help="Number of bedrooms")
    add_prop_parser.add_argument("--baths", type=float, required=True, help="Number of bathrooms")
    add_prop_parser.add_argument("--price", type=float, required=True, help="Listing price")
    add_prop_parser.add_argument("--description", help="Property description")
    add_prop_parser.set_defaults(func=add_property_command)

    # Get Property command
    get_prop_parser = subparsers.add_parser("get-property", help="Get property details by ID")
    get_prop_parser.add_argument("property_id", help="ID of the property to retrieve")
    get_prop_parser.set_defaults(func=get_property_command)

    args = parser.parse_args()

    if args.command:
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

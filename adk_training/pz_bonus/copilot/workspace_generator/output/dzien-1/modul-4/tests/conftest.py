import pytest
from src.logistics.models import Address, Package, Shipment
from src.logistics.shipping_service import ShippingService, ShipmentRepository # Updated import

# W Zadanie 4, Krok 3, użyjesz Copilot Agent Mode tutaj, aby zaktualizować fixture'y
# do obsługi refaktoryzacji ShippingService, która teraz przyjmuje ShipmentRepository.
# Pamiętaj o mockowaniu ShipmentRepository w testach jednostkowych.

@pytest.fixture(scope="function")
def mock_shipment_repository():
    \"\"\"Provides a fresh, mocked ShipmentRepository instance for each test function.\"\"\"
    repo = ShipmentRepository()
    return repo

@pytest.fixture(scope="function")
def empty_shipping_service(mock_shipment_repository):
    \"\"\"Provides a fresh, empty ShippingService instance with a mocked repository.\"\"\"
    return ShippingService(shipment_repo=mock_shipment_repository)

@pytest.fixture(scope="session")
def example_address_origin():
    \"\"\"Provides a reusable origin Address for the entire test session.\"\"\"
    return Address(street="123 Corporate Blvd", city="Logisticsville", zip_code="LS1 1AA", country="GB")

@pytest.fixture(scope="session")
def example_address_destination():
    \"\"\"Provides a reusable destination Address for the entire test session.\"\"\"
    return Address(street="789 Distribution Rd", city="Deliverytown", zip_code="DL9 9ZZ", country="GB")

@pytest.fixture
def example_package_heavy():
    \"\"\"Provides a heavy package.\"\"\"\
    return Package(package_id="HPKG001", weight_kg=50.0, dimensions_cm=(100, 50, 50), fragile=False)

@pytest.fixture
def example_package_light_fragile():
    \"\"\"Provides a light, fragile package.\"\"\"
    return Package(package_id="LPFG002", weight_kg=1.0, dimensions_cm=(20, 20, 10), fragile=True)

@pytest.fixture
def populated_shipping_service(empty_shipping_service, example_address_origin, example_address_destination,
                               example_package_heavy, example_package_light_fragile):
    \"\"\"Provides a ShippingService with some pre-created shipments, using the mocked repo.\"\"\"
    service = empty_shipping_service
    service.create_shipment([example_package_heavy], example_address_origin, example_address_destination)
    service.create_shipment([example_package_light_fragile], example_address_destination, example_address_origin)
    return service

# TODO: Użyj Copilot Agent Mode, aby wygenerować fixture'y, które symulują różne stany baz danych (np. pustą, z istniejącymi danymi),
# jeśli ShipmentRepository zostanie zmienione na bardziej realistyczną implementację.
# TODO: Użyj Copilot inline suggestions, aby dodać fixture wykorzystującą `tmp_path` dla testowania operacji na plikach.

import pytest
from datetime import datetime, timedelta
from src.logistics.models import Address, Package, Shipment
from src.logistics.shipping_service import ShippingService, ShipmentRepository

# W Zadanie 4, Krok 3, użyjesz Copilot Agent Mode tutaj, aby zaktualizować testy po refaktoryzacji ShippingService.
# Upewnij się, że testy poprawnie obsługują wstrzyknięcie ShipmentRepository.

@pytest.fixture
def mock_shipment_repository():
    """Fixture providing a mocked ShipmentRepository."""
    repo = ShipmentRepository()
    return repo

@pytest.fixture
def shipping_service_with_mock_repo(mock_shipment_repository):
    return ShippingService(shipment_repo=mock_shipment_repository)

@pytest.fixture
def sample_address_origin():
    return Address(street="123 Main St", city="Anytown", zip_code="12345", country="USA")

@pytest.fixture
def sample_address_destination():
    return Address(street="456 Oak Ave", city="Otherville", zip_code="67890", country="USA")

@pytest.fixture
def sample_package_fragile():
    return Package(package_id="PKG001", weight_kg=1.5, dimensions_cm=(10, 10, 10), fragile=True)

@pytest.fixture
def sample_package_standard():
    return Package(package_id="PKG002", weight_kg=5.0, dimensions_cm=(20, 15, 10), fragile=False)

# W Zadanie 2, Krok 2, użyjesz @workspace tutaj, aby wygenerować kompleksowe testy jednostkowe dla `ShippingService` methods.
# Na przykład, upewnij się, że wszystkie pola utworzonej przesyłki są aserowane.
def test_create_shipment(shipping_service_with_mock_repo, sample_package_standard, sample_address_origin, sample_address_destination):
    shipment = shipping_service_with_mock_repo.create_shipment([sample_package_standard], sample_address_origin, sample_address_destination)
    assert shipment is not None
    assert shipment.shipment_id.startswith("SHP-")
    assert shipment.status == "PENDING"
    assert shipment.packages[0].package_id == "PKG002"
    assert shipment.origin == sample_address_origin
    assert shipment.destination == sample_address_destination
    assert shipping_service_with_mock_repo.shipment_repo.find_by_id(shipment.shipment_id) == shipment


def test_get_shipment_status_found(shipping_service_with_mock_repo, sample_package_standard, sample_address_origin, sample_address_destination):
    created_shipment = shipping_service_with_mock_repo.create_shipment([sample_package_standard], sample_address_origin, sample_address_destination)
    retrieved_shipment = shipping_service_with_mock_repo.get_shipment_status(created_shipment.shipment_id)
    assert retrieved_shipment == created_shipment

# W Zadanie 2, Krok 2, użyjesz @workspace (lub Copilot Chat) do wygenerowania testu dla przypadku nieznalezionego ID.
def test_get_shipment_status_not_found(shipping_service_with_mock_repo):
    retrieved_shipment = shipping_service_with_mock_repo.get_shipment_status("NONEXISTENT-ID")
    assert retrieved_shipment is None

def test_update_shipment_status(shipping_service_with_mock_repo, sample_package_standard, sample_address_origin, sample_address_destination):
    created_shipment = shipping_service_with_mock_repo.create_shipment([sample_package_standard], sample_address_origin, sample_address_destination)
    updated_shipment = shipping_service_with_mock_repo.update_shipment_status(created_shipment.shipment_id, "SHIPPED")
    assert updated_shipment is not None
    assert updated_shipment.status == "SHIPPED"
    assert "Status updated to SHIPPED" in updated_shipment.tracking_history[-1]
    # TODO: Użyj Copilot Chat, aby dodać test aktualizacji statusu do nieprawidłowego stanu (jeśli zdefiniowano dozwolone stany).

def test_calculate_shipping_cost_standard(shipping_service_with_mock_repo, sample_package_standard, sample_address_origin, sample_address_destination):
    shipment = shipping_service_with_mock_repo.create_shipment([sample_package_standard], sample_address_origin, sample_address_destination)
    cost = shipping_service_with_mock_repo.calculate_shipping_cost(shipment)
    expected_cost = sample_package_standard.weight_kg * 5.0
    assert cost == expected_cost

def test_calculate_shipping_cost_fragile(shipping_service_with_mock_repo, sample_package_fragile, sample_address_origin, sample_address_destination):
    shipment = shipping_service_with_mock_repo.create_shipment([sample_package_fragile], sample_address_origin, sample_address_destination)
    cost = shipping_service_with_mock_repo.calculate_shipping_cost(shipment)
    expected_cost = (sample_package_fragile.weight_kg * 5.0) + 10.0
    assert cost == expected_cost

# W Zadanie 2, Krok 4, użyjesz Copilot Chat tutaj, aby dodać test przypadku `calculate_shipping_cost` z wieloma paczkami (kruche + standardowe).
def test_calculate_shipping_cost_multiple_packages(shipping_service_with_mock_repo, sample_package_fragile, sample_package_standard, sample_address_origin, sample_address_destination):
    shipment = shipping_service_with_mock_repo.create_shipment([sample_package_fragile, sample_package_standard], sample_address_origin, sample_address_destination)
    cost = shipping_service_with_mock_repo.calculate_shipping_cost(shipment)
    expected_cost = (sample_package_fragile.weight_kg + sample_package_standard.weight_kg) * 5.0 + 10.0 # fragile surcharge applied once
    assert cost == expected_cost

def test_estimate_delivery_time(shipping_service_with_mock_repo, sample_package_standard, sample_address_origin, sample_address_destination):
    shipment = shipping_service_with_mock_repo.create_shipment([sample_package_standard], sample_address_origin, sample_address_destination)
    estimated_time = shipping_service_with_mock_repo.estimate_delivery_time(shipment)
    assert isinstance(estimated_time, datetime)
    assert estimated_time > datetime.now()
    assert estimated_time < datetime.now() + timedelta(days=5) # Assuming simple estimation

# W Zadanie 4, Krok 3, użyjesz Copilot Agent Mode tutaj, aby upewnić się, że testy działają poprawnie po refaktoryzacji
# i mockowaniu ShipmentRepository.
# TODO: Użyj Copilot Agent Mode do wygenerowania testów dla `ShipmentRepository` (jeśli to jest odrębne zadanie).

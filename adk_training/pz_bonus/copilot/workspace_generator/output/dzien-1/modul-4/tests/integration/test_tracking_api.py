import pytest
import requests_mock
import requests
from datetime import datetime, timedelta
from src.logistics.models import Address, Package, Shipment
from src.logistics.shipping_service import ShippingService, ShipmentRepository
from freezegun import freeze_time # Recommended for time simulation in tests

# Wymagane do Zadania 3, Krok 2 - może być potrzebna instalacja: pip install freezegun

# Mock external API response for tracking
@pytest.fixture
def mock_tracking_api(requests_mock):
    requests_mock.get(
        "https://api.externaltracker.com/track/SHP-00001",
        json={
            "shipment_id": "SHP-00001",
            "current_status": "IN_TRANSIT",
            "last_location": "Warehouse A, New York",
            "estimated_delivery": (datetime.now() + timedelta(days=2)).isoformat()
        },
        status_code=200
    )
    requests_mock.get(
        "https://api.externaltracker.com/track/SHP-NOTFOUND",
        json={"error": "Shipment not found"},
        status_code=404
    )
    # W Zadanie 3, Krok 2, użyjesz Copilot Agent Mode tutaj, aby dodać bardziej złożone scenariusze mockowania
    # dla SHP-00002, symulując np. DELIVERY_ATTEMPT_FAILED, a następnie DELIVERED.
    requests_mock.get(
        "https://api.externaltracker.com/track/SHP-00002",
        [
            {'json': {"shipment_id": "SHP-00002", "current_status": "DELIVERY_ATTEMPT_FAILED", "last_location": "Customer Door", "timestamp": (datetime.now() + timedelta(days=2)).isoformat()}, 'status_code': 200},
            {'json': {"shipment_id": "SHP-00002", "current_status": "DELIVERED", "last_location": "Customer Door", "timestamp": (datetime.now() + timedelta(days=3)).isoformat()}, 'status_code': 200}
        ]
    )


def test_external_tracking_api_success(mock_tracking_api):
    shipment_id = "SHP-00001"
    response = requests.get(f"https://api.externaltracker.com/track/{shipment_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["shipment_id"] == shipment_id
    assert data["current_status"] == "IN_TRANSIT"
    # TODO: Użyj Copilot Workspace, aby zintegrować to wywołanie API do ShippingService i stworzyć kompleksowy test.

def test_external_tracking_api_not_found(mock_tracking_api):
    shipment_id = "SHP-NOTFOUND"
    response = requests.get(f"https://api.externaltracker.com/track/{shipment_id}")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    # TODO: Użyj Copilot inline suggestions, aby dodać test dla obsługi innych błędów HTTP (np. 500 Internal Server Error).

# W Zadanie 3, Krok 2, użyjesz Copilot Agent Mode do wygenerowania testu integracyjnego, który weryfikuje złożony przepływ statusów dla SHP-00002.
# Użyj freezegun do symulacji upływu czasu.
def test_external_tracking_api_complex_status_flow(mock_tracking_api):
    shipment_id = "SHP-00002"
    with freeze_time(datetime.now() + timedelta(days=2)):
        response1 = requests.get(f"https://api.externaltracker.com/track/{shipment_id}")
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["current_status"] == "DELIVERY_ATTEMPT_FAILED"

    with freeze_time(datetime.now() + timedelta(days=3)):
        response2 = requests.get(f"https://api.externaltracker.com/track/{shipment_id}")
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["current_status"] == "DELIVERED"

    # W Zadanie 3, Krok 3, zastosuj pętlę samokorekcji, jeśli ten test wymaga dopracowania.
    # Na przykład, poproś Copilota o dodanie więcej asercji lub lepsze zarządzanie stanem czasu.


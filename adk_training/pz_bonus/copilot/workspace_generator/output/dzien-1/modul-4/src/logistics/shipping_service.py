from datetime import datetime, timedelta
from typing import List, Optional
from src.logistics.models import Shipment, Package, Address
import requests # Added for Zadanie 3, Step 4

# Zadanie 4: Refaktoryzacja ShippingService z użyciem ShipmentRepository
# W Zadanie 4, Krok 2, użyjesz @workspace, aby wydzielić logikę dostępu do danych do nowej klasy ShipmentRepository.
# ShippingService powinien wtedy przyjmować instancję ShipmentRepository w konstruktorze.

class ShipmentRepository:
    def __init__(self):
        self._shipments: List[Shipment] = []

    def save(self, shipment: Shipment):
        self._shipments.append(shipment)
        # TODO: Use Copilot to add structured logging here for saving shipments.

    def find_by_id(self, shipment_id: str) -> Optional[Shipment]:
        # TODO: Use Copilot Workspace to optimize this lookup for very large datasets, e.g., by using a dictionary for faster access.
        return next((s for s in self._shipments if s.shipment_id == shipment_id), None)

    def update(self, updated_shipment: Shipment):
        for i, shipment in enumerate(self._shipments):
            if shipment.shipment_id == updated_shipment.shipment_id:
                self._shipments[i] = updated_shipment
                return
        # TODO: Use Copilot to implement error handling if shipment not found for update.

class ShippingService:
    def __init__(self, shipment_repo: ShipmentRepository = None):
        self.shipment_repo = shipment_repo if shipment_repo is not None else ShipmentRepository()
        # W Zadanie 4, Krok 2, użyjesz @workspace do refaktoryzacji tej klasy, aby używała ShipmentRepository.

    def create_shipment(self, packages: List[Package], origin: Address, destination: Address) -> Shipment:
        shipment_id = f"SHP-{len(self.shipment_repo._shipments) + 1:05d}" # Adjust ID generation based on repo state
        new_shipment = Shipment(
            shipment_id=shipment_id,
            packages=packages,
            origin=origin,
            destination=destination
        )
        self.shipment_repo.save(new_shipment)
        # TODO: Użyj Copilot inline suggestions tutaj, aby dodać logowanie zdarzenia utworzenia przesyłki.
        return new_shipment

    def get_shipment_status(self, shipment_id: str) -> Optional[Shipment]:
        return self.shipment_repo.find_by_id(shipment_id)

    def update_shipment_status(self, shipment_id: str, new_status: str) -> Optional[Shipment]:
        shipment = self.get_shipment_status(shipment_id)
        if shipment:
            shipment.status = new_status
            shipment.update_tracking_history(f"Status updated to {new_status}") # Using new method from models.py
            self.shipment_repo.update(shipment)
            # TODO: Użyj Copilot inline suggestions tutaj, aby zaimplementować mechanizm powiadomień (e.g., email, webhook) po zmianie statusu.
            return shipment
        return None

    def calculate_shipping_cost(self, shipment: Shipment) -> float:
        base_cost_per_kg = 5.0
        fragile_surcharge = 10.0
        total_weight = sum(pkg.weight_kg for pkg in shipment.packages)
        cost = total_weight * base_cost_per_kg

        if any(pkg.fragile for pkg in shipment.packages):
            cost += fragile_surcharge
        
        # TODO: Użyj Copilot inline suggestions tutaj, aby dodać obsługę rabatów dla dużych przesyłek (>100kg).

        # TODO: Użyj Copilot Agent Mode do integracji z zewnętrznym API do dynamicznego obliczania kosztów
        # na podstawie odległości i aktualnych cen paliwa. To zadanie może być częścią większej refaktoryzacji.
        return cost

    def estimate_delivery_time(self, shipment: Shipment) -> datetime:
        # Simple estimation: 2-5 days
        # TODO: Użyj Copilot Agent Mode do symulacji złożonego algorytmu optymalizacji trasy dostawy,
        # uwzględniającego zmienne takie jak pogoda, ruch drogowy i dostępność kurierów.
        return datetime.now() + timedelta(days=3) # Placeholder

    # W Zadanie 3, Krok 4, użyjesz Copilot inline suggestions tutaj, aby zaimplementować `track_shipment_external(shipment_id: str)`.
    # Ta metoda powinna wysłać zapytanie GET do https://api.externaltracker.com/track/{shipment_id} i zwrócić odpowiedź JSON.
    def track_shipment_external(self, shipment_id: str) -> Optional[dict]:
        try:
            response = requests.get(f"https://api.externaltracker.com/track/{shipment_id}")
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error tracking shipment {shipment_id} externally: {e}")
            return None

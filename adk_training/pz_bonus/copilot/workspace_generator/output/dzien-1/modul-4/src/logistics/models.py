from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import re # Needed for postal code validation

@dataclass
class Address:
    street: str
    city: str
    zip_code: str
    country: str

    # W Zadanie 1, Krok 2, użyjesz Copilot Chat tutaj, aby dodać metodę `validate_address` do Address.
    # Przykład: Poproś o walidację formatu kodu pocztowego dla USA (np. 5 cyfr lub 5+4).
    def validate_address(self) -> bool:
        if self.country == "USA":
            # Example: 5 digits or 5 digits + 4 digits
            if not re.fullmatch(r"\d{5}(-\d{4})?", self.zip_code):
                return False
        # TODO: Use Copilot Chat to add validation for other countries, e.g., UK postcodes.
        return True


@dataclass
class Package:
    package_id: str
    weight_kg: float
    dimensions_cm: tuple[float, float, float]  # (length, width, height)
    fragile: bool = False

    # W Zadanie 1, Krok 3, użyjesz Copilot inline suggestions tutaj, aby dodać metodę `calculate_volumetric_weight`.
    # Przyjmij wzór: (length * width * height) / 5000
    def calculate_volumetric_weight(self) -> float:
        length, width, height = self.dimensions_cm
        return (length * width * height) / 5000.0


@dataclass
class Shipment:
    shipment_id: str
    packages: List[Package]
    origin: Address
    destination: Address
    status: str = "PENDING"
    estimated_delivery: Optional[datetime] = None
    tracking_history: List[str] = None # type: ignore

    def __post_init__(self):
        if self.tracking_history is None:
            self.tracking_history = [f"Shipment {self.shipment_id} created at {datetime.now().isoformat()}"]

    # W Zadanie 1, Krok 4, użyjesz Copilot inline suggestions tutaj, aby dodać metodę `update_tracking_history(event: str)`.
    def update_tracking_history(self, event: str):
        self.tracking_history.append(f"{event} at {datetime.now().isoformat()}")
        # TODO: Use Copilot to automatically update `estimated_delivery` based on certain events (e.g., 'DELIVERED')

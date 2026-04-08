"""
Module for defining data models in the Healthcare / Medical Records domain.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class Patient:
    """
    Represents a patient in the medical system.
    """
    patient_id: str
    first_name: str
    last_name: str
    date_of_birth: datetime
    gender: str
    contact_number: Optional[str] = None
    address: Optional[str] = None

    # TODO: Use Copilot to add validation logic for patient data (e.g., age, valid gender)
    # TODO: Refactor date_of_birth to a more robust date type or custom validation
    # TODO: Consider adding an 'is_active' status to patients.

@dataclass
class MedicalRecord:
    """
    Represents a single medical record entry for a patient.
    """
    record_id: str
    patient_id: str
    record_date: datetime
    diagnosis: str
    treatment: str
    prescribed_medication: List[str]
    doctor_id: str
    notes: Optional[str] = None

    # TODO: Use Copilot to implement a method to calculate the age of the patient at the time of record.
    # TODO: Enhance 'prescribed_medication' to include dosage and frequency using a nested dataclass.
    # TODO: Refactor 'diagnosis' to use a structured vocabulary (e.g., ICD codes) instead of free text.

@dataclass
class Doctor:
    """
    Represents a doctor in the medical system.
    """
    doctor_id: str
    first_name: str
    last_name: str
    specialization: str
    contact_number: Optional[str] = None

    # TODO: Use Copilot to add a method to associate doctors with patients they treat.
    # TODO: Implement validation for doctor's specialization from a predefined list.

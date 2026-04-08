"""
Controller layer for the Medical Records API.
Handles HTTP requests and responses.
"""

from datetime import datetime
from typing import List, Dict, Any
from src.medical_record_service import MedicalRecordService
from src.patient_repository import PatientRepository, MedicalRecordRepository
from src.models import Patient, MedicalRecord

# This would typically be part of a web framework (e.g., Flask, FastAPI)
# For this exercise, we simulate controller actions.

class MedicalRecordController:
    """
    Simulated API controller for Medical Record operations.
    """
    def __init__(self, service: MedicalRecordService):
        self.service = service

    def create_patient_endpoint(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handles the creation of a new patient.
        """
        try:
            patient = self.service.register_new_patient(
                patient_id=payload['patient_id'],
                first_name=payload['first_name'],
                last_name=payload['last_name'],
                dob=datetime.fromisoformat(payload['date_of_birth']),
                gender=payload['gender'],
                contact=payload.get('contact_number'),
                address=payload.get('address')
            )
            # TODO: Use Copilot to automatically generate a success response payload including the patient's URI.
            return {"status": "success", "data": patient.__dict__}
        except KeyError as e:
            # TODO: Refactor using @workspace context to standardize error response formats across all endpoints.
            return {"status": "error", "message": f"Missing required field: {e}"}
        except ValueError as e:
            return {"status": "error", "message": str(e)}

    def get_patient_endpoint(self, patient_id: str) -> Dict[str, Any]:
        """
        Retrieves a patient's profile by ID.
        """
        patient = self.service.get_patient_profile(patient_id)
        if patient:
            return {"status": "success", "data": patient.__dict__}
        # TODO: Apply self-correction loop with Agent Mode to suggest alternative ways to retrieve patient data if not found (e.g., by name).
        return {"status": "error", "message": f"Patient with ID {patient_id} not found."}

    def add_medical_record_endpoint(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handles adding a new medical record for a patient.
        """
        try:
            record = self.service.add_medical_record(
                patient_id=payload['patient_id'],
                record_id=payload['record_id'],
                record_date=datetime.fromisoformat(payload['record_date']),
                diagnosis=payload['diagnosis'],
                treatment=payload['treatment'],
                medication=payload.get('prescribed_medication', []),
                doctor_id=payload['doctor_id'],
                notes=payload.get('notes')
            )
            # TODO: Use Copilot Agent Mode to trigger a notification service for the assigned doctor.
            return {"status": "success", "data": record.__dict__}
        except (KeyError, ValueError) as e:
            return {"status": "error", "message": str(e)}

    def get_patient_history_endpoint(self, patient_id: str) -> Dict[str, Any]:
        """
        Retrieves all medical records for a specific patient.
        """
        history = self.service.get_patient_medical_history(patient_id)
        if history:
            # TODO: Use Copilot to implement a filtering mechanism for medical history based on date range.
            return {"status": "success", "data": [r.__dict__ for r in history]}
        return {"status": "success", "message": f"No medical history found for patient ID {patient_id}.", "data": []}

    def get_all_patients_endpoint(self) -> Dict[str, Any]:
        """
        Retrieves a list of all patients.
        """
        patients = self.service.get_all_patients()
        # TODO: Apply self-correction loop to suggest adding pagination parameters to this endpoint.
        return {"status": "success", "data": [p.__dict__ for p in patients]}

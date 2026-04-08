"""
Service layer for managing medical records and patient information.
"""

from typing import List, Optional
from datetime import datetime
from src.models import Patient, MedicalRecord
from src.patient_repository import PatientRepository, MedicalRecordRepository

class MedicalRecordService:
    """
    Provides business logic for patient and medical record operations.
    """
    def __init__(self, patient_repo: PatientRepository, record_repo: MedicalRecordRepository):
        self.patient_repo = patient_repo
        self.record_repo = record_repo

    def register_new_patient(self, patient_id: str, first_name: str, last_name: str, dob: datetime, gender: str, contact: Optional[str] = None, address: Optional[str] = None) -> Patient:
        """
        Registers a new patient in the system.
        """
        new_patient = Patient(patient_id, first_name, last_name, dob, gender, contact, address)
        self.patient_repo.add_patient(new_patient)
        # TODO: Use Copilot to add an event publishing mechanism here (e.g., patient_registered_event).
        # TODO: Implement robust input validation for patient details before creation.
        return new_patient

    def get_patient_profile(self, patient_id: str) -> Optional[Patient]:
        """
        Retrieves a patient's profile.
        """
        patient = self.patient_repo.get_patient_by_id(patient_id)
        # TODO: Apply self-correction loop with Agent Mode to suggest alternative data sources if not found in primary repo.
        return patient

    def update_patient_contact_info(self, patient_id: str, new_contact: str) -> Patient:
        """
        Updates a patient's contact information.
        """
        patient = self.patient_repo.get_patient_by_id(patient_id)
        if not patient:
            raise ValueError(f"Patient with ID {patient_id} not found.")
        patient.contact_number = new_contact
        self.patient_repo.update_patient(patient)
        # TODO: Use Copilot Agent Mode to implement multi-file refactoring: ensure all related UIs/APIs reflect updated contact info.
        return patient

    def add_medical_record(self, patient_id: str, record_id: str, record_date: datetime, diagnosis: str, treatment: str, medication: List[str], doctor_id: str, notes: Optional[str] = None) -> MedicalRecord:
        """
        Adds a new medical record for a patient.
        """
        if not self.patient_repo.get_patient_by_id(patient_id):
            raise ValueError(f"Patient with ID {patient_id} does not exist.")

        new_record = MedicalRecord(record_id, patient_id, record_date, diagnosis, treatment, medication, doctor_id, notes)
        self.record_repo.add_record(new_record)
        # TODO: Refactor using @workspace context to automatically generate a summary report of the new record for the doctor.
        # TODO: Implement a system to check for drug interactions based on existing medications for the patient.
        return new_record

    def get_patient_medical_history(self, patient_id: str) -> List[MedicalRecord]:
        """
        Retrieves the complete medical history for a patient.
        """
        history = self.record_repo.get_records_by_patient_id(patient_id)
        # TODO: Use Copilot to implement a feature to redact sensitive information based on user roles.
        return history

    def get_all_patients(self) -> List[Patient]:
        """
        Retrieves all registered patients.
        """
        # TODO: Apply self-correction loop to optimize this for performance when dealing with millions of patients.
        return self.patient_repo.get_all_patients()

    def get_all_medical_records(self) -> List[MedicalRecord]:
        """
        Retrieves all medical records.
        """
        return self.record_repo.get_all_records()

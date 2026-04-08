"""
Main application entry point for the Medical Records System.
Demonstrates how to wire up the components.
"""

from datetime import datetime
from src.models import Patient, MedicalRecord
from src.patient_repository import PatientRepository, MedicalRecordRepository
from src.medical_record_service import MedicalRecordService
from src.medical_record_controller import MedicalRecordController
from config import get_config

# TODO: Use Copilot Agent Mode to refactor this main entry point into a proper FastAPI or Flask application structure.
# TODO: Refactor using @workspace context to include dependency injection for better testability and modularity.

def initialize_app():
    """
    Initializes repositories, service, and controller.
    """
    current_config = get_config()
    print(f"Using database: {current_config.DATABASE_URL}")

    # In-memory repositories for demonstration
    patient_repo = PatientRepository()
    record_repo = MedicalRecordRepository()

    service = MedicalRecordService(patient_repo, record_repo)
    controller = MedicalRecordController(service)

    return service, controller

def run_demo():
    service, controller = initialize_app()

    print("\n--- Demonstrating Patient Registration ---")
    try:
        patient_payload_1 = {
            "patient_id": "P001",
            "first_name": "Alice",
            "last_name": "Smith",
            "date_of_birth": "1990-01-15",
            "gender": "Female",
            "contact_number": "123-456-7890",
            "address": "101 Pine St"
        }
        response1 = controller.create_patient_endpoint(patient_payload_1)
        print(f"Registered Patient: {response1}")

        patient_payload_2 = {
            "patient_id": "P002",
            "first_name": "Bob",
            "last_name": "Johnson",
            "date_of_birth": "1985-03-22",
            "gender": "Male"
        }
        response2 = controller.create_patient_endpoint(patient_payload_2)
        print(f"Registered Patient: {response2}")

        # Try to register same patient again (should fail)
        response_fail = controller.create_patient_endpoint(patient_payload_1)
        print(f"Attempt to re-register P001: {response_fail}")

    except Exception as e:
        print(f"Error during patient registration: {e}")

    print("\n--- Demonstrating Medical Record Addition ---")
    try:
        record_payload_1 = {
            "patient_id": "P001",
            "record_id": "REC001",
            "record_date": "2023-01-20T10:00:00",
            "diagnosis": "Common Cold",
            "treatment": "Rest and fluids",
            "prescribed_medication": ["Paracetamol"],
            "doctor_id": "D001",
            "notes": "Patient presented with mild fever."
        }
        response3 = controller.add_medical_record_endpoint(record_payload_1)
        print(f"Added Medical Record: {response3}")

        record_payload_2 = {
            "patient_id": "P001",
            "record_id": "REC002",
            "record_date": "2023-02-10T14:30:00",
            "diagnosis": "Seasonal Allergies",
            "treatment": "Antihistamines",
            "prescribed_medication": ["Cetirizine"],
            "doctor_id": "D002"
        }
        response4 = controller.add_medical_record_endpoint(record_payload_2)
        print(f"Added Medical Record: {response4}")

        record_payload_3 = {
            "patient_id": "P002",
            "record_id": "REC003",
            "record_date": "2023-03-05T09:00:00",
            "diagnosis": "Annual Checkup",
            "treatment": "General health advice",
            "prescribed_medication": [],
            "doctor_id": "D001",
            "notes": "Healthy patient."
        }
        response5 = controller.add_medical_record_endpoint(record_payload_3)
        print(f"Added Medical Record: {response5}")

    except Exception as e:
        print(f"Error during record addition: {e}")

    print("\n--- Retrieving Patient Data ---")
    patient_profile = controller.get_patient_endpoint("P001")
    print(f"Patient P001 Profile: {patient_profile}")

    patient_history = controller.get_patient_history_endpoint("P001")
    print(f"Patient P001 History: {patient_history}")

    all_patients = controller.get_all_patients_endpoint()
    print(f"All Patients: {all_patients}")

    # TODO: Use Copilot to add a demonstration of updating patient contact info and then retrieving it to confirm.

if __name__ == "__main__":
    run_demo()

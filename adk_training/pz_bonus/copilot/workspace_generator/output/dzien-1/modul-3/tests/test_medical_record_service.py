"""
Unit tests for the MedicalRecordService.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock

from src.models import Patient, MedicalRecord
from src.patient_repository import PatientRepository, MedicalRecordRepository
from src.medical_record_service import MedicalRecordService

@pytest.fixture
def mock_patient_repository():
    """
    A pytest fixture to provide a mocked PatientRepository.
    """
    repo = Mock(spec=PatientRepository)
    # Pre-populate with some data if needed for specific tests
    repo._patients = {
        "P001": Patient("P001", "John", "Doe", datetime(1990, 5, 15), "Male"),
        "P002": Patient("P002", "Jane", "Smith", datetime(1985, 10, 20), "Female"),
    }
    repo.get_patient_by_id.side_effect = lambda patient_id: repo._patients.get(patient_id)
    repo.add_patient.side_effect = lambda patient: repo._patients.update({patient.patient_id: patient})
    repo.update_patient.side_effect = lambda patient: repo._patients.update({patient.patient_id: patient})
    repo.get_all_patients.side_effect = lambda: list(repo._patients.values())
    return repo

@pytest.fixture
def mock_medical_record_repository():
    """
    A pytest fixture to provide a mocked MedicalRecordRepository.
    """
    repo = Mock(spec=MedicalRecordRepository)
    # Pre-populate with some data
    repo._records = {
        "R001": MedicalRecord("R001", "P001", datetime(2023, 1, 10), "Flu", "Rest", ["Tamiflu"], "D001"),
        "R002": MedicalRecord("R002", "P001", datetime(2023, 3, 20), "Sprain", "RICE", ["Ibuprofen"], "D002"),
    }
    repo.add_record.side_effect = lambda record: repo._records.update({record.record_id: record})
    repo.get_records_by_patient_id.side_effect = lambda patient_id: [r for r in repo._records.values() if r.patient_id == patient_id]
    repo.get_record_by_id.side_effect = lambda record_id: repo._records.get(record_id)
    repo.get_all_records.side_effect = lambda: list(repo._records.values())
    return repo

@pytest.fixture
def medical_record_service(mock_patient_repository, mock_medical_record_repository):
    """
    A pytest fixture to provide a MedicalRecordService with mocked repositories.
    """
    return MedicalRecordService(mock_patient_repository, mock_medical_record_repository)


class TestMedicalRecordService:

    def test_register_new_patient(self, medical_record_service, mock_patient_repository):
        """
        Test registering a new patient.
        """
        new_patient = medical_record_service.register_new_patient(
            "P003", "Alice", "Johnson", datetime(2000, 1, 1), "Female", "111-222-3333", "123 Main St"
        )
        assert new_patient.patient_id == "P003"
        mock_patient_repository.add_patient.assert_called_once_with(new_patient)
        # TODO: Use Copilot Agent Mode to implement multi-file refactoring: update the mock patient repository to assert the state change correctly.

    def test_get_patient_profile(self, medical_record_service, mock_patient_repository):
        """
        Test retrieving an existing patient's profile.
        """
        patient = medical_record_service.get_patient_profile("P001")
        assert patient is not None
        assert patient.first_name == "John"
        mock_patient_repository.get_patient_by_id.assert_called_once_with("P001")
        # TODO: Refactor using @workspace context to add a test case for a non-existent patient and verify error handling.

    def test_get_patient_profile_not_found(self, medical_record_service, mock_patient_repository):
        """
        Test retrieving a non-existent patient's profile.
        """
        patient = medical_record_service.get_patient_profile("P999")
        assert patient is None
        mock_patient_repository.get_patient_by_id.assert_called_once_with("P999")

    def test_add_medical_record(self, medical_record_service, mock_medical_record_repository, mock_patient_repository):
        """
        Test adding a new medical record for an existing patient.
        """
        # Ensure patient exists in the mocked patient repository
        assert mock_patient_repository.get_patient_by_id("P001") is not None

        new_record = medical_record_service.add_medical_record(
            "P001", "R003", datetime(2023, 6, 1), "Cold", "Rest and fluids", [], "D003", "Patient felt unwell."
        )
        assert new_record.record_id == "R003"
        mock_medical_record_repository.add_record.assert_called_once_with(new_record)
        # TODO: Apply self-correction loop to add a test case that verifies the behavior when adding a record for a non-existent patient.

    def test_add_medical_record_non_existent_patient(self, medical_record_service, mock_medical_record_repository):
        """
        Test adding a medical record for a non-existent patient.
        """
        with pytest.raises(ValueError, match="Patient with ID P999 does not exist."):
            medical_record_service.add_medical_record(
                "P999", "R004", datetime(2023, 7, 1), "Headache", "Painkillers", [], "D004"
            )
        mock_medical_record_repository.add_record.assert_not_called()

    def test_get_patient_medical_history(self, medical_record_service, mock_medical_record_repository):
        """
        Test retrieving medical history for a patient.
        """
        history = medical_record_service.get_patient_medical_history("P001")
        assert len(history) == 2
        assert history[0].diagnosis == "Flu"
        assert history[1].diagnosis == "Sprain"
        mock_medical_record_repository.get_records_by_patient_id.assert_called_once_with("P001")
        # TODO: Use Copilot to add a test case for a patient with no medical history.

    def test_update_patient_contact_info(self, medical_record_service, mock_patient_repository):
        """
        Test updating a patient's contact information.
        """
        updated_patient = medical_record_service.update_patient_contact_info("P001", "555-123-4567")
        assert updated_patient.contact_number == "555-123-4567"
        mock_patient_repository.update_patient.assert_called_once_with(updated_patient)

    def test_get_all_patients(self, medical_record_service, mock_patient_repository):
        """
        Test retrieving all patients.
        """
        patients = medical_record_service.get_all_patients()
        assert len(patients) == 2
        mock_patient_repository.get_all_patients.assert_called_once()

    def test_get_all_medical_records(self, medical_record_service, mock_medical_record_repository):
        """
        Test retrieving all medical records.
        """
        records = medical_record_service.get_all_medical_records()
        assert len(records) == 2
        mock_medical_record_repository.get_all_records.assert_called_once()

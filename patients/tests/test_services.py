# patients/tests/test_services.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from patients.services import add_favorite_doctor, upload_medical_record
from patients.models import SavedDoctor, MedicalRecord
from django.core.files.uploadedfile import SimpleUploadedFile

# Use Django's dynamic user model reference
User = get_user_model()

class PatientServiceTests(TestCase):
    """
    Unit tests for patients.services module.
    These tests validate business logic for saving doctors and uploading medical records.
    """

    def setUp(self):
        # Create a test user to simulate an authenticated patient
        self.user = User.objects.create_user(username='waqar', password='test123')

    def test_add_favorite_doctor(self):
        """
        Test that a doctor can be successfully saved to a patient's favorites.
        """
        obj, created = add_favorite_doctor(self.user, doctor_id=42)

        # Assert that the object was created
        self.assertTrue(created)

        # Assert that the correct doctor ID was saved
        self.assertEqual(obj.doctor_id, 42)

        # Assert that the saved doctor is linked to the correct patient profile
        self.assertEqual(obj.patient.user, self.user)

    def test_upload_medical_record(self):
        """
        Test that a medical record file can be uploaded and linked to the patient.
        """
        # Create a dummy file for upload
        file = SimpleUploadedFile("report.txt", b"Test content")

        # Call the service to upload the record
        record = upload_medical_record(self.user, "Blood Test", file, "Routine check")

        # Assert that the record was created with correct metadata
        self.assertEqual(record.title, "Blood Test")
        self.assertEqual(record.notes, "Routine check")
        self.assertEqual(record.patient.user, self.user)

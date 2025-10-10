# prescriptions/tests/test_services.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from prescriptions.services import PrescriptionService
from prescriptions.models import Prescription

User = get_user_model()

class PrescriptionServiceTests(TestCase):
    def setUp(self):
        self.patient = User.objects.create_user(username="patient2", email="p2@example.com", password="pass")
        self.doctor = User.objects.create_user(username="doc2", email="d2@example.com", password="pass")
        self.service = PrescriptionService()

    def test_create_prescription_with_meds(self):
        meds = [{"name": "Med A", "dosage": "10mg", "quantity": 2}]
        pres = self.service.create_prescription(patient=self.patient, doctor=self.doctor, notes="note", medications=meds)
        self.assertIsInstance(pres, Prescription)
        self.assertEqual(pres.medications.count(), 1)
        self.assertIn("Med A", pres.summary)

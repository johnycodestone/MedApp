# prescriptions/tests/test_models.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from prescriptions.models import Prescription, Medication

User = get_user_model()

class PrescriptionModelTests(TestCase):
    def setUp(self):
        self.patient = User.objects.create_user(username="patient1", email="p@example.com", password="pass")
        self.doctor = User.objects.create_user(username="doc1", email="d@example.com", password="pass")

    def test_create_prescription_and_medication(self):
        p = Prescription.objects.create(patient=self.patient, doctor=self.doctor, notes="Test")
        m = Medication.objects.create(prescription=p, name="Paracetamol", dosage="500mg", quantity=10)
        self.assertEqual(p.medications.count(), 1)
        self.assertEqual(str(p), f"Prescription #{p.id} for {p.patient}")
        self.assertIn("Paracetamol", str(m))

    def test_finalize_and_revoke(self):
        p = Prescription.objects.create(patient=self.patient)
        p.finalize()
        self.assertEqual(p.status, Prescription.STATUS_FINAL)
        p.revoke()
        self.assertEqual(p.status, Prescription.STATUS_REVOKED)

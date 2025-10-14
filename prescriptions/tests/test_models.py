from django.test import TestCase
from .models import Prescription, Medication
from doctors.models import DoctorProfile
from patients.models import PatientProfile
from django.contrib.auth.models import User

class PrescriptionModelTest(TestCase):
    def test_create_prescription(self):
        doctor_user = User.objects.create(username='doc')
        patient_user = User.objects.create(username='pat')
        doctor = DoctorProfile.objects.create(user=doctor_user)
        patient = PatientProfile.objects.create(user=patient_user)

        prescription = Prescription.objects.create(doctor=doctor, patient=patient, notes="Take rest")
        self.assertEqual(str(prescription), f"Prescription #{prescription.id} for {patient_user.get_full_name()}")

from django.test import TestCase
from .services import create_prescription_with_medications
from doctors.models import DoctorProfile
from patients.models import PatientProfile
from django.contrib.auth.models import User

class PrescriptionServiceTest(TestCase):
    def test_create_prescription_with_meds(self):
        doc_user = User.objects.create(username='doc')
        pat_user = User.objects.create(username='pat')
        doctor = DoctorProfile.objects.create(user=doc_user)
        patient = PatientProfile.objects.create(user=pat_user)

        data = {
            'patient': patient,
            'notes': 'Hydrate well',
            'medications': [
                {'name': 'Paracetamol', 'dosage': '500mg', 'frequency': '2x/day', 'duration': '5 days'}
            ]
        }

        prescription = create_prescription_with_medications(data, doc_user)
        self.assertEqual(prescription.medications.count(), 1)

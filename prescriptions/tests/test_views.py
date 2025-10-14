from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Prescription
from patients.models import PatientProfile
from doctors.models import DoctorProfile

class PrescriptionViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.patient = PatientProfile.objects.create(user=self.user)

    def test_prescription_list_view(self):
        self.client.login(username='testuser', password='pass')
        response = self.client.get('/prescriptions/')
        self.assertEqual(response.status_code, 200)

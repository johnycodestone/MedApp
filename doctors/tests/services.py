from django.test import TestCase
from django.contrib.auth import get_user_model
from doctors.services import ensure_doctor_profile

User = get_user_model()

class DoctorServiceTests(TestCase):
    def test_profile_creation(self):
        user = User.objects.create_user(username="dr1", password="12345")
        doc = ensure_doctor_profile(user, specialization="Cardiology")
        self.assertEqual(doc.specialization, "Cardiology")

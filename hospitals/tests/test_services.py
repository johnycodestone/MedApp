from django.test import TestCase
from django.contrib.auth import get_user_model
from hospitals.services import register_hospital

User = get_user_model()

class HospitalServiceTests(TestCase):
    def test_register_hospital_creates_profile(self):
        user = User.objects.create_user(username="h1", password="pass")
        hospital = register_hospital(user, "City Hospital")
        self.assertEqual(hospital.name, "City Hospital")

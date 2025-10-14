from django.test import TestCase
from django.contrib.auth import get_user_model
from hospitals.models import Hospital, Department

User = get_user_model()

class HospitalModelTests(TestCase):
    def setUp(self):
        # Create a real user first since Hospital has FK to User
        self.user = User.objects.create_user(username="admin", password="123", first_name="City", last_name="Admin")
        # Create a hospital linked to that user
        self.hospital = Hospital.objects.create(user=self.user, name="Medicity")

    def test_create_hospital(self):
        self.assertEqual(str(self.hospital), "Medicity")

    def test_create_department(self):
        dept = Department.objects.create(hospital=self.hospital, name="Cardiology")
        self.assertIn("Cardiology", str(dept))
        self.assertIn("Medicity", str(dept))

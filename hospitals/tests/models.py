from django.test import TestCase
from hospitals.models import Hospital, Department

class HospitalModelTests(TestCase):
    def test_create_hospital(self):
        hospital = Hospital.objects.create(user_id=1, name="Medicity")
        self.assertEqual(str(hospital), "Medicity")

    def test_create_department(self):
        dept = Department.objects.create(hospital_id=1, name="Cardiology")
        self.assertEqual(str(dept), "Cardiology (Hospital 1)")

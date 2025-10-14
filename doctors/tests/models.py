from django.test import TestCase
from doctors.models import DoctorProfile, Timetable

class DoctorModelTests(TestCase):
    def test_doctor_profile_str(self):
        doc = DoctorProfile.objects.create(user_id=1, specialization="Dermatology")
        self.assertIn("Dermatology", str(doc))

    def test_timetable_str(self):
        tt = Timetable.objects.create(doctor_id=1, file="file.pdf")
        self.assertIn("Timetable", str(tt))

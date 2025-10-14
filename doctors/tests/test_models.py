from django.test import TestCase
from django.contrib.auth import get_user_model
from doctors.models import DoctorProfile, Timetable

User = get_user_model()

class DoctorModelTests(TestCase):
    def setUp(self):
        # Create a real user first (since DoctorProfile has FK to User)
        self.user = User.objects.create_user(username="drsmith", password="123", first_name="John", last_name="Smith")
        # Then create the doctor profile linked to that user
        self.doctor = DoctorProfile.objects.create(user=self.user, specialization="Dermatology")

    def test_doctor_profile_str(self):
        self.assertIn("Dermatology", str(self.doctor))
        self.assertIn("Dr.", str(self.doctor))

    def test_timetable_str(self):
        # Create a timetable linked to the existing doctor
        timetable = Timetable.objects.create(doctor=self.doctor, file="schedule.pdf")
        self.assertIn("Timetable", str(timetable))
        self.assertIn("Dr.", str(timetable.doctor))

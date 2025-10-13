from django.test import TestCase
from django.contrib.auth import get_user_model
from appointments.models import Appointment, AppointmentStatus
from datetime import datetime, timedelta

User = get_user_model()

class AppointmentModelTest(TestCase):
    def setUp(self):
        self.patient = User.objects.create_user(username='patient1', password='pass')
        self.doctor = User.objects.create_user(username='doctor1', password='pass')

    def test_create_appointment(self):
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            scheduled_time=datetime.now() + timedelta(days=1),
            reason="Routine checkup"
        )
        self.assertEqual(appointment.status, AppointmentStatus.PENDING)
        self.assertEqual(str(appointment), f"{self.patient.username} with {self.doctor.username} at {appointment.scheduled_time}")

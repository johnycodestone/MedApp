from django.test import TestCase
from django.contrib.auth import get_user_model
from appointments.services import AppointmentService
from datetime import datetime, timedelta

User = get_user_model()

class AppointmentServiceTest(TestCase):
    def setUp(self):
        self.patient = User.objects.create_user(username='patient2', password='pass')
        self.doctor = User.objects.create_user(username='doctor2', password='pass')
        self.scheduled_time = datetime.now() + timedelta(days=2)

    def test_create_and_cancel_appointment(self):
        appointment = AppointmentService.create_appointment(
            patient=self.patient,
            doctor=self.doctor,
            scheduled_time=self.scheduled_time,
            reason="Consultation"
        )
        self.assertEqual(appointment.status, 'pending')

        cancelled = AppointmentService.cancel_appointment(appointment.id, self.patient)
        self.assertEqual(cancelled.status, 'cancelled')

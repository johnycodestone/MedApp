from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from appointments.models import Appointment
from datetime import datetime, timedelta

User = get_user_model()

class AppointmentViewTest(APITestCase):
    def setUp(self):
        self.patient = User.objects.create_user(username='patient3', password='pass')
        self.doctor = User.objects.create_user(username='doctor3', password='pass')
        self.client.login(username='patient3', password='pass')

    def test_create_appointment_api(self):
        url = '/appointments/'
        data = {
            'doctor': self.doctor.id,
            'scheduled_time': (datetime.now() + timedelta(days=3)).isoformat(),
            'reason': 'Follow-up'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'pending')

from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from appointments.models import Appointment
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class AppointmentViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.patient = User.objects.create_user(username='patient3', password='pass')
        self.doctor = User.objects.create_user(username='doctor3', password='pass')
        self.client.force_authenticate(user=self.patient)  # ✅ This is the key fix

    def test_create_appointment_api(self):
        url = '/appointments/'
        data = {
            'doctor': self.doctor.id,
            'scheduled_time': (timezone.now() + timedelta(days=3)).isoformat(),
            'reason': 'Follow-up'
        }
        response = self.client.post(url, data, format='json')
        print("STATUS:", response.status_code)
        print("DATA:", response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'pending')

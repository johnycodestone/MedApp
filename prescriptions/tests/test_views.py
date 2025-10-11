# prescriptions/tests/test_views.py
from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from prescriptions.models import Prescription

User = get_user_model()

class PrescriptionAPITests(APITestCase):
    def setUp(self):
        self.patient = User.objects.create_user(username="patient3", email="p3@example.com", password="pass")
        self.doctor = User.objects.create_user(username="doc3", email="d3@example.com", password="pass")
        self.client.login(username="patient3", password="pass")

    def test_create_and_list_prescription(self):
        url = reverse("prescription-list")
        payload = {
            "patient": self.patient.id,
            "doctor": self.doctor.id,
            "notes": "Created via API",
            "medications": [{"name": "A", "quantity": 1}]
        }
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get(url)
        self.assertEqual(list_resp.status_code, 200)
        self.assertTrue(len(list_resp.data) >= 1)

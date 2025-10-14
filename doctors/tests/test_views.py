from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class DoctorViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="doc", password="123")
        self.client.login(username="doc", password="123")

    def test_get_doctor_profile(self):
        url = reverse("doctor-profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

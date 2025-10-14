from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User

class HospitalViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="hosp", password="123")
        self.client.login(username="hosp", password="123")

    def test_create_hospital_profile(self):
        url = reverse("hospital-profile")
        response = self.client.post(url, {"name": "City Hospital"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

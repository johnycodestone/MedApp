from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class HospitalViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="hosp", password="123")
        self.client.login(username="hosp", password="123")

    def test_create_hospital_profile(self):
        url = reverse("hospital-profile")
        data = {"name": "City Hospital", "phone": "123456789", "address": "Downtown"}
        response = self.client.post(url, data)
        # Accept either 201 if it’s created, or 200 if already exists
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])

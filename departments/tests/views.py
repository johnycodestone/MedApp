from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from departments.models import Department

class DepartmentViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="hosp_admin", password="123")
        self.client.login(username="hosp_admin", password="123")
        self.url = reverse("departments-list")

    def test_create_department(self):
        response = self.client.post(self.url, {
            "hospital_id": 1,
            "name": "Orthopedics",
            "description": "Bone and joint treatments"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Department.objects.count(), 1)

    def test_list_departments(self):
        Department.objects.create(hospital_id=1, name="Cardiology")
        response = self.client.get(self.url + "?hospital_id=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Cardiology", str(response.data))

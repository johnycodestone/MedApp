from django.test import TestCase
from departments.services import add_department, delete_department, get_departments_for_hospital
from departments.models import Department
from django.core.exceptions import ValidationError

class DepartmentServiceTests(TestCase):
    def test_add_department(self):
        dept = add_department(1, "Cardiology", "Heart-related care")
        self.assertEqual(dept.name, "Cardiology")

    def test_prevent_duplicate_department(self):
        add_department(1, "Dermatology")
        with self.assertRaises(ValidationError):
            add_department(1, "Dermatology")

    def test_delete_department(self):
        add_department(1, "Radiology")
        delete_department(1, "Radiology")
        self.assertEqual(Department.objects.count(), 0)

    def test_list_departments(self):
        add_department(1, "ENT")
        add_department(1, "Pediatrics")
        result = get_departments_for_hospital(1)
        self.assertEqual(len(result), 2)

from django.test import TestCase
from departments.models import Department

class DepartmentModelTests(TestCase):
    def test_department_str_method(self):
        dept = Department.objects.create(hospital_id=1, name="Neurology")
        self.assertEqual(str(dept), "Neurology (Hospital 1)")

    def test_unique_together_constraint(self):
        Department.objects.create(hospital_id=1, name="Oncology")
        with self.assertRaises(Exception):
            # Attempt to create another department with same name under same hospital
            Department.objects.create(hospital_id=1, name="Oncology")

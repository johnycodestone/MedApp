from django.core.exceptions import ValidationError
from .repositories import (
    create_department, remove_department, update_department,
    list_departments, get_department_by_name
)

def add_department(hospital_id, name, description="", head_doctor_id=None):
    existing = get_department_by_name(hospital_id, name)
    if existing:
        raise ValidationError("Department already exists.")
    return create_department(hospital_id, name, description, head_doctor_id)

def delete_department(hospital_id, name):
    if not get_department_by_name(hospital_id, name):
        raise ValidationError("Department not found.")
    return remove_department(hospital_id, name)

def edit_department(dept_id, **kwargs):
    return update_department(dept_id, **kwargs)

def get_departments_for_hospital(hospital_id):
    return list_departments(hospital_id)

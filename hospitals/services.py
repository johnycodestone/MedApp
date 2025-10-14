from django.core.exceptions import ValidationError
from .repositories import (
    get_or_create_hospital, add_department, remove_department,
    assign_doctor, waive_duty, list_reports
)

def register_hospital(user, name, **kwargs):
    return get_or_create_hospital(user, name, **kwargs)

def manage_department(hospital, action, name, description=""):
    if action == "add":
        return add_department(hospital, name, description)
    elif action == "remove":
        return remove_department(hospital, name)
    raise ValidationError("Invalid action")

def manage_doctor(hospital, doctor_id, action, department=None):
    if action == "assign":
        return assign_doctor(hospital, doctor_id, department)
    elif action == "waive":
        return waive_duty(hospital, doctor_id)
    raise ValidationError("Invalid action")

def get_reports(hospital):
    return list_reports(hospital)

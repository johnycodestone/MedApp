from django.core.exceptions import ValidationError
from .repositories import (
    get_or_create_doctor, upload_timetable, get_latest_timetable,
    cancel_appointment, add_prescription, list_prescriptions
)

def ensure_doctor_profile(user, **kwargs):
    return get_or_create_doctor(user, **kwargs)

def manage_timetable(user, file_obj):
    if file_obj.size > 5 * 1024 * 1024:
        raise ValidationError("File too large. Max 5MB.")
    doctor = ensure_doctor_profile(user)
    return upload_timetable(doctor, file_obj)

def get_timetable(user):
    doctor = ensure_doctor_profile(user)
    return get_latest_timetable(doctor)

def cancel_patient_appointment(user, appointment_id, reason=""):
    doctor = ensure_doctor_profile(user)
    return cancel_appointment(doctor, appointment_id, reason)

def give_prescription(user, patient_id, text, pdf_file=None):
    doctor = ensure_doctor_profile(user)
    return add_prescription(doctor, patient_id, text, pdf_file)

def get_doctor_prescriptions(user):
    doctor = ensure_doctor_profile(user)
    return list_prescriptions(doctor)

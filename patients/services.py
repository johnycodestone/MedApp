from django.core.exceptions import ValidationError
from .repositories import (
    get_or_create_profile, get_profile_by_id,
    save_doctor, remove_saved_doctor, list_saved_doctors,
    add_medical_record, list_medical_records
)

# Business-layer function to get or create profile
def ensure_profile_for_user(user):
    """
    Ensure and return a PatientProfile for the given authenticated user.
    Keep business rules here (e.g., create default preferences, initial checks).
    """
    return get_or_create_profile(user)

# Save a doctor to patient's favorites
def add_favorite_doctor(user, doctor_id):
    profile = ensure_profile_for_user(user)
    obj, created = save_doctor(profile, doctor_id)
    return obj, created

def delete_favorite_doctor(user, doctor_id):
    profile = ensure_profile_for_user(user)
    remove_saved_doctor(profile, doctor_id)
    return True

# Upload medical record and apply lightweight validation
def upload_medical_record(user, title, file_obj, notes=''):
    if file_obj.size > 10 * 1024 * 1024:
        raise ValidationError("File too large (max 10MB)")
    profile = ensure_profile_for_user(user)
    return add_medical_record(profile, title, file_obj, notes)

def get_records(user):
    profile = ensure_profile_for_user(user)
    return list_medical_records(profile)

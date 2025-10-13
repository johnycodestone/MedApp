from .models import PatientProfile, SavedDoctor, MedicalRecord, AppointmentHistoryEntry

# Fetch or create patient profile for a given user
def get_or_create_profile(user):
    profile, _ = PatientProfile.objects.get_or_create(user=user)
    return profile

def get_profile_by_id(profile_id):
    return PatientProfile.objects.filter(pk=profile_id).first()

def list_saved_doctors(patient_profile):
    return SavedDoctor.objects.filter(patient=patient_profile).order_by('-saved_at')

def save_doctor(patient_profile, doctor_id):
    obj, created = SavedDoctor.objects.get_or_create(patient=patient_profile, doctor_id=doctor_id)
    return obj, created

def remove_saved_doctor(patient_profile, doctor_id):
    return SavedDoctor.objects.filter(patient=patient_profile, doctor_id=doctor_id).delete()

def add_medical_record(patient_profile, title, file_obj, notes=''):
    return MedicalRecord.objects.create(patient=patient_profile, title=title, file=file_obj, notes=notes)

def list_medical_records(patient_profile):
    return MedicalRecord.objects.filter(patient=patient_profile).order_by('-uploaded_at')

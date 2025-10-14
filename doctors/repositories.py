from .models import DoctorProfile, Timetable, Prescription, AppointmentCancellation

def get_or_create_doctor(user, **kwargs):
    doctor, _ = DoctorProfile.objects.get_or_create(user=user, defaults=kwargs)
    return doctor

def upload_timetable(doctor, file_obj):
    return Timetable.objects.create(doctor=doctor, file=file_obj)

def get_latest_timetable(doctor):
    return Timetable.objects.filter(doctor=doctor, active=True).order_by("-uploaded_at").first()

def cancel_appointment(doctor, appointment_id, reason=""):
    return AppointmentCancellation.objects.create(doctor=doctor, appointment_id=appointment_id, reason=reason)

def add_prescription(doctor, patient_id, text, pdf=None):
    return Prescription.objects.create(doctor=doctor, patient_id=patient_id, text=text, pdf_file=pdf)

def list_prescriptions(doctor):
    return Prescription.objects.filter(doctor=doctor).order_by("-created_at")

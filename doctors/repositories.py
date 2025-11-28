from .models import DoctorProfile, Timetable, AppointmentCancellation
from prescriptions.models import Prescription


def get_or_create_doctor(user, **kwargs):
    """Get or create a doctor profile for a user."""
    doctor, _ = DoctorProfile.objects.get_or_create(user=user, defaults=kwargs)
    return doctor


def upload_timetable(doctor, file_obj):
    """Upload a timetable file for a doctor."""
    return Timetable.objects.create(doctor=doctor, file=file_obj)


def get_latest_timetable(doctor):
    """Get the latest active timetable for a doctor."""
    return Timetable.objects.filter(doctor=doctor, active=True).order_by("-uploaded_at").first()


def cancel_appointment(doctor, appointment_id, reason=""):
    """Record an appointment cancellation by a doctor."""
    return AppointmentCancellation.objects.create(
        doctor=doctor,
        appointment_id=appointment_id,
        reason=reason
    )


def add_prescription(doctor, appointment_id, text, pdf=None):
    """
    Create a prescription tied to an appointment.
    ✅ Updated: uses appointment_id instead of patient_id.
    """
    return Prescription.objects.create(
        doctor=doctor,
        appointment_id=appointment_id,
        text=text,
        pdf_file=pdf
    )


def list_prescriptions(doctor):
    """List prescriptions issued by a doctor."""
    return Prescription.objects.filter(doctor=doctor).order_by("-created_at")

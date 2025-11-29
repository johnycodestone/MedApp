# doctors/services.py
"""
Service layer (lightweight repository)
- Responsibility: encapsulate data access and business queries used by views and presenters.
- This file preserves your existing functions and appends/updates dashboard helpers to use real models.
- SOLID:
  - SRP: each function returns a focused dataset.
  - DIP: views depend on these functions rather than raw model queries.
- Safety: all new functions are defensive and return safe defaults on error.
"""

from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, time

# Preserve existing repository-based functions (if repositories exist)
try:
    from .repositories import (
        get_or_create_doctor, upload_timetable, get_latest_timetable,
        cancel_appointment, add_prescription, list_prescriptions
    )
except Exception:
    get_or_create_doctor = None
    upload_timetable = None
    get_latest_timetable = None
    cancel_appointment = None
    add_prescription = None
    list_prescriptions = None


def ensure_doctor_profile(user, **kwargs):
    """
    Return DoctorProfile for user. Prefer repository if present, else try related object.
    """
    if get_or_create_doctor:
        return get_or_create_doctor(user, **kwargs)
    try:
        return getattr(user, "doctors_doctor_profile", None)
    except Exception:
        return None


def manage_timetable(user, file_obj):
    """
    Upload timetable via repository if available; otherwise raise a ValidationError.
    """
    if file_obj.size > 5 * 1024 * 1024:
        raise ValidationError("File too large. Max 5MB.")
    doctor = ensure_doctor_profile(user)
    if upload_timetable and doctor:
        return upload_timetable(doctor, file_obj)
    raise ValidationError("Timetable upload not available.")


def get_timetable(user):
    doctor = ensure_doctor_profile(user)
    if get_latest_timetable and doctor:
        return get_latest_timetable(doctor)
    return None


def cancel_patient_appointment(user, appointment_id, reason=""):
    """
    Cancel appointment via repository if available; otherwise attempt to mark Appointment as cancelled.
    """
    doctor = ensure_doctor_profile(user)
    if cancel_appointment and doctor:
        return cancel_appointment(doctor, appointment_id, reason)
    try:
        from appointments.models import Appointment, AppointmentStatus
        appt = Appointment.objects.filter(id=appointment_id, doctor__id=getattr(user, "id", None)).first()
        if appt:
            appt.status = AppointmentStatus.CANCELLED
            appt.save(update_fields=["status"])
            # Record cancellation in local model if available
            try:
                from .models import AppointmentCancellation
                doctor_profile = ensure_doctor_profile(user)
                if doctor_profile:
                    AppointmentCancellation.objects.create(doctor=doctor_profile, appointment_id=appointment_id, reason=reason)
            except Exception:
                pass
            return appt
    except Exception:
        pass
    raise ValidationError("Unable to cancel appointment via service layer.")


def give_prescription(user, patient_id, text, pdf_file=None):
    """
    Create prescription via repository if available; otherwise create local Prescription model.
    """
    doctor = ensure_doctor_profile(user)
    if add_prescription and doctor:
        return add_prescription(doctor, patient_id, text, pdf_file)
    try:
        from .models import Prescription
        doctor_profile = ensure_doctor_profile(user)
        if doctor_profile:
            pres = Prescription.objects.create(doctor=doctor_profile, patient_id=patient_id, text=text, pdf_file=pdf_file)
            return pres
    except Exception:
        pass
    raise ValidationError("Unable to create prescription via service layer.")


def get_doctor_prescriptions(user):
    """
    Return prescriptions for doctor via repository or local model.
    """
    doctor_profile = ensure_doctor_profile(user)
    if list_prescriptions and doctor_profile:
        return list_prescriptions(doctor_profile)
    try:
        from .models import Prescription
        if doctor_profile:
            return Prescription.objects.filter(doctor=doctor_profile).order_by("-created_at")
    except Exception:
        pass
    return []


# ---------------------------
# Dashboard helper functions (real ORM queries where possible)
# ---------------------------

# Attempt to import Appointment model; if not available, set to None
try:
    from appointments.models import Appointment, AppointmentStatus
except Exception:
    Appointment = None
    AppointmentStatus = None

# Attempt to import DoctorProfile and PatientProfile for richer queries
try:
    from .models import DoctorProfile
except Exception:
    DoctorProfile = None

try:
    from patients.models import PatientProfile
except Exception:
    PatientProfile = None

# Attempt to import Shift model from schedules app
try:
    from schedules.models import Shift
except Exception:
    Shift = None


def count_todays_appointments(user):
    """
    Return number of appointments for today for the given doctor user.
    Safe: returns 0 if Appointment model is not available.
    """
    if Appointment is None:
        return 0
    try:
        today = timezone.localdate()
        start = timezone.make_aware(datetime.combine(today, time.min))
        end = timezone.make_aware(datetime.combine(today, time.max))
        return Appointment.objects.filter(doctor=user, scheduled_time__range=(start, end)).count()
    except Exception:
        return 0


def count_current_oncall(user):
    """
    Return number of active on-call shifts for the doctor.
    If schedules.Shift exists, query it; otherwise return 0.
    """
    if Shift is None:
        return 0
    try:
        now = timezone.now()
        # Defensive filtering: try common relation patterns
        qs = Shift.objects.filter(is_active=True)
        try:
            qs = qs.filter(duty__doctor__user=user, start_time__lte=now.time(), end_time__gte=now.time())
        except Exception:
            try:
                qs = qs.filter(duty__doctor__user__id=getattr(user, "id", None))
            except Exception:
                pass
        return qs.count()
    except Exception:
        return 0


def count_active_patients(user):
    """
    Return number of distinct active patients assigned to the doctor.
    Strategy: count distinct patients with non-cancelled appointments in recent window.
    """
    if Appointment is None:
        return 0
    try:
        cutoff = timezone.now() - timezone.timedelta(days=90)
        qs = Appointment.objects.filter(doctor=user, scheduled_time__gte=cutoff).exclude(status=AppointmentStatus.CANCELLED)
        return qs.values_list("patient", flat=True).distinct().count()
    except Exception:
        return 0


def get_upcoming_appointments_for_doctor(user, limit=6):
    """
    Return a list of upcoming Appointment instances for the doctor.
    """
    if Appointment is None:
        return []
    try:
        now = timezone.now()
        qs = Appointment.objects.filter(doctor=user, scheduled_time__gte=now).order_by("scheduled_time")[:limit]
        return list(qs)
    except Exception:
        return []


def get_upcoming_shifts_for_doctor(user, limit=6):
    """
    Return upcoming Shift instances for the doctor if schedules.Shift exists.
    """
    if Shift is None:
        return []
    try:
        now = timezone.now()
        try:
            qs = Shift.objects.filter(duty__doctor__user=user, is_active=True).order_by("start_time")[:limit]
        except Exception:
            qs = Shift.objects.filter(duty__doctor__user__id=getattr(user, "id", None), is_active=True)[:limit]
        return list(qs)
    except Exception:
        return []


def get_active_patients_for_doctor(user, limit=6):
    """
    Return active patients for the doctor.
    If PatientProfile exists, return profiles; otherwise return simple placeholder objects.
    """
    if Appointment is None:
        return []
    try:
        now = timezone.now()
        cutoff = now - timezone.timedelta(days=90)
        patient_ids = Appointment.objects.filter(doctor=user, scheduled_time__gte=cutoff).exclude(status=AppointmentStatus.CANCELLED).values_list("patient", flat=True).distinct()[:limit]
        if PatientProfile is not None:
            profiles = PatientProfile.objects.filter(user__in=patient_ids)[:limit]
            return list(profiles)
        else:
            class SimplePatient:
                def __init__(self, user_id):
                    self.user_id = user_id
                def __str__(self):
                    return f"User {self.user_id}"
            return [SimplePatient(pid) for pid in patient_ids]
    except Exception:
        return []


def get_recent_reports_for_doctor(user, limit=6):
    """
    Return recent reports relevant to the doctor if reports app exists.
    """
    try:
        from reports.models import Report
        qs = Report.objects.filter(author__user=user).order_by("-created_at")[:limit]
        return list(qs)
    except Exception:
        return []

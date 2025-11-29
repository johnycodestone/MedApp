# doctors/services.py
"""
Service layer (lightweight repository)
- Responsibility: encapsulate data access and business queries used by views and presenters.
- Preserves repository-based functions and adds dashboard helpers using real models.
- SOLID:
  - SRP: each function returns a focused dataset.
  - DIP: views depend on these services, not raw ORM scattered everywhere.
- Safety: defensive fallbacks; return safe defaults on error.
"""

from datetime import datetime, time, timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.shortcuts import get_object_or_404

# Preserve existing repository functions if present
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

# Models
try:
    from appointments.models import Appointment, AppointmentStatus
except Exception:
    Appointment = None
    AppointmentStatus = None

try:
    from .models import DoctorProfile
except Exception:
    DoctorProfile = None

try:
    from patients.models import PatientProfile
except Exception:
    PatientProfile = None

try:
    from schedules.models import Shift
except Exception:
    Shift = None

try:
    from prescriptions.models import Prescription
except Exception:
    Prescription = None

from django.contrib.auth import get_user_model

def ensure_doctor_profile(user, **kwargs):
    """
    Return DoctorProfile for a user. Prefer repository if present; else follow relation.
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
    """
    Return latest timetable via repository if available.
    """
    doctor = ensure_doctor_profile(user)
    if get_latest_timetable and doctor:
        return get_latest_timetable(doctor)
    return None


def cancel_patient_appointment(user, appointment_id, reason=""):
    """
    Cancel an appointment. Prefer repository; fallback to local update.
    Appointment.doctor is DoctorProfile (not User), so match on doctor profile.
    """
    doctor = ensure_doctor_profile(user)
    if cancel_appointment and doctor:
        return cancel_appointment(doctor, appointment_id, reason)

    try:
        if Appointment is None:
            raise ValidationError("Appointments not available.")
        appt = Appointment.objects.filter(id=appointment_id, doctor=doctor).first()
        if appt:
            appt.status = AppointmentStatus.CANCELLED
            appt.save(update_fields=["status", "updated_at"])
            # Record cancellation in local model if available
            try:
                from .models import AppointmentCancellation
                if doctor:
                    AppointmentCancellation.objects.create(doctor=doctor, appointment_id=appointment_id, reason=reason)
            except Exception:
                pass
            return appt
    except Exception:
        pass
    raise ValidationError("Unable to cancel appointment via service layer.")


def give_prescription(user, appointment_id, notes, pdf_file=None):
    """
    Create or update a prescription for a given appointment.
    Ensures only the doctor assigned to the appointment can issue it.
    - Prescription model has fields: appointment (OneToOne), notes; no pdf_file in your schema.
    """
    if Appointment is None or Prescription is None:
        raise ValidationError("Prescription service unavailable.")
    doctor = ensure_doctor_profile(user)
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor)

    pres, created = Prescription.objects.get_or_create(
        appointment=appointment,
        defaults={"notes": notes}
    )
    if not created:
        pres.notes = notes
    # pdf_file is ignored (model does not have it)
    pres.save()
    return pres


def get_doctor_prescriptions(user):
    """
    Return prescriptions for the current doctor.
    - Your Prescription model does NOT have a `doctor` field; filter via appointment__doctor.
    """
    doctor_profile = ensure_doctor_profile(user)
    try:
        if Prescription and doctor_profile:
            return Prescription.objects.filter(appointment__doctor=doctor_profile).order_by("-created_at")
    except Exception:
        pass
    return []


# ---------------------------
# Dashboard helper functions
# ---------------------------

def count_todays_appointments(user):
    """
    Number of appointments for today for the given doctor (DoctorProfile).
    """
    if Appointment is None:
        return 0
    try:
        doctor = ensure_doctor_profile(user)
        if doctor is None:
            return 0
        today = timezone.localdate()
        start = timezone.make_aware(datetime.combine(today, time.min))
        end = timezone.make_aware(datetime.combine(today, time.max))
        return Appointment.objects.filter(doctor=doctor, scheduled_time__range=(start, end)).count()
    except Exception:
        return 0


def count_current_oncall(user):
    """
    Number of active shifts right now for the doctor.
    - Shift belongs to Duty, Duty.doctor is DoctorProfile.
    - We check today's weekday and current time window.
    """
    if Shift is None:
        return 0
    try:
        doctor = ensure_doctor_profile(user)
        if doctor is None:
            return 0
        now = timezone.localtime()
        weekday = now.weekday()  # Monday=0..Sunday=6
        return Shift.objects.filter(
            duty__doctor=doctor,
            is_active=True,
            day_of_week=weekday,
            start_time__lte=now.time(),
            end_time__gte=now.time(),
        ).count()
    except Exception:
        return 0


def count_active_patients(user):
    """
    Distinct active patients assigned to the doctor in the recent window (90 days),
    excluding cancelled appointments.
    """
    if Appointment is None:
        return 0
    try:
        doctor = ensure_doctor_profile(user)
        if doctor is None:
            return 0
        cutoff = timezone.now() - timedelta(days=90)
        qs = Appointment.objects.filter(doctor=doctor, scheduled_time__gte=cutoff).exclude(status=AppointmentStatus.CANCELLED)
        return qs.values_list("patient", flat=True).distinct().count()
    except Exception:
        return 0


def get_upcoming_appointments_for_doctor(user, limit=6):
    """
    Upcoming appointments for the doctor.
    """
    if Appointment is None:
        return []
    try:
        doctor = ensure_doctor_profile(user)
        if doctor is None:
            return []
        now = timezone.now()
        qs = Appointment.objects.filter(doctor=doctor, scheduled_time__gte=now).order_by("scheduled_time")[:limit]
        return list(qs)
    except Exception:
        return []


def get_upcoming_shifts_for_doctor(user, limit=6):
    """
    Upcoming shifts for the doctor (Shift via Duty).
    """
    if Shift is None:
        return []
    try:
        doctor = ensure_doctor_profile(user)
        if doctor is None:
            return []
        qs = Shift.objects.filter(duty__doctor=doctor, is_active=True).order_by("day_of_week", "start_time")[:limit]
        return list(qs)
    except Exception:
        return []


def get_active_patients_for_doctor(user, limit=6):
    """
    Active PatientProfile objects for the doctor in recent window.
    """
    if Appointment is None or PatientProfile is None:
        return []
    try:
        doctor = ensure_doctor_profile(user)
        if doctor is None:
            return []
        cutoff = timezone.now() - timedelta(days=90)
        patient_ids = (Appointment.objects
                       .filter(doctor=doctor, scheduled_time__gte=cutoff)
                       .exclude(status=AppointmentStatus.CANCELLED)
                       .values_list("patient", flat=True)
                       .distinct()[:limit])
        profiles = PatientProfile.objects.filter(id__in=patient_ids)[:limit]
        return list(profiles)
    except Exception:
        return []


def get_recent_reports_for_doctor(user, limit=6):
    """
    Recent reports relevant to the doctor.
    - Your Report model uses doctor=DoctorProfile (not author).
    """
    try:
        from reports.models import Report
        doctor = ensure_doctor_profile(user)
        if doctor is None:
            return []
        qs = Report.objects.filter(doctor=doctor).order_by("-generated_at")[:limit]
        return list(qs)
    except Exception:
        return []

def _to_doctor_profile(doctor_or_user):
    """
    Normalize input to a DoctorProfile.
    Accepts either DoctorProfile or User and returns DoctorProfile or None.
    """
    # Already a DoctorProfile-like object
    if hasattr(doctor_or_user, "appointments") and hasattr(doctor_or_user, "user"):
        return doctor_or_user
    # If it's a User, try the common reverse relation name
    try:
        return getattr(doctor_or_user, "doctors_doctor_profile", None)
    except Exception:
        return None

def get_available_slots(doctor, date=None):
    """
    Returns a list of available datetime slots for the given doctor.
    - Accepts DoctorProfile or User (auto-normalized to DoctorProfile).
    - Default: today
    - Filters out already booked slots
    - Assumes 30-minute slots from 9 AM to 5 PM
    """
    from datetime import datetime, timedelta  # local import to avoid import cycles
    doctor_profile = _to_doctor_profile(doctor)
    if doctor_profile is None:
        return []

    if date is None:
        date = datetime.today().date()

    start_time = datetime.combine(date, datetime.min.time()).replace(hour=9)
    end_time = datetime.combine(date, datetime.min.time()).replace(hour=17)

    all_slots = [start_time + timedelta(minutes=30 * i) for i in range(16)]  # 9:00 to 17:00

    booked = Appointment.objects.filter(
        doctor=doctor_profile,
        scheduled_time__date=date,
        status__in=[AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]
    ).values_list("scheduled_time", flat=True)

    available = [slot for slot in all_slots if slot not in booked]
    return available

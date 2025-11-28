from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from appointments.models import Appointment, AppointmentStatus
from prescriptions.models import Prescription

from .repositories import (
    get_or_create_doctor, upload_timetable, get_latest_timetable,
    cancel_appointment
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


# ✅ Updated: prescriptions tied to appointments
def give_prescription(user, appointment_id, notes, pdf_file=None):
    """
    Create or update a prescription for a given appointment.
    Ensures only the doctor assigned to the appointment can issue it.
    """
    doctor = ensure_doctor_profile(user)
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=doctor)

    # One-to-one: either create or update
    pres, created = Prescription.objects.get_or_create(
        appointment=appointment,
        defaults={"notes": notes}
    )
    if not created:
        pres.notes = notes

    if pdf_file:
        pres.pdf_file = pdf_file

    pres.save()
    return pres


def get_doctor_prescriptions(user):
    """
    Return all prescriptions issued by the authenticated doctor.
    """
    doctor = ensure_doctor_profile(user)
    return Prescription.objects.filter(appointment__doctor=doctor)


# ✅ Slot availability for booking modal
def get_available_slots(doctor, date=None):
    """
    Returns a list of available datetime slots for the given doctor.
    - Default: today
    - Filters out already booked slots
    - Assumes 30-minute slots from 9 AM to 5 PM
    """
    if date is None:
        date = datetime.today().date()

    start_time = datetime.combine(date, datetime.min.time()).replace(hour=9)
    end_time = datetime.combine(date, datetime.min.time()).replace(hour=17)

    all_slots = [start_time + timedelta(minutes=30 * i) for i in range(16)]  # 9:00 to 17:00

    booked = Appointment.objects.filter(
        doctor=doctor,
        scheduled_time__date=date,
        status__in=[AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]
    ).values_list("scheduled_time", flat=True)

    available = [slot for slot in all_slots if slot not in booked]
    return available

from django.utils import timezone
from django.core.exceptions import ValidationError
from .repositories import AppointmentRepository
from .models import AppointmentStatus, Appointment

from patients.models import PatientProfile
from doctors.models import DoctorProfile


class AppointmentService:
    @staticmethod
    def create_appointment(patient_user, doctor_user, scheduled_time, reason=None):
        """
        Create a new appointment if the slot is valid and not already booked.
        - patient_user: CustomUser instance
        - doctor_user: CustomUser instance
        """
        if not scheduled_time:
            raise ValidationError("Scheduled time is required.")

        if scheduled_time < timezone.now():
            raise ValidationError("Cannot book an appointment in the past.")

        # Resolve profiles
        try:
            patient = patient_user.patientprofile
        except PatientProfile.DoesNotExist:
            raise ValidationError("Patient profile not found.")

        try:
            doctor = doctor_user.doctorprofile
        except DoctorProfile.DoesNotExist:
            raise ValidationError("Doctor profile not found.")

        # Prevent double-booking
        if Appointment.objects.filter(doctor=doctor, scheduled_time=scheduled_time).exists():
            raise ValidationError("This time slot is already booked for the selected doctor.")

        return AppointmentRepository.create(patient, doctor, scheduled_time, reason)

    @staticmethod
    def cancel_appointment(appointment_id, user):
        """
        Cancel an appointment if the user is the patient or doctor,
        and if the appointment is still pending/confirmed.
        """
        appointment = AppointmentRepository.get_by_id(appointment_id)
        if not appointment:
            return None

        # Check ownership via profiles
        patient_match = hasattr(user, "patientprofile") and appointment.patient == user.patientprofile
        doctor_match = hasattr(user, "doctorprofile") and appointment.doctor == user.doctorprofile

        if (patient_match or doctor_match) and appointment.status in [
            AppointmentStatus.PENDING,
            AppointmentStatus.CONFIRMED,
        ]:
            appointment.status = AppointmentStatus.CANCELLED
            appointment.save(update_fields=["status", "updated_at"])
            return appointment

        return None

    @staticmethod
    def get_upcoming_appointments(user):
        """
        Get upcoming appointments for a user (patient or doctor).
        Only include pending/confirmed appointments scheduled in the future.
        """
        now = timezone.now()

        if hasattr(user, "patientprofile"):
            return Appointment.objects.filter(
                patient=user.patientprofile,
                scheduled_time__gte=now,
                status__in=[AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]
            ).select_related("doctor", "patient").order_by("scheduled_time")

        if hasattr(user, "doctorprofile"):
            return Appointment.objects.filter(
                doctor=user.doctorprofile,
                scheduled_time__gte=now,
                status__in=[AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]
            ).select_related("doctor", "patient").order_by("scheduled_time")

        return Appointment.objects.none()

    @staticmethod
    def reschedule_appointment(appointment_id, new_time):
        """
        Reschedule an appointment if it's still pending and the new slot is valid.
        """
        appointment = AppointmentRepository.get_by_id(appointment_id)
        if not appointment:
            return None

        if appointment.status != AppointmentStatus.PENDING:
            return None

        if not new_time or new_time < timezone.now():
            return None

        # Prevent double-booking
        if Appointment.objects.filter(doctor=appointment.doctor, scheduled_time=new_time).exists():
            return None

        appointment.scheduled_time = new_time
        appointment.save(update_fields=["scheduled_time", "updated_at"])
        return appointment

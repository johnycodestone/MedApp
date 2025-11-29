from django.utils import timezone
from .models import Appointment, AppointmentStatus

from patients.models import PatientProfile
from doctors.models import DoctorProfile


class AppointmentRepository:
    @staticmethod
    def create(patient, doctor, scheduled_time, reason=None):
        """
        Create a new appointment record.
        Expects patient = PatientProfile, doctor = DoctorProfile.
        """
        return Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            scheduled_time=scheduled_time,
            reason=reason,
            status=AppointmentStatus.PENDING
        )

    @staticmethod
    def get_by_id(appointment_id):
        """
        Retrieve an appointment by its ID.
        """
        try:
            return Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            return None

    @staticmethod
    def get_upcoming(user):
        """
        Get upcoming appointments for a user (patient or doctor).
        Includes only pending/confirmed appointments scheduled in the future.
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
    def get_by_user_and_status(user, status=None):
        """
        Get appointments for a user filtered by status.
        Supports patient, doctor, and admin roles.
        """
        qs = Appointment.objects.all()

        if hasattr(user, "doctorprofile"):
            qs = qs.filter(doctor=user.doctorprofile)
        elif hasattr(user, "patientprofile"):
            qs = qs.filter(patient=user.patientprofile)

        if status:
            qs = qs.filter(status=status)

        return qs.select_related("doctor", "patient").order_by("-scheduled_time")

    @staticmethod
    def exists_for_doctor_slot(doctor, scheduled_time):
        """
        Check if a doctor already has an appointment at the given time.
        Expects doctor = DoctorProfile.
        """
        return Appointment.objects.filter(
            doctor=doctor,
            scheduled_time=scheduled_time,
            status__in=[AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]
        ).exists()

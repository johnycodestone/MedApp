from .repositories import AppointmentRepository
from .models import AppointmentStatus
from django.utils import timezone

class AppointmentService:
    @staticmethod
    def create_appointment(patient, doctor, scheduled_time, reason=None):
        return AppointmentRepository.create(patient, doctor, scheduled_time, reason)

    @staticmethod
    def cancel_appointment(appointment_id, user):
        appointment = AppointmentRepository.get_by_id(appointment_id)
        if appointment and (appointment.patient == user or appointment.doctor == user):
            appointment.status = AppointmentStatus.CANCELLED
            appointment.save()
            return appointment
        return None

    @staticmethod
    def get_upcoming_appointments(user):
        return AppointmentRepository.get_upcoming(user)

    @staticmethod
    def reschedule_appointment(appointment_id, new_time):
        appointment = AppointmentRepository.get_by_id(appointment_id)
        if appointment and appointment.status == AppointmentStatus.PENDING:
            appointment.scheduled_time = new_time
            appointment.save()
            return appointment
        return None

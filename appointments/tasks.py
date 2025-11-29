from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
import logging

from .models import Appointment, AppointmentStatus

logger = logging.getLogger(__name__)


@shared_task
def send_appointment_reminder(appointment_id):
    """
    Celery task to send an appointment reminder email.
    - Only sends for pending/confirmed appointments.
    - Uses both plain text and HTML formats.
    """
    try:
        appointment = Appointment.objects.get(id=appointment_id)

        # Only send reminders for active appointments
        if appointment.status not in [AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]:
            logger.info(f"Skipping reminder: appointment {appointment_id} has status {appointment.status}")
            return

        subject = "Appointment Reminder"
        patient_name = appointment.patient.get_full_name() or appointment.patient.username
        doctor_name = appointment.doctor.get_full_name() or appointment.doctor.username
        scheduled_time = timezone.localtime(appointment.scheduled_time).strftime("%A, %B %d at %I:%M %p")

        message = (
            f"Dear {patient_name},\n\n"
            f"This is a reminder that you have an appointment with Dr. {doctor_name} "
            f"on {scheduled_time}.\n\n"
            "Please ensure you are available at the scheduled time.\n\n"
            "Best regards,\nMedApp Team"
        )

        html_message = f"""
            <p>Dear <strong>{patient_name}</strong>,</p>
            <p>This is a reminder that you have an appointment with <strong>Dr. {doctor_name}</strong> 
            on <strong>{scheduled_time}</strong>.</p>
            <p>Please ensure you are available at the scheduled time.</p>
            <p>Best regards,<br><em>MedApp Team</em></p>
        """

        send_mail(
            subject,
            message,
            'noreply@medapp.com',
            [appointment.patient.email],
            html_message=html_message,
        )

        logger.info(f"Reminder sent for appointment {appointment_id}")

    except Appointment.DoesNotExist:
        logger.error(f"Appointment {appointment_id} does not exist")

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from patients.models import PatientProfile
from doctors.models import DoctorProfile


class AppointmentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    CONFIRMED = "confirmed", "Confirmed"
    CANCELLED = "cancelled", "Cancelled"
    COMPLETED = "completed", "Completed"


class Appointment(models.Model):
    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name="appointments"
    )
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name="appointments"
    )
    scheduled_time = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=AppointmentStatus.choices,
        default=AppointmentStatus.PENDING
    )
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # ✅ track changes

    class Meta:
        ordering = ["-scheduled_time"]
        unique_together = ("doctor", "scheduled_time")

    def __str__(self):
        patient_name = self.patient.get_full_name_or_username()
        doctor_name = self.doctor.get_full_name_or_username()
        return f"{patient_name} with Dr. {doctor_name} at {self.scheduled_time.strftime('%Y-%m-%d %H:%M')}"

    def clean(self):
        """Validation to prevent past bookings and double-booking."""
        if self.scheduled_time and self.scheduled_time < timezone.now():
            raise ValidationError("Cannot schedule an appointment in the past.")

        if self.scheduled_time and Appointment.objects.exclude(pk=self.pk).filter(
            doctor=self.doctor,
            scheduled_time=self.scheduled_time,
            status__in=[AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]
        ).exists():
            raise ValidationError("This time slot is already booked for the selected doctor.")

    def is_upcoming(self):
        """Check if appointment is in the future and active."""
        return self.scheduled_time >= timezone.now() and self.status in [
            AppointmentStatus.PENDING,
            AppointmentStatus.CONFIRMED,
        ]

    def cancel(self):
        """Cancel the appointment."""
        self.status = AppointmentStatus.CANCELLED
        self.save(update_fields=["status", "updated_at"])

    def reschedule(self, new_time):
        """Reschedule the appointment if valid."""
        if new_time < timezone.now():
            raise ValidationError("Cannot reschedule to a past time.")
        if Appointment.objects.filter(
            doctor=self.doctor,
            scheduled_time=new_time,
            status__in=[AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]
        ).exists():
            raise ValidationError("This time slot is already booked for the selected doctor.")
        self.scheduled_time = new_time
        self.save(update_fields=["scheduled_time", "updated_at"])

from django.db import models

class Prescription(models.Model):
    appointment = models.OneToOneField(
        "appointments.Appointment",   # ✅ one prescription per appointment
        on_delete=models.CASCADE,
        related_name="prescription"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        patient_name = self.appointment.patient.get_full_name_or_username()
        doctor_name = self.appointment.doctor.get_full_name_or_username()
        return f"Prescription for {patient_name} by Dr. {doctor_name}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Prescription"
        verbose_name_plural = "Prescriptions"


class Medication(models.Model):
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name="medications"
    )
    name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50)
    frequency = models.CharField(max_length=50)
    duration = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} ({self.dosage})"

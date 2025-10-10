# prescriptions/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator

User = settings.AUTH_USER_MODEL

class Prescription(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_FINAL = "final"
    STATUS_REVOKED = "revoked"

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_FINAL, "Finalized"),
        (STATUS_REVOKED, "Revoked"),
    ]

    patient = models.ForeignKey(User, related_name="prescriptions", on_delete=models.CASCADE)
    doctor = models.ForeignKey(User, related_name="issued_prescriptions", on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    file = models.FileField(upload_to="prescriptions/files/", null=True, blank=True)
    summary = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Prescription #{self.id} for {self.patient}"

    def finalize(self):
        self.status = self.STATUS_FINAL
        self.save(update_fields=["status", "updated_at"])

    def revoke(self):
        self.status = self.STATUS_REVOKED
        self.save(update_fields=["status", "updated_at"])


class Medication(models.Model):
    prescription = models.ForeignKey(Prescription, related_name="medications", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=255, blank=True)
    frequency = models.CharField(max_length=255, blank=True)
    duration = models.CharField(max_length=255, blank=True)
    instructions = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.name} (Prescription #{self.prescription_id})"

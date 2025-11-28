from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver


# -------------------------------
# Patient Profile
# -------------------------------
class PatientProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patientprofile"
    )
    phone = models.CharField(max_length=20, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PatientProfile(user={self.user.username})"

    def get_full_name_or_username(self):
        return self.user.get_full_name() or self.user.username


# -------------------------------
# Auto-create PatientProfile when a User is created
# -------------------------------
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_patient_profile(sender, instance, created, **kwargs):
    if created:
        PatientProfile.objects.get_or_create(user=instance)


# -------------------------------
# Saved Doctor (favorites)
# -------------------------------
class SavedDoctor(models.Model):
    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name="saved_doctors"
    )
    doctor = models.ForeignKey(
        "doctors.DoctorProfile",   # ✅ string reference to avoid circular import
        on_delete=models.CASCADE,
        related_name="saved_by_patients"
    )
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("patient", "doctor")

    def __str__(self):
        return f"{self.patient} saved {self.doctor}"


# -------------------------------
# Medical Record
# -------------------------------
class MedicalRecord(models.Model):
    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name="medical_records"
    )
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to="patient_records/")  # configure MEDIA_ROOT in settings
    notes = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Record({self.title}) for {self.patient}"


# -------------------------------
# Appointment History Entry
# -------------------------------
class AppointmentHistoryEntry(models.Model):
    patient = models.ForeignKey(
        PatientProfile,
        on_delete=models.CASCADE,
        related_name="appointment_history"
    )
    appointment_id = models.PositiveIntegerField()
    doctor_id = models.PositiveIntegerField()
    started_at = models.DateTimeField()
    status = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"HistoryEntry(appointment={self.appointment_id}, patient={self.patient})"

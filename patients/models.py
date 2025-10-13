from django.db import models

# Create your models here.

from django.db import models
from django.conf import settings

# PatientProfile: one-to-one with auth User (core.User in your core app)
class PatientProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient_profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PatientProfile({self.user_id})"

# SavedDoctor: patient can save favorite doctors
class SavedDoctor(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='saved_doctors')
    doctor_id = models.PositiveIntegerField()  # store FK id to doctors app; avoid direct import to reduce coupling
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('patient', 'doctor_id')

# MedicalRecord: uploaded medical history files or notes
class MedicalRecord(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='medical_records')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='patient_records/')  # configure MEDIA_ROOT in settings
    notes = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

# AppointmentHistoryEntry: local cache/history of appointments (read-only replication from appointments app)
class AppointmentHistoryEntry(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='appointment_history')
    appointment_id = models.PositiveIntegerField()
    doctor_id = models.PositiveIntegerField()
    started_at = models.DateTimeField()
    status = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)

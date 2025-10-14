#from django.db import models
#
## Create your models here.
from django.db import models
from django.conf import settings

class DoctorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_profile"
    )
    specialization = models.CharField(max_length=100)
    experience_years = models.PositiveIntegerField(default=0)
    qualification = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    rating = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} ({self.specialization})"


class Timetable(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name="timetables")
    file = models.FileField(upload_to="doctor_timetables/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"Timetable {self.id} for {self.doctor}"


class Prescription(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name="prescriptions")
    patient_id = models.PositiveIntegerField()
    text = models.TextField()
    pdf_file = models.FileField(upload_to="prescriptions/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription to patient {self.patient_id} by {self.doctor}"


class AppointmentCancellation(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    appointment_id = models.PositiveIntegerField()
    reason = models.TextField(blank=True)
    cancelled_at = models.DateTimeField(auto_now_add=True)

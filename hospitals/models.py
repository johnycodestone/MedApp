#from django.db import models

# Create your models here.

from django.db import models
from django.conf import settings

class Hospital(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="hospital_profile"
    )
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=500, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Department(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name="departments")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("hospital", "name")

    def __str__(self):
        return f"{self.name} ({self.hospital.name})"


class DoctorAssignment(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    doctor_id = models.PositiveIntegerField()  # FK to doctors app
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    duty_status = models.CharField(max_length=20, default="Active")
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Doctor {self.doctor_id} @ {self.hospital.name}"


class Report(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name="reports")
    title = models.CharField(max_length=255)
    report_file = models.FileField(upload_to="hospital_reports/")
    created_at = models.DateTimeField(auto_now_add=True)

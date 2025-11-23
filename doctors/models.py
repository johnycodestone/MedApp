# doctors/models.py
from django.db import models
from django.conf import settings


# Single source of truth for specialization choices (key, label)
SPECIALIZATION_CHOICES = [
    ("cardiology", "Cardiology"),
    ("neurology", "Neurology"),
    ("orthopedics", "Orthopedics"),
    ("dermatology", "Dermatology"),
    ("pediatrics", "Pediatrics"),
    ("endocrinology", "Endocrinology"),
    ("gastroenterology", "Gastroenterology"),
    ("psychiatry", "Psychiatry"),
    ("urology", "Urology"),
    ("oncology", "Oncology"),
    ("gynecology", "Gynecology / Obstetrics"),
    ("nephrology", "Nephrology"),
    ("pulmonology", "Pulmonology"),
    ("rheumatology", "Rheumatology"),
    ("ophthalmology", "Ophthalmology"),
    ("ent", "ENT (Otolaryngology)"),
    ("radiology", "Radiology"),
    ("anesthesiology", "Anesthesiology"),
    ("emergency", "Emergency Medicine"),
    ("family", "Family Medicine / General Practice"),
]


class DoctorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctors_doctor_profile",
        help_text="Linked account for this doctor"
    )
    specialization = models.CharField(
        max_length=50,
        choices=SPECIALIZATION_CHOICES,
        db_index=True,
        help_text="Medical specialization (from predefined choices)"
    )
    experience_years = models.PositiveIntegerField(
        default=0,
        help_text="Years of professional experience"
    )
    qualification = models.CharField(
        max_length=255,
        blank=True,
        help_text="Degrees/certifications (e.g., MBBS, MD)"
    )
    bio = models.TextField(
        blank=True,
        help_text="Short professional bio"
    )
    rating = models.FloatField(
        default=0.0,
        help_text="Average rating out of 5.0"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-rating", "user__first_name"]
        indexes = [
            models.Index(fields=["specialization"]),
            models.Index(fields=["-rating"]),
            models.Index(fields=["experience_years"]),
        ]
        verbose_name = "Doctor profile"
        verbose_name_plural = "Doctor profiles"

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} ({self.get_specialization_display()})"

    @property
    def specialization_label(self):
        """Human-readable specialization label."""
        return self.get_specialization_display()


class Timetable(models.Model):
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name="timetables"
    )
    file = models.FileField(upload_to="doctor_timetables/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Timetable"
        verbose_name_plural = "Timetables"

    def __str__(self):
        return f"Timetable {self.id} for {self.doctor}"


class Prescription(models.Model):
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name="doctor_prescriptions"
    )
    patient_id = models.PositiveIntegerField()
    text = models.TextField()
    pdf_file = models.FileField(upload_to="prescriptions/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Prescription"
        verbose_name_plural = "Prescriptions"

    def __str__(self):
        return f"Prescription to patient {self.patient_id} by {self.doctor}"


class AppointmentCancellation(models.Model):
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    appointment_id = models.PositiveIntegerField()
    reason = models.TextField(blank=True)
    cancelled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-cancelled_at"]
        verbose_name = "Appointment cancellation"
        verbose_name_plural = "Appointment cancellations"

    def __str__(self):
        return f"Cancellation #{self.appointment_id} by {self.doctor}"

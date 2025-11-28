from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

# -------------------------------
# Specialization Choices
# -------------------------------
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

# -------------------------------
# Doctor Profile
# -------------------------------
class DoctorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctorprofile",
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
        return f"Dr. {self.user.get_full_name() or self.user.username} ({self.get_specialization_display()})"

    @property
    def specialization_label(self):
        """Human-readable specialization label."""
        return self.get_specialization_display()

    def get_full_name_or_username(self):
        return self.user.get_full_name() or self.user.username

# -------------------------------
# Auto-create DoctorProfile when a User is created
# -------------------------------
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_doctor_profile(sender, instance, created, **kwargs):
    if created and getattr(instance, "is_doctor", False):
        DoctorProfile.objects.get_or_create(user=instance)

# -------------------------------
# Timetable
# -------------------------------
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

# -------------------------------
# Appointment Cancellation
# -------------------------------
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

# -------------------------------
# Saved Doctor (Favorites)
# -------------------------------
class SavedDoctor(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_doctors"
    )
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name="saved_by",
        null=True, blank=True,   # ✅ must be here
        help_text="Doctor that the user has saved/favorited"
    )
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "doctor")
        ordering = ["-saved_at"]
        verbose_name = "Saved doctor"
        verbose_name_plural = "Saved doctors"

    def __str__(self):
        return f"{self.user} saved {self.doctor}"

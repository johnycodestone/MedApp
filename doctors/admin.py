# doctors/admin.py

from django.contrib import admin
from .models import (
    DoctorProfile,
    Timetable,
    Prescription,
    AppointmentCancellation
)

# -------------------------------
# Admin registration for DoctorProfile
# -------------------------------
@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for DoctorProfile.
    Displays core doctor identity, specialization, and metadata.
    """
    list_display = ("user", "specialization", "experience_years", "qualification", "rating", "created_at")
    search_fields = ("user__username", "specialization", "qualification")
    list_filter = ("specialization", "experience_years", "created_at")
    ordering = ("-created_at",)

# -------------------------------
# Admin registration for Timetable
# -------------------------------
@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for Timetable.
    Displays uploaded schedule files for doctors.
    """
    list_display = ("doctor", "uploaded_at", "updated_at", "active")
    search_fields = ("doctor__user__username",)
    list_filter = ("active", "uploaded_at", "updated_at")
    ordering = ("-uploaded_at",)

# -------------------------------
# Admin registration for Prescription
# -------------------------------
@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for Prescription.
    Displays prescriptions issued by doctors to patients.
    """
    list_display = ("doctor", "patient_id", "created_at")
    search_fields = ("doctor__user__username", "patient_id")
    list_filter = ("created_at",)
    ordering = ("-created_at",)

# -------------------------------
# Admin registration for AppointmentCancellation
# -------------------------------
@admin.register(AppointmentCancellation)
class AppointmentCancellationAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for AppointmentCancellation.
    Tracks cancelled appointments and reasons.
    """
    list_display = ("doctor", "appointment_id", "cancelled_at")
    search_fields = ("doctor__user__username", "appointment_id")
    list_filter = ("cancelled_at",)
    ordering = ("-cancelled_at",)

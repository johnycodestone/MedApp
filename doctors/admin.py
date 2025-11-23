# doctors/admin.py
from django.contrib import admin
from .models import (
    DoctorProfile,
    Timetable,
    Prescription,
    AppointmentCancellation,
)

# -------------------------------
# Admin registration for DoctorProfile
# -------------------------------
from .forms import DoctorProfileForm  # ← Add this import

@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    form = DoctorProfileForm  # ← Add this line

    def specialization_label(self, obj):
        return obj.get_specialization_display()
    specialization_label.short_description = "Specialization"

    list_display = (
        "user",
        "specialization_label",
        "experience_years",
        "qualification",
        "rating",
        "created_at",
    )
    list_filter = (
        "specialization",
        "experience_years",
        "rating",
        "created_at",
    )
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "qualification",
        "bio",
    )
    autocomplete_fields = ("user",)
    date_hierarchy = "created_at"
    ordering = ("-rating", "user__first_name")
# -------------------------------
# Admin registration for Timetable
# -------------------------------
@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for Timetable.
    Displays uploaded schedule files for doctors.
    """
    list_display = ("id", "doctor", "active", "uploaded_at", "updated_at")
    search_fields = (
        "doctor__user__username",
        "doctor__user__first_name",
        "doctor__user__last_name",
    )
    list_filter = ("active", "uploaded_at", "updated_at")
    date_hierarchy = "uploaded_at"
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
    list_display = ("id", "doctor", "patient_id", "created_at")
    search_fields = (
        "doctor__user__username",
        "doctor__user__first_name",
        "doctor__user__last_name",
        "patient_id",
        "text",
    )
    list_filter = ("created_at",)
    date_hierarchy = "created_at"
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
    list_display = ("id", "doctor", "appointment_id", "cancelled_at")
    search_fields = (
        "doctor__user__username",
        "doctor__user__first_name",
        "doctor__user__last_name",
        "appointment_id",
        "reason",
    )
    list_filter = ("cancelled_at",)
    date_hierarchy = "cancelled_at"
    ordering = ("-cancelled_at",)

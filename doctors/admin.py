from django.contrib import admin
from .models import (
    DoctorProfile,
    Timetable,
    AppointmentCancellation,
)
from .forms import DoctorProfileForm


# -------------------------------
# Admin registration for DoctorProfile
# -------------------------------
@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    form = DoctorProfileForm

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
# Admin registration for AppointmentCancellation
# -------------------------------
@admin.register(AppointmentCancellation)
class AppointmentCancellationAdmin(admin.ModelAdmin):
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

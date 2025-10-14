from django.contrib import admin
from .models import DoctorProfile, Timetable, Prescription, AppointmentCancellation

@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "specialization", "experience_years", "rating")
    search_fields = ("user__username", "specialization")

@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ("doctor", "uploaded_at", "active")

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ("doctor", "patient_id", "created_at")
    search_fields = ("patient_id",)

@admin.register(AppointmentCancellation)
class AppointmentCancellationAdmin(admin.ModelAdmin):
    list_display = ("doctor", "appointment_id", "cancelled_at")

# appointments/admin.py

from django.contrib import admin
from .models import Appointment

# -------------------------------
# Admin registration for Appointment
# -------------------------------
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for Appointment.
    Displays scheduled appointments between patients and doctors.
    Includes status tracking, filtering, and search capabilities.
    """
    list_display = (
        'patient',
        'doctor',
        'scheduled_time',
        'status',
        'created_at'
    )
    search_fields = (
        'patient__username',
        'doctor__username',
        'reason'
    )
    list_filter = (
        'status',
        'scheduled_time',
        'created_at'
    )
    ordering = ('-scheduled_time',)

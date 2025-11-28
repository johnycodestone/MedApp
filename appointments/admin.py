from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for Appointment.
    Displays scheduled appointments between patients and doctors.
    Includes status tracking, filtering, and search capabilities.
    """
    list_display = (
        'patient_full_name',
        'doctor_full_name',
        'scheduled_time',
        'status',
        'created_at',
    )
    search_fields = (
        'patient__username',
        'patient__first_name',
        'patient__last_name',
        'doctor__username',
        'doctor__first_name',
        'doctor__last_name',
        'reason',
    )
    list_filter = (
        'status',
        'scheduled_time',
        'created_at',
    )
    ordering = ('-scheduled_time',)
    readonly_fields = ('created_at',)
    date_hierarchy = 'scheduled_time'
    list_select_related = ('patient', 'doctor')

    def patient_full_name(self, obj):
        return obj.patient.get_full_name() or obj.patient.username
    patient_full_name.short_description = "Patient"

    def doctor_full_name(self, obj):
        return obj.doctor.get_full_name() or obj.doctor.username
    doctor_full_name.short_description = "Doctor"

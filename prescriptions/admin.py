from django.contrib import admin
from .models import Prescription, Medication

# -------------------------------
# Inline configuration for Medication
# -------------------------------
class MedicationInline(admin.TabularInline):
    """
    Allows medications to be added/edited directly within a Prescription form.
    Uses a tabular layout for compact display.
    """
    model = Medication
    extra = 1  # Show one empty row by default
    fields = ('name', 'dosage', 'frequency', 'duration')
    verbose_name_plural = "Medications"


# -------------------------------
# Admin registration for Prescription
# -------------------------------
@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for Prescription.
    Displays prescriptions tied to appointments.
    Includes inline medication editing and filtering.
    """
    list_display = ('id', 'appointment', 'doctor_name', 'patient_name', 'created_at')
    search_fields = (
        'appointment__doctor__user__username',
        'appointment__doctor__user__first_name',
        'appointment__doctor__user__last_name',
        'appointment__patient__user__username',
        'appointment__patient__user__first_name',
        'appointment__patient__user__last_name',
        'notes',
    )
    list_filter = ('created_at', 'appointment__doctor__specialization')
    ordering = ('-created_at',)
    inlines = [MedicationInline]

    def doctor_name(self, obj):
        return obj.appointment.doctor.get_full_name_or_username()
    doctor_name.short_description = "Doctor"

    def patient_name(self, obj):
        return obj.appointment.patient.get_full_name_or_username()
    patient_name.short_description = "Patient"

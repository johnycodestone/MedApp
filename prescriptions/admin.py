# prescriptions/admin.py

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
    Displays prescriptions issued by doctors to patients.
    Includes inline medication editing and filtering.
    """
    list_display = ('id', 'doctor', 'patient', 'created_at')
    search_fields = (
        'doctor__user__username',
        'patient__user__username',
        'notes'
    )
    list_filter = ('created_at', 'doctor__specialization')
    ordering = ('-created_at',)
    inlines = [MedicationInline]

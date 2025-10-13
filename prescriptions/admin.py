from django.contrib import admin
from .models import Prescription, Medication

class MedicationInline(admin.TabularInline):
    model = Medication
    extra = 1

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'doctor', 'patient', 'created_at']
    inlines = [MedicationInline]

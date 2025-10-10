# prescriptions/admin.py
from django.contrib import admin
from .models import Prescription, Medication

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "doctor", "created_at", "status")
    search_fields = ("patient__username", "patient__email", "doctor__username", "doctor__email", "notes")
    list_filter = ("status", "created_at")

@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ("id", "prescription", "name", "dosage", "quantity")
    search_fields = ("name",)

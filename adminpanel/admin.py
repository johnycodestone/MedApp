from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User,  # Assuming you have a custom User model
    Patient,
    Doctor,
    Appointment,
    MedicalRecord,
    Prescription
)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active', 'date_joined')

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'age', 'gender', 'contact_number')
    search_fields = ('full_name', 'contact_number')
    list_filter = ('gender', 'age')

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'specialization', 'contact_number')
    search_fields = ('full_name', 'specialization')
    list_filter = ('specialization',)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'appointment_date', 'status')
    search_fields = ('patient__full_name', 'doctor__full_name')
    list_filter = ('status', 'appointment_date')

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'record_date')
    search_fields = ('patient__full_name', 'doctor__full_name')
    list_filter = ('record_date',)

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'prescription_date')
    search_fields = ('patient__full_name', 'doctor__full_name')
    list_filter = ('prescription_date',)

# Customize admin site headers
admin.site.site_header = 'MedApp Administration'
admin.site.site_title = 'MedApp Admin Portal'
admin.site.index_title = 'Welcome to MedApp Admin'

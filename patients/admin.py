# patients/admin.py

from django.contrib import admin
from .models import (
    PatientProfile,
    SavedDoctor,
    MedicalRecord,
    AppointmentHistoryEntry
)

# -------------------------------
# Admin registration for PatientProfile
# -------------------------------
@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for PatientProfile.
    Displays core patient identity and contact info.
    """
    list_display = ('user', 'phone', 'dob', 'gender', 'created_at')
    search_fields = ('user__username', 'phone')
    list_filter = ('gender', 'created_at')

# -------------------------------
# Admin registration for SavedDoctor
# -------------------------------
@admin.register(SavedDoctor)
class SavedDoctorAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for SavedDoctor.
    Tracks which doctors a patient has saved as favorites.
    """
    list_display = ('patient', 'doctor_id', 'saved_at')
    search_fields = ('patient__user__username',)
    list_filter = ('saved_at',)

# -------------------------------
# Admin registration for MedicalRecord
# -------------------------------
@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for MedicalRecord.
    Displays uploaded medical files and notes by patients.
    """
    list_display = ('patient', 'title', 'uploaded_at')
    search_fields = ('title', 'patient__user__username')
    list_filter = ('uploaded_at',)

# -------------------------------
# Admin registration for AppointmentHistoryEntry
# -------------------------------
@admin.register(AppointmentHistoryEntry)
class AppointmentHistoryAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for AppointmentHistoryEntry.
    Displays cached appointment history for patients.
    This is read-only replication from the appointments app.
    """
    list_display = ('patient', 'appointment_id', 'doctor_id', 'started_at', 'status', 'created_at')
    search_fields = ('patient__user__username', 'status')
    list_filter = ('status', 'started_at', 'created_at')

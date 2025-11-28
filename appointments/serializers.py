from rest_framework import serializers
from .models import Appointment
from django.contrib.auth import get_user_model

User = get_user_model()


class AppointmentSerializer(serializers.ModelSerializer):
    # Basic identifiers
    patient_name = serializers.CharField(source='patient.username', read_only=True)
    doctor_name = serializers.CharField(source='doctor.username', read_only=True)

    # Full names for readability
    patient_full_name = serializers.SerializerMethodField()
    doctor_full_name = serializers.SerializerMethodField()

    # Human-readable status
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id',
            'patient',
            'doctor',
            'scheduled_time',
            'status',
            'status_display',
            'reason',
            'created_at',
            'patient_name',
            'doctor_name',
            'patient_full_name',
            'doctor_full_name',
        ]
        read_only_fields = ['status', 'created_at']

    def get_patient_full_name(self, obj):
        if hasattr(obj.patient, "get_full_name"):
            return obj.patient.get_full_name()
        return obj.patient.username

    def get_doctor_full_name(self, obj):
        if hasattr(obj.doctor, "get_full_name"):
            return obj.doctor.get_full_name()
        return obj.doctor.username

from rest_framework import serializers
from .models import DoctorProfile, Timetable, Prescription

class DoctorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorProfile
        fields = ["id", "user", "specialization", "experience_years", "qualification", "bio", "rating"]

class TimetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timetable
        fields = ["id", "file", "uploaded_at", "active"]

class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = ["id", "patient_id", "text", "pdf_file", "created_at"]

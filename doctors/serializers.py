from rest_framework import serializers
from .models import DoctorProfile, Timetable
from prescriptions.models import Prescription   # ✅ import from prescriptions app

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
        fields = ["id", "appointment", "notes", "created_at"]   # ✅ updated fields

from rest_framework import serializers
from .models import PatientProfile, SavedDoctor, MedicalRecord

class PatientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientProfile
        fields = ['id', 'user', 'phone', 'dob', 'gender', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

class SaveDoctorSerializer(serializers.Serializer):
    doctor_id = serializers.IntegerField()

class MedicalRecordUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = ['id', 'title', 'file', 'notes', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']

from rest_framework import serializers
from .models import Hospital, Department, DoctorAssignment, Report

class HospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = ["id", "name", "address", "phone", "created_at"]

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "description"]

class DoctorAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorAssignment
        fields = ["id", "doctor_id", "department", "duty_status", "assigned_at"]

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ["id", "title", "report_file", "created_at"]

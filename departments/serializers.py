from rest_framework import serializers
from .models import Department

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "hospital_id", "name", "description", "head_doctor_id", "created_at"]
        read_only_fields = ["id", "created_at"]

# prescriptions/serializers.py
from rest_framework import serializers
from .models import Prescription, Medication
from django.contrib.auth import get_user_model

User = get_user_model()

class MedicationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Medication
        fields = ["id", "name", "dosage", "frequency", "duration", "instructions", "quantity"]

class PrescriptionSerializer(serializers.ModelSerializer):
    medications = MedicationSerializer(many=True, required=False)
    patient = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    doctor = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Prescription
        fields = ["id", "patient", "doctor", "notes", "status", "created_at", "updated_at", "file", "summary", "medications"]
        read_only_fields = ["created_at", "updated_at", "summary"]

    def create(self, validated_data):
        meds_data = validated_data.pop("medications", [])
        prescription = Prescription.objects.create(**validated_data)
        for med in meds_data:
            Medication.objects.create(prescription=prescription, **med)
        # populate summary
        prescription.summary = self._build_summary_text(prescription)
        prescription.save(update_fields=["summary"])
        return prescription

    def update(self, instance, validated_data):
        meds_data = validated_data.pop("medications", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if meds_data is not None:
            instance.medications.all().delete()
            for med in meds_data:
                Medication.objects.create(prescription=instance, **med)
        # update summary
        instance.summary = self._build_summary_text(instance)
        instance.save(update_fields=["summary"])
        return instance

    def _build_summary_text(self, prescription):
        lines = []
        for m in prescription.medications.all():
            parts = [m.name]
            if m.dosage:
                parts.append(m.dosage)
            if m.frequency:
                parts.append(m.frequency)
            parts.append(f"x{m.quantity}")
            lines.append(" | ".join(parts))
        return "\n".join(lines)

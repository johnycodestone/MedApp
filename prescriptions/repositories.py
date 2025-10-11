# prescriptions/repositories.py
from typing import Optional
from .models import Prescription

class PrescriptionRepository:
    def get_by_id(self, pk: int) -> Optional[Prescription]:
        try:
            return Prescription.objects.prefetch_related("medications").get(pk=pk)
        except Prescription.DoesNotExist:
            return None

    def list_for_patient(self, patient_id):
        return Prescription.objects.filter(patient_id=patient_id).order_by("-created_at").prefetch_related("medications")

    def list_for_doctor(self, doctor_id):
        return Prescription.objects.filter(doctor_id=doctor_id).order_by("-created_at").prefetch_related("medications")

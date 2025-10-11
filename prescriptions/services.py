# prescriptions/services.py
from typing import Optional, List
from django.contrib.auth import get_user_model
from .models import Prescription, Medication
from .repositories import PrescriptionRepository
from .utils import generate_prescription_pdf_bytes

User = get_user_model()

class PrescriptionService:
    def __init__(self, repo: PrescriptionRepository = None):
        self.repo = repo or PrescriptionRepository()

    def create_prescription(self, patient: User, doctor: Optional[User] = None, notes: str = "", medications: Optional[List[dict]] = None, file=None) -> Prescription:
        prescription = Prescription(patient=patient, doctor=doctor, notes=notes)
        if file:
            prescription.file = file
        prescription.save()
        if medications:
            for med in medications:
                Medication.objects.create(prescription=prescription, **med)
        prescription.summary = self._build_summary(prescription)
        prescription.save(update_fields=["summary"])
        return prescription

    def _build_summary(self, prescription: Prescription) -> str:
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

    def get_prescription(self, prescription_id: int) -> Optional[Prescription]:
        return self.repo.get_by_id(prescription_id)

    def generate_pdf(self, prescription: Prescription) -> bytes:
        """
        Returns PDF bytes for the prescription. Uses utils.generate_prescription_pdf_bytes.
        """
        return generate_prescription_pdf_bytes(prescription)

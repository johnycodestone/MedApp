# prescriptions/tasks.py
from celery import shared_task
from .repositories import PrescriptionRepository
from .utils import generate_prescription_pdf_bytes
from django.core.files.base import ContentFile

@shared_task
def generate_pdf_task(prescription_id):
    repo = PrescriptionRepository()
    prescription = repo.get_by_id(prescription_id)
    if not prescription:
        return {"ok": False, "reason": "not_found"}
    try:
        pdf_bytes = generate_prescription_pdf_bytes(prescription)
        if not pdf_bytes:
            return {"ok": False, "reason": "no_pdf_bytes"}
        filename = f"prescription_{prescription.id}.pdf"
        content_file = ContentFile(pdf_bytes, name=filename)
        prescription.file.save(filename, content_file, save=True)
        return {"ok": True, "saved_as": prescription.file.name}
    except Exception as exc:
        return {"ok": False, "reason": str(exc)}

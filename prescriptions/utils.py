# prescriptions/utils.py
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from .models import Prescription

def generate_prescription_pdf_bytes(prescription: Prescription) -> bytes:
    """
    Generate a simple PDF from prescription and return bytes.
    Uses reportlab; install with `pip install reportlab` or replace with other generator.
    """
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, height - 50, f"Prescription #{prescription.id}")
    p.setFont("Helvetica", 11)
    p.drawString(50, height - 80, f"Patient: {prescription.patient}")
    p.drawString(50, height - 100, f"Doctor: {prescription.doctor or 'N/A'}")
    p.drawString(50, height - 120, f"Created: {prescription.created_at.strftime('%Y-%m-%d %H:%M')}")

    y = height - 150
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Medications:")
    y -= 20
    p.setFont("Helvetica", 11)
    for med in prescription.medications.all():
        line = f"- {med.name} | {med.dosage or ''} | {med.frequency or ''} | Qty: {med.quantity}"
        p.drawString(60, y, line)
        y -= 18
        if y < 50:
            p.showPage()
            y = height - 50

    if prescription.notes:
        y -= 10
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, "Notes:")
        y -= 18
        p.setFont("Helvetica", 11)
        for line in prescription.notes.splitlines():
            p.drawString(60, y, line)
            y -= 14
            if y < 50:
                p.showPage()
                y = height - 50

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer.read()

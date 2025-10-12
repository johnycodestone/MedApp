# Placeholder for background tasks (e.g., emailing prescriptions)
from celery import shared_task

@shared_task
def send_prescription_email(prescription_id):
    # Logic to email prescription PDF to patient
    pass

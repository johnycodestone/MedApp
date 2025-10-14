from celery import shared_task
from .models import Prescription

@shared_task
def send_prescription_notification(prescription_id):
    pres = Prescription.objects.get(id=prescription_id)
    # TODO: integrate email/SMS notification
    return f"Notification sent for prescription {prescription_id}"

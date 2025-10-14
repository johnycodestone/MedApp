from celery import shared_task
from .models import Report

@shared_task
def generate_hospital_report(hospital_id):
    # TODO: implement logic
    return f"Report generated for hospital {hospital_id}"

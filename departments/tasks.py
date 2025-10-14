from celery import shared_task
from .models import Department

@shared_task
def send_department_report(hospital_id):
    """Generate or send report of all departments in a hospital."""
    departments = Department.objects.filter(hospital_id=hospital_id)
    # Example: Export to CSV / send email
    return f"{departments.count()} departments processed for hospital {hospital_id}"

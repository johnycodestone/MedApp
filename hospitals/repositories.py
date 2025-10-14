from .models import Hospital, Department, DoctorAssignment, Report

def get_or_create_hospital(user, name, **kwargs):
    hospital, _ = Hospital.objects.get_or_create(user=user, defaults={"name": name, **kwargs})
    return hospital

def add_department(hospital, name, description=""):
    return Department.objects.create(hospital=hospital, name=name, description=description)

def remove_department(hospital, name):
    return Department.objects.filter(hospital=hospital, name=name).delete()

def assign_doctor(hospital, doctor_id, department=None):
    return DoctorAssignment.objects.create(hospital=hospital, doctor_id=doctor_id, department=department)

def waive_duty(hospital, doctor_id):
    return DoctorAssignment.objects.filter(hospital=hospital, doctor_id=doctor_id).update(duty_status="Waived")

def list_reports(hospital):
    return Report.objects.filter(hospital=hospital).order_by("-created_at")

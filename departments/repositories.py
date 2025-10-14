from .models import Department

def create_department(hospital_id, name, description="", head_doctor_id=None):
    return Department.objects.create(
        hospital_id=hospital_id,
        name=name,
        description=description,
        head_doctor_id=head_doctor_id,
    )

def remove_department(hospital_id, name):
    return Department.objects.filter(hospital_id=hospital_id, name=name).delete()

def update_department(dept_id, **kwargs):
    Department.objects.filter(id=dept_id).update(**kwargs)
    return Department.objects.get(id=dept_id)

def list_departments(hospital_id):
    return Department.objects.filter(hospital_id=hospital_id).order_by("name")

def get_department_by_name(hospital_id, name):
    return Department.objects.filter(hospital_id=hospital_id, name=name).first()

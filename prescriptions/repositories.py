from .models import Prescription

def get_prescriptions_for_patient(patient_user):
    return Prescription.objects.filter(patient__user=patient_user).select_related('doctor', 'patient').prefetch_related('medications')

from .models import Prescription, Medication
from doctors.models import DoctorProfile
from patients.models import PatientProfile

def create_prescription_with_medications(data, user):
    doctor = DoctorProfile.objects.get(user=user)
    patient = data.get('patient')
    notes = data.get('notes')
    prescription = Prescription.objects.create(doctor=doctor, patient=patient, notes=notes)

    medications_data = data.get('medications', [])
    for med in medications_data:
        Medication.objects.create(prescription=prescription, **med)

    return prescription

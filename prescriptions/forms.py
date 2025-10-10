# prescriptions/forms.py
from django import forms
from .models import Prescription, Medication

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ["patient", "doctor", "notes", "file", "status"]

class MedicationForm(forms.ModelForm):
    class Meta:
        model = Medication
        exclude = ("prescription",)

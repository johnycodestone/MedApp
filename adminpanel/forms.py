from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import (
    User,
    Patient,
    Doctor,
    Appointment,
    MedicalRecord,
    Prescription
)

class CustomUserCreationForm(UserCreationForm):
    """
    A form for creating new users. Includes all required fields.
    """
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class CustomUserChangeForm(UserChangeForm):
    """
    A form for updating users. Includes all required fields.
    """
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

class PatientAdminForm(forms.ModelForm):
    """
    Admin form for Patient model with additional validation
    """
    class Meta:
        model = Patient
        fields = '__all__'
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_contact_number(self):
        contact = self.cleaned_data.get('contact_number')
        if not contact.isdigit():
            raise forms.ValidationError("Contact number must contain only digits")
        return contact

class DoctorAdminForm(forms.ModelForm):
    """
    Admin form for Doctor model with additional validation
    """
    class Meta:
        model = Doctor
        fields = '__all__'
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
        }

class AppointmentAdminForm(forms.ModelForm):
    """
    Admin form for Appointment model with additional validation
    """
    class Meta:
        model = Appointment
        fields = '__all__'
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'doctor': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        patient = cleaned_data.get('patient')
        doctor = cleaned_data.get('doctor')
        
        if patient and doctor and patient == doctor:
            raise forms.ValidationError("Patient cannot be the same as the doctor")
        
        return cleaned_data

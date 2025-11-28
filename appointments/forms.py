from django import forms
from django.utils import timezone
from .models import Appointment
from doctors.models import DoctorProfile


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'scheduled_time', 'reason']
        widgets = {
            'doctor': forms.Select(
                attrs={'class': 'form-control'}
            ),
            'scheduled_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
            'reason': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'Reason for appointment (optional)',
                    'class': 'form-control'
                }
            ),
        }

    def clean_scheduled_time(self):
        scheduled_time = self.cleaned_data.get('scheduled_time')
        doctor = self.cleaned_data.get('doctor')

        # Ensure scheduled_time is provided
        if not scheduled_time:
            raise forms.ValidationError("Please select a valid time slot.")

        # Ensure slot is not in the past
        if scheduled_time < timezone.now():
            raise forms.ValidationError("You cannot book an appointment in the past.")

        # Ensure slot is not already booked for this doctor
        if doctor and Appointment.objects.filter(
            doctor=doctor,
            scheduled_time=scheduled_time,
            status__in=['pending', 'confirmed']
        ).exists():
            raise forms.ValidationError("This time slot is already booked for the selected doctor.")

        return scheduled_time

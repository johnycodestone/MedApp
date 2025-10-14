from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import ScheduleCategory, Schedule, ScheduleReminder

class ScheduleCategoryForm(forms.ModelForm):
    """
    Form for creating and updating Schedule Categories
    """
    class Meta:
        model = ScheduleCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean_name(self):
        """
        Validate category name is unique
        """
        name = self.cleaned_data.get('name')
        if ScheduleCategory.objects.filter(name__iexact=name).exists():
            raise ValidationError("A category with this name already exists.")
        return name

class ScheduleForm(forms.ModelForm):
    """
    Form for creating and updating Schedules
    """
    class Meta:
        model = Schedule
        fields = [
            'title', 
            'description', 
            'doctor', 
            'patient', 
            'category', 
            'start_time', 
            'end_time', 
            'status', 
            'priority',
            'is_recurring',
            'recurrence_pattern'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'recurrence_pattern': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean(self):
        """
        Validate schedule times and constraints
        """
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        doctor = cleaned_data.get('doctor')
        patient = cleaned_data.get('patient')
        
        # Validate time constraints
        if start_time and end_time:
            if start_time >= end_time:
                raise ValidationError("End time must be after start time")
            
            if start_time < timezone.now():
                raise ValidationError("Schedule cannot be in the past")
        
        # Validate doctor and patient are not the same
        if doctor and patient and doctor == patient:
            raise ValidationError("Doctor and patient cannot be the same")
        
        return cleaned_data

class ScheduleReminderForm(forms.ModelForm):
    """
    Form for creating and updating Schedule Reminders
    """
    class Meta:
        model = ScheduleReminder
        fields = ['schedule', 'reminder_type', 'send_time']
        widgets = {
            'schedule': forms.Select(attrs={'class': 'form-control'}),
            'reminder_type': forms.Select(attrs={'class': 'form-control'}),
            'send_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
    
    def clean(self):
        """
        Validate reminder constraints
        """
        cleaned_data = super().clean()
        schedule = cleaned_data.get('schedule')
        send_time = cleaned_data.get('send_time')
        
        # Validate send time is before schedule start time
        if schedule and send_time:
            if send_time >= schedule.start_time:
                raise ValidationError("Reminder send time must be before schedule start time")
        
        return cleaned_data

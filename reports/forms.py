from django import forms
from django.core.exceptions import ValidationError
from .models import ReportCategory, Report, ReportTemplate

class ReportCategoryForm(forms.ModelForm):
    """
    Form for creating and updating Report Categories
    """
    class Meta:
        model = ReportCategory
        fields = ['name', 'description', 'report_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'report_type': forms.Select(attrs={'class': 'form-control'})
        }
    
    def clean_name(self):
        """
        Validate category name is unique
        """
        name = self.cleaned_data.get('name')
        if ReportCategory.objects.filter(name__iexact=name).exists():
            raise ValidationError("A category with this name already exists.")
        return name

class ReportForm(forms.ModelForm):
    """
    Form for creating and updating Reports
    """
    class Meta:
        model = Report
        fields = [
            'title', 
            'description', 
            'doctor', 
            'patient', 
            'category', 
            'content', 
            'status', 
            'priority'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'content': forms.JSONField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5})),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'})
        }
    
    def clean(self):
        """
        Validate report constraints
        """
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        patient = cleaned_data.get('patient')
        
        if doctor and patient and doctor == patient:
            raise ValidationError("Doctor and patient cannot be the same")
        
        return cleaned_data

class ReportTemplateForm(forms.ModelForm):
    """
    Form for creating and updating Report Templates
    """
    class Meta:
        model = ReportTemplate
        fields = ['name', 'description', 'template_structure', 'category']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'template_structure': forms.JSONField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5})),
            'category': forms.Select(attrs={'class': 'form-control'})
        }
    
    def clean_name(self):
        """
        Validate template name is unique
        """
        name = self.cleaned_data.get('name')
        if ReportTemplate.objects.filter(name__iexact=name).exists():
            raise ValidationError("A template with this name already exists.")
        return name

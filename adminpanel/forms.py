# adminpanel/forms.py

from django import forms
from .models import (
    SystemConfiguration,
    BackupRecord,
    RolePermission
)

# -------------------------------
# Form for SystemConfiguration
# -------------------------------
class SystemConfigurationForm(forms.ModelForm):
    """
    Admin form for managing system configuration entries.
    Includes validation for key uniqueness and value formatting.
    """
    class Meta:
        model = SystemConfiguration
        fields = '__all__'
        widgets = {
            'key': forms.TextInput(attrs={'class': 'form-control'}),
            'value': forms.Textarea(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def clean_key(self):
        key = self.cleaned_data.get('key')
        if SystemConfiguration.objects.filter(key__iexact=key).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A configuration with this key already exists.")
        return key

# -------------------------------
# Form for BackupRecord
# -------------------------------
class BackupRecordForm(forms.ModelForm):
    """
    Admin form for managing backup records.
    """
    class Meta:
        model = BackupRecord
        fields = '__all__'
        widgets = {
            'file_path': forms.TextInput(attrs={'class': 'form-control'}),
            'error_message': forms.Textarea(attrs={'class': 'form-control'}),
        }

# -------------------------------
# Form for RolePermission
# -------------------------------
class RolePermissionForm(forms.ModelForm):
    """
    Admin form for assigning permissions to roles.
    """
    class Meta:
        model = RolePermission
        fields = '__all__'
        widgets = {
            'permission_key': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

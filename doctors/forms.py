# doctors/forms.py
from django import forms
from .models import DoctorProfile, SPECIALIZATION_CHOICES

class DoctorProfileForm(forms.ModelForm):
    specialization = forms.ChoiceField(choices=SPECIALIZATION_CHOICES)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("DoctorProfileForm loaded — specialization widget:", type(self.fields["specialization"].widget))

    class Meta:
        model = DoctorProfile
        fields = "__all__"

from django import forms


class UrgencyForm(forms.Form):
    """
    Patient-facing vitals form for urgency prediction.
    """

    age = forms.IntegerField(
        min_value=1,
        max_value=120,
        label="Age",
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )

    temp = forms.FloatField(
        label="Temperature (°F)",
        help_text="Normal: 97 – 99 °F",
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.1"})
    )

    hr = forms.IntegerField(
        min_value=30,
        max_value=200,
        label="Heart Rate (bpm)",
        help_text="Normal: 60 – 100 bpm (resting adult)",
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )

    bp_sys = forms.IntegerField(
        min_value=70,
        max_value=250,
        label="Systolic BP (mmHg)",
        help_text="Normal: 90 – 120 mmHg",
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )

    bp_dia = forms.IntegerField(
        min_value=40,
        max_value=150,
        label="Diastolic BP (mmHg)",
        help_text="Normal: 60 – 80 mmHg",
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )

    resp_rate = forms.IntegerField(
        min_value=8,
        max_value=40,
        label="Respiratory Rate (breaths/min)",
        help_text="Normal: 12 – 20 breaths/min",
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )

    chest_pain = forms.BooleanField(
        required=False,
        label="Chest Pain",
        help_text="Check if you are experiencing chest pain right now",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    bleeding = forms.BooleanField(
        required=False,
        label="Bleeding",
        help_text="Check if you have active bleeding",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    fever = forms.BooleanField(
        required=False,
        label="Fever",
        help_text="Check if you currently have a fever",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    vomiting = forms.BooleanField(
        required=False,
        label="Vomiting",
        help_text="Check if you are currently vomiting",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )


class DiabetesForm(forms.Form):
    """
    Inputs aligned to Diabetes.csv columns (excluding Class).
    """

    gender = forms.ChoiceField(
        choices=[('0', 'Female'), ('1', 'Male')],
        label="Gender",
        help_text="0 = Female, 1 = Male",
        widget=forms.Select(attrs={"class": "form-select"})
    )

    age = forms.IntegerField(
        min_value=1,
        max_value=120,
        label="Age",
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )

    urea = forms.FloatField(
        label="Urea (mg/dL)",
        help_text="Normal: 15 – 40 mg/dL",
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.1"})
    )

    cr = forms.FloatField(
        label="Creatinine (mg/dL)",
        help_text="Normal: 0.6 – 1.3 mg/dL",
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.1"})
    )

    hba1c = forms.FloatField(
        label="HbA1c (%)",
        help_text="Normal: < 5.7% | Pre-diabetes: 5.7 – 6.4% | Diabetes: ≥ 6.5%",
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.1"})
    )

    chol = forms.FloatField(
        label="Total Cholesterol (mg/dL)",
        help_text="Desirable: < 200 mg/dL",
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.1"})
    )

    tg = forms.FloatField(
        label="Triglycerides (mg/dL)",
        help_text="Normal: < 150 mg/dL",
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.1"})
    )

    hdl = forms.FloatField(
        label="HDL (mg/dL)",
        help_text="Men: > 40 mg/dL | Women: > 50 mg/dL",
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.1"})
    )

    ldl = forms.FloatField(
        label="LDL (mg/dL)",
         help_text="Optimal: < 100 mg/dL",
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.1"})
    )

    vldl = forms.FloatField(
        label="VLDL (mg/dL)",
        help_text="Normal: 5 – 40 mg/dL",
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.1"})
    )

    bmi = forms.FloatField(
        label="BMI",
        help_text="Normal: 18.5 – 24.9",
        widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.1"})
    )

    def clean_gender(self):
        return int(self.cleaned_data['gender'])

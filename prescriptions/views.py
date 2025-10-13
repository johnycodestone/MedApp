from django.shortcuts import render, get_object_or_404, redirect
from .models import Prescription
from .forms import PrescriptionForm, MedicationForm
from .services import create_prescription_with_medications

def prescription_list(request):
    prescriptions = Prescription.objects.filter(patient__user=request.user)
    return render(request, 'prescriptions/list.html', {'prescriptions': prescriptions})

def create_prescription(request):
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = create_prescription_with_medications(form.cleaned_data, request.user)
            return redirect('prescriptions:list')
    else:
        form = PrescriptionForm()
    return render(request, 'prescriptions/create.html', {'form': form})

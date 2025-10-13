from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import TemplateView, ListView, DetailView
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.db.models import Count
from django.http import JsonResponse

from .models import (
    Patient, 
    Doctor, 
    Appointment, 
    MedicalRecord, 
    Prescription
)
from .serializers import (
    PatientSerializer, 
    DoctorSerializer, 
    AppointmentSerializer, 
    MedicalRecordSerializer, 
    PrescriptionSerializer
)
from .permissions import StrictAdminAccess, IsAdminOrReadOnly

class AdminDashboardView(TemplateView):
    """
    Main admin dashboard view
    """
    template_name = 'adminpanel/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_patients'] = Patient.objects.count()
        context['total_doctors'] = Doctor.objects.count()
        context['total_appointments'] = Appointment.objects.count()
        context['recent_appointments'] = Appointment.objects.order_by('-appointment_date')[:5]
        return context

class PatientViewSet(viewsets.ModelViewSet):
    """
    Viewset for Patient model with admin-level access control
    """
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [StrictAdminAccess]
    
    @action(detail=False, methods=['GET'])
    def patient_stats(self, request):
        """
        Custom action to get patient statistics
        """
        total_patients = self.queryset.count()
        gender_breakdown = self.queryset.values('gender').annotate(count=Count('gender'))
        
        return Response({
            'total_patients': total_patients,
            'gender_breakdown': list(gender_breakdown)
        })

class DoctorViewSet(viewsets.ModelViewSet):
    """
    Viewset for Doctor model with admin-level access control
    """
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [StrictAdminAccess]
    
    @action(detail=False, methods=['GET'])
    def specialization_stats(self, request):
        """
        Custom action to get doctor specialization statistics
        """
        specialization_breakdown = self.queryset.values('specialization').annotate(count=Count('specialization'))
        
        return Response({
            'specialization_breakdown': list(specialization_breakdown)
        })

class AppointmentViewSet(viewsets.ModelViewSet):
    """
    Viewset for Appointment model with admin-level access control
    """
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [StrictAdminAccess]
    
    @action(detail=False, methods=['GET'])
    def appointment_stats(self, request):
        """
        Custom action to get appointment statistics
        """
        total_appointments = self.queryset.count()
        status_breakdown = self.queryset.values('status').annotate(count=Count('status'))
        
        return Response({
            'total_appointments': total_appointments,
            'status_breakdown': list(status_breakdown)
        })

# Error Handler Views
def bad_request(request, exception):
    """
    Custom 400 error handler
    """
    return render(request, 'adminpanel/errors/400.html', status=400)

def permission_denied(request, exception):
    """
    Custom 403 error handler
    """
    return render(request, 'adminpanel/errors/403.html', status=403)

def page_not_found(request, exception):
    """
    Custom 404 error handler
    """
    return render(request, 'adminpanel/errors/404.html', status=404)

def server_error(request):
    """
    Custom 500 error handler
    """
    return render(request, 'adminpanel/errors/500.html', status=500)

# Authentication Views
@staff_member_required
def admin_login_view(request):
    """
    Custom admin login view with additional security checks
    """
    # Implement login logic here
    pass

@login_required
def admin_logout_view(request):
    """
    Custom admin logout view
    """
    # Implement logout logic here
    pass

@staff_member_required
def admin_password_reset_view(request):
    """
    Custom admin password reset view
    """
    # Implement password reset logic here
    pass

# Utility Views
@staff_member_required
def patient_count_view(request):
    """
    View to get patient count
    """
    patient_count = Patient.objects.count()
    return JsonResponse({'patient_count': patient_count})

@staff_member_required
def appointment_stats_view(request):
    """
    View to get appointment statistics
    """
    total_appointments = Appointment.objects.count()
    pending_appointments = Appointment.objects.filter(status='pending').count()
    completed_appointments = Appointment.objects.filter(status='completed').count()
    
    return JsonResponse({
        'total_appointments': total_appointments,
        'pending_appointments': pending_appointments,
        'completed_appointments': completed_appointments
    })

@staff_member_required
def revenue_summary_view(request):
    """
    View to get revenue summary
    """
    # Implement revenue calculation logic
    pass

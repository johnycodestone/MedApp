from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from adminpanel.models import (
    Patient, 
    Doctor, 
    Appointment, 
    MedicalRecord, 
    Prescription
)
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class AdminPanelViewsTest(TestCase):
    def setUp(self):
        """
        Set up test data for admin panel views
        """
        # Create test users
        self.admin_user = User.objects.create_superuser(
            username='admin', 
            email='admin@example.com', 
            password='adminpass123'
        )
        self.doctor_user = User.objects.create_user(
            username='doctor', 
            email='doctor@example.com', 
            password='doctorpass123'
        )
        self.patient_user = User.objects.create_user(
            username='patient', 
            email='patient@example.com', 
            password='patientpass123'
        )
        
        # Create test doctor and patient
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            full_name='Dr. John Doe',
            specialization='Cardiology',
            contact_number='1234567890'
        )
        self.patient = Patient.objects.create(
            user=self.patient_user,
            full_name='Jane Smith',
            age=35,
            gender='Female',
            contact_number='9876543210'
        )
        
        # Create test appointment
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timedelta(days=1),
            status=Appointment.AppointmentStatus.PENDING,
            reason='Routine Check-up'
        )
        
        # Create test medical record
        self.medical_record = MedicalRecord.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            diagnosis='Hypertension',
            treatment='Medication and Lifestyle Changes'
        )
        
        # Create test prescription
        self.prescription = Prescription.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            medication='Lisinopril',
            dosage='10mg',
            frequency='Once daily'
        )
        
        # Setup clients
        self.client = Client()
        self.api_client = APIClient()

    def test_admin_dashboard_view(self):
        """
        Test admin dashboard view access
        """
        # Test unauthenticated access
        response = self.client.get(reverse('admin-dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Test admin access
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('admin-dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'adminpanel/dashboard.html')

    def test_patient_viewset_api(self):
        """
        Test Patient ViewSet API endpoints
        """
        # Authenticate as admin
        self.api_client.force_authenticate(user=self.admin_user)
        
        # Test list endpoint
        response = self.api_client.get(reverse('patient-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test retrieve endpoint
        response = self.api_client.get(reverse('patient-detail', kwargs={'pk': self.patient.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test create endpoint
        new_patient_data = {
            'user': self.patient_user.id,
            'full_name': 'New Patient',
            'age': 40,
            'gender': 'Female',
            'contact_number': '5555555555'
        }
        response = self.api_client.post(reverse('patient-list'), new_patient_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_doctor_viewset_api(self):
        """
        Test Doctor ViewSet API endpoints
        """
        # Authenticate as admin
        self.api_client.force_authenticate(user=self.admin_user)
        
        # Test list endpoint
        response = self.api_client.get(reverse('doctor-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test retrieve endpoint
        response = self.api_client.get(reverse('doctor-detail', kwargs={'pk': self.doctor.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test create endpoint
        new_doctor_data = {
            'user': self.doctor_user.id,
            'full_name': 'Dr. New Doctor',
            'specialization': 'Neurology',
            'contact_number': '7777777777',
            'consultation_fee': 600.00
        }
        response = self.api_client.post(reverse('doctor-list'), new_doctor_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_appointment_viewset_api(self):
        """
        Test Appointment ViewSet API endpoints
        """
        # Authenticate as admin
        self.api_client.force_authenticate(user=self.admin_user)
        
        # Test list endpoint
        response = self.api_client.get(reverse('appointment-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test retrieve endpoint
        response = self.api_client.get(reverse('appointment-detail', kwargs={'pk': self.appointment.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test create endpoint
        new_appointment_data = {
            'patient': self.patient.id,
            'doctor': self.doctor.id,
            'appointment_date': (timezone.now() + timedelta(days=7)).isoformat(),
            'status': Appointment.AppointmentStatus.PENDING,
            'reason': 'Follow-up Consultation'
        }
        response = self.api_client.post(reverse('appointment-list'), new_appointment_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_medical_record_viewset_api(self):
        """
        Test MedicalRecord ViewSet API endpoints
        """
        # Authenticate as admin
        self.api_client.force_authenticate(user=self.admin_user)
        
        # Test list endpoint
        response = self.api_client.get(reverse('medical-record-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test retrieve endpoint
        response = self.api_client.get(reverse('medical-record-detail', kwargs={'pk': self.medical_record.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test create endpoint
        new_medical_record_data = {
            'patient': self.patient.id,
            'doctor': self.doctor.id,
            'diagnosis': 'Diabetes',
            'treatment': 'Insulin and Diet Management'
        }
        response = self.api_client.post(reverse('medical-record-list'), new_medical_record_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_prescription_viewset_api(self):
        """
        Test Prescription ViewSet API endpoints
        """
        # Authenticate as admin
        self.api_client.force_authenticate(user=self.admin_user)
        
        # Test list endpoint
        response = self.api_client.get(reverse('prescription-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test retrieve endpoint
        response = self.api_client.get(reverse('prescription-detail', kwargs={'pk': self.prescription.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test create endpoint
        new_prescription_data = {
            'patient': self.patient.id,
            'doctor': self.doctor.id,
            'medication': 'Metformin',
            'dosage': '500mg',
            'frequency': 'Twice daily'
        }
        response = self.api_client.post(reverse('prescription-list'), new_prescription_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unauthorized_access(self):
        """
        Test unauthorized access to admin panel endpoints
        """
        # Authenticate as a non-admin user
        self.api_client.force_authenticate(user=self.patient_user)
        
        # Test create patient (should be forbidden)
        new_patient_data = {
            'full_name': 'Unauthorized Patient',
            'age': 25,
            'gender': 'Male'
        }
        response = self.api_client.post(reverse('patient-list'), new_patient_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_custom_actions(self):
        """
        Test custom ViewSet actions
        """
        # Authenticate as admin
        self.api_client.force_authenticate(user=self.admin_user)
        
        # Test patient stats
        response = self.api_client.get(reverse('patient-stats'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test doctor stats
        response = self.api_client.get(reverse('doctor-stats'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Test appointment stats
        response = self.api_client.get(reverse('appointment-stats'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date
from adminpanel.models import (
    Patient, 
    Doctor, 
    Appointment, 
    MedicalRecord, 
    Prescription
)

User = get_user_model()

class PatientModelTest(TestCase):
    def setUp(self):
        """
        Set up test data for Patient model
        """
        self.user = User.objects.create_user(
            username='testpatient', 
            email='patient@example.com', 
            password='testpass123'
        )
        self.patient = Patient.objects.create(
            user=self.user,
            full_name='John Doe',
            age=35,
            gender='Male',
            contact_number='1234567890',
            address='123 Test Street',
            blood_group='A+'
        )
    
    def test_patient_creation(self):
        """
        Test Patient model creation
        """
        self.assertEqual(self.patient.full_name, 'John Doe')
        self.assertEqual(self.patient.age, 35)
        self.assertEqual(self.patient.gender, 'Male')
    
    def test_patient_str_method(self):
        """
        Test string representation of Patient
        """
        self.assertEqual(str(self.patient), 'John Doe')
    
    def test_patient_contact_number_validation(self):
        """
        Test contact number validation
        """
        with self.assertRaises(ValidationError):
            invalid_patient = Patient(
                user=self.user,
                full_name='Invalid Patient',
                contact_number='invalid_number'
            )
            invalid_patient.full_clean()

class DoctorModelTest(TestCase):
    def setUp(self):
        """
        Set up test data for Doctor model
        """
        self.user = User.objects.create_user(
            username='testdoctor', 
            email='doctor@example.com', 
            password='testpass123'
        )
        self.doctor = Doctor.objects.create(
            user=self.user,
            full_name='Dr. Jane Smith',
            specialization='Cardiology',
            contact_number='9876543210',
            consultation_fee=500.00
        )
    
    def test_doctor_creation(self):
        """
        Test Doctor model creation
        """
        self.assertEqual(self.doctor.full_name, 'Dr. Jane Smith')
        self.assertEqual(self.doctor.specialization, 'Cardiology')
        self.assertEqual(self.doctor.consultation_fee, 500.00)
    
    def test_doctor_str_method(self):
        """
        Test string representation of Doctor
        """
        self.assertEqual(str(self.doctor), 'Dr. Jane Smith')

class AppointmentModelTest(TestCase):
    def setUp(self):
        """
        Set up test data for Appointment model
        """
        # Create test doctor and patient
        self.doctor_user = User.objects.create_user(
            username='doctor', 
            email='doctor@example.com', 
            password='testpass123'
        )
        self.patient_user = User.objects.create_user(
            username='patient', 
            email='patient@example.com', 
            password='testpass123'
        )
        
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            full_name='Dr. John Doe',
            specialization='Neurology'
        )
        
        self.patient = Patient.objects.create(
            user=self.patient_user,
            full_name='Jane Smith',
            age=30,
            gender='Female'
        )
        
        # Create test appointment
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            appointment_date=timezone.now() + timezone.timedelta(days=1),
            status=Appointment.AppointmentStatus.PENDING,
            reason='Routine Check-up'
        )
    
    def test_appointment_creation(self):
        """
        Test Appointment model creation
        """
        self.assertEqual(self.appointment.patient, self.patient)
        self.assertEqual(self.appointment.doctor, self.doctor)
        self.assertEqual(self.appointment.status, Appointment.AppointmentStatus.PENDING)
    
    def test_appointment_str_method(self):
        """
        Test string representation of Appointment
        """
        self.assertTrue(str(self.appointment).startswith('Appointment for Jane Smith'))
    
    def test_past_appointment_validation(self):
        """
        Test validation for past appointment dates
        """
        with self.assertRaises(ValidationError):
            past_appointment = Appointment(
                patient=self.patient,
                doctor=self.doctor,
                appointment_date=timezone.now() - timezone.timedelta(days=1)
            )
            past_appointment.full_clean()

class MedicalRecordModelTest(TestCase):
    def setUp(self):
        """
        Set up test data for MedicalRecord model
        """
        # Create test doctor and patient
        self.doctor_user = User.objects.create_user(
            username='doctor', 
            email='doctor@example.com', 
            password='testpass123'
        )
        self.patient_user = User.objects.create_user(
            username='patient', 
            email='patient@example.com', 
            password='testpass123'
        )
        
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            full_name='Dr. Emily Johnson',
            specialization='Pediatrics'
        )
        
        self.patient = Patient.objects.create(
            user=self.patient_user,
            full_name='Tommy Brown',
            age=8,
            gender='Male'
        )
        
        # Create test medical record
        self.medical_record = MedicalRecord.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            diagnosis='Common Cold',
            treatment='Rest and Hydration',
            notes='Patient needs follow-up in a week'
        )
    
    def test_medical_record_creation(self):
        """
        Test MedicalRecord model creation
        """
        self.assertEqual(self.medical_record.patient, self.patient)
        self.assertEqual(self.medical_record.doctor, self.doctor)
        self.assertEqual(self.medical_record.diagnosis, 'Common Cold')
    
    def test_medical_record_str_method(self):
        """
        Test string representation of MedicalRecord
        """
        self.assertTrue(str(self.medical_record).startswith('Medical Record for Tommy Brown'))

class PrescriptionModelTest(TestCase):
    def setUp(self):
        """
        Set up test data for Prescription model
        """
        # Create test doctor and patient
        self.doctor_user = User.objects.create_user(
            username='doctor', 
            email='doctor@example.com', 
            password='testpass123'
        )
        self.patient_user = User.objects.create_user(
            username='patient', 
            email='patient@example.com', 
            password='testpass123'
        )
        
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            full_name='Dr. Michael Lee',
            specialization='Oncology'
        )
        
        self.patient = Patient.objects.create(
            user=self.patient_user,
            full_name='Sarah Williams',
            age=45,
            gender='Female'
        )
        
        # Create test prescription
        self.prescription = Prescription.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            medication='Paracetamol',
            dosage='500mg',
            frequency='Twice daily',
            duration='7 days'
        )
    
    def test_prescription_creation(self):
        """
        Test Prescription model creation
        """
        self.assertEqual(self.prescription.patient, self.patient)
        self.assertEqual(self.prescription.doctor, self.doctor)
        self.assertEqual(self.prescription.medication, 'Paracetamol')
    
    def test_prescription_str_method(self):
        """
        Test string representation of Prescription
        """
        self.assertTrue(str(self.prescription).startswith('Prescription for Sarah Williams'))

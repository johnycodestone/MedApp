"""
accounts/tests/test_models.py

Unit tests for accounts models.
Tests model creation, validation, and methods.
"""

from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from accounts.models import CustomUser, VerificationToken, UserActivity


class CustomUserModelTest(TestCase):
    """Test cases for CustomUser model"""
    
    def setUp(self):
        """Set up test data"""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'PATIENT'
        }
    
    def test_create_user(self):
        """Test creating a user"""
        user = CustomUser.objects.create_user(**self.user_data)
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.role, 'PATIENT')
        self.assertTrue(user.check_password('TestPass123!'))
        self.assertFalse(user.is_verified)
        self.assertTrue(user.is_active)
    
    def test_user_role_methods(self):
        """Test role checking methods"""
        # Test patient
        patient = CustomUser.objects.create_user(
            username='patient',
            email='patient@example.com',
            password='pass123',
            role='PATIENT'
        )
        self.assertTrue(patient.is_patient())
        self.assertFalse(patient.is_doctor())
        self.assertFalse(patient.is_hospital())
        self.assertFalse(patient.is_admin())
        
        # Test doctor
        doctor = CustomUser.objects.create_user(
            username='doctor',
            email='doctor@example.com',
            password='pass123',
            role='DOCTOR'
        )
        self.assertTrue(doctor.is_doctor())
        self.assertFalse(doctor.is_patient())
        
        # Test hospital
        hospital = CustomUser.objects.create_user(
            username='hospital',
            email='hospital@example.com',
            password='pass123',
            role='HOSPITAL'
        )
        self.assertTrue(hospital.is_hospital())
        
        # Test admin
        admin = CustomUser.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='pass123',
            role='ADMIN'
        )
        self.assertTrue(admin.is_admin())
    
    def test_user_str_representation(self):
        """Test string representation of user"""
        user = CustomUser.objects.create_user(**self.user_data)
        expected = "testuser (Patient)"
        self.assertEqual(str(user), expected)
    
    def test_email_case_insensitive(self):
        """Test that emails are stored in lowercase"""
        user = CustomUser.objects.create_user(
            username='testuser',
            email='Test@EXAMPLE.COM',
            password='pass123',
            role='PATIENT'
        )
        self.assertEqual(user.email, 'test@example.com')


class VerificationTokenModelTest(TestCase):
    """Test cases for VerificationToken model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='pass123',
            role='PATIENT'
        )
    
    def test_create_verification_token(self):
        """Test creating a verification token"""
        expires_at = timezone.now() + timedelta(hours=24)
        token = VerificationToken.objects.create(
            user=self.user,
            token='test_token_123',
            token_type='EMAIL',
            expires_at=expires_at
        )
        
        self.assertEqual(token.user, self.user)
        self.assertEqual(token.token, 'test_token_123')
        self.assertEqual(token.token_type, 'EMAIL')
        self.assertFalse(token.is_used)
    
    def test_token_is_valid(self):
        """Test token validity checking"""
        # Valid token
        expires_at = timezone.now() + timedelta(hours=24)
        valid_token = VerificationToken.objects.create(
            user=self.user,
            token='valid_token',
            token_type='EMAIL',
            expires_at=expires_at
        )
        self.assertTrue(valid_token.is_valid())
        
        # Expired token
        expires_at = timezone.now() - timedelta(hours=1)
        expired_token = VerificationToken.objects.create(
            user=self.user,
            token='expired_token',
            token_type='EMAIL',
            expires_at=expires_at
        )
        self.assertFalse(expired_token.is_valid())
        
        # Used token
        expires_at = timezone.now() + timedelta(hours=24)
        used_token = VerificationToken.objects.create(
            user=self.user,
            token='used_token',
            token_type='EMAIL',
            expires_at=expires_at,
            is_used=True
        )
        self.assertFalse(used_token.is_valid())


class UserActivityModelTest(TestCase):
    """Test cases for UserActivity model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='pass123',
            role='PATIENT'
        )
    
    def test_create_activity(self):
        """Test creating a user activity"""
        activity = UserActivity.objects.create(
            user=self.user,
            action='LOGIN',
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0',
            metadata={'success': True}
        )
        
        self.assertEqual(activity.user, self.user)
        self.assertEqual(activity.action, 'LOGIN')
        self.assertEqual(activity.ip_address, '192.168.1.1')
        self.assertEqual(activity.metadata['success'], True)
    
    def test_activity_str_representation(self):
        """Test string representation of activity"""
        activity = UserActivity.objects.create(
            user=self.user,
            action='LOGIN'
        )
        self.assertIn('testuser', str(activity))
        self.assertIn('Login', str(activity))
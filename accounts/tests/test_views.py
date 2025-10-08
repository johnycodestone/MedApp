"""
accounts/tests/test_views.py

Unit tests for accounts views.
Tests API endpoints and HTML views.
"""

from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from accounts.models import CustomUser


class UserRegistrationAPITestCase(APITestCase):
    """Test cases for user registration API"""
    
    def setUp(self):
        """Set up test client"""
        self.client = APIClient()
        self.register_url = reverse('accounts:api_register')
    
    def test_register_user_success(self):
        """Test successful user registration"""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'PATIENT'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('verification_token', response.data)
        
        # Check user exists in database
        user = CustomUser.objects.get(username='newuser')
        self.assertEqual(user.email, 'new@example.com')
    
    def test_register_duplicate_username(self):
        """Test registration with duplicate username"""
        CustomUser.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='pass123',
            role='PATIENT'
        )
        
        data = {
            'username': 'existinguser',
            'email': 'new@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!',
            'role': 'PATIENT'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_password_mismatch(self):
        """Test registration with mismatched passwords"""
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'DifferentPass123!',
            'role': 'PATIENT'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginAPITestCase(APITestCase):
    """Test cases for user login API"""
    
    def setUp(self):
        """Set up test client and user"""
        self.client = APIClient()
        self.login_url = reverse('accounts:api_login')
        
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            role='PATIENT'
        )
        self.user.is_active = True
        self.user.save()
    
    def test_login_with_username(self):
        """Test login with username"""
        data = {
            'username_or_email': 'testuser',
            'password': 'TestPass123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
    
    def test_login_with_email(self):
        """Test login with email"""
        data = {
            'username_or_email': 'test@example.com',
            'password': 'TestPass123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        data = {
            'username_or_email': 'testuser',
            'password': 'WrongPassword123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
    
    def test_login_inactive_user(self):
        """Test login with inactive account"""
        self.user.is_active = False
        self.user.save()
        
        data = {
            'username_or_email': 'testuser',
            'password': 'TestPass123!'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserProfileAPITestCase(APITestCase):
    """Test cases for user profile API"""
    
    def setUp(self):
        """Set up test client and user"""
        self.client = APIClient()
        self.profile_url = reverse('accounts:api_profile')
        
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            role='PATIENT',
            first_name='Test',
            last_name='User'
        )
        
        # Authenticate
        self.client.force_authenticate(user=self.user)
    
    def test_get_profile(self):
        """Test retrieving user profile"""
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')
    
    def test_update_profile(self):
        """Test updating user profile"""
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone': '+1234567890'
        }
        
        response = self.client.patch(self.profile_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['first_name'], 'Updated')
        self.assertEqual(response.data['user']['last_name'], 'Name')
        
        # Verify in database
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
    
    def test_profile_unauthorized(self):
        """Test accessing profile without authentication"""
        self.client.force_authenticate(user=None)
        
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PasswordChangeAPITestCase(APITestCase):
    """Test cases for password change API"""
    
    def setUp(self):
        """Set up test client and user"""
        self.client = APIClient()
        self.change_password_url = reverse('accounts:api_change_password')
        
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='OldPass123!',
            role='PATIENT'
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_change_password_success(self):
        """Test successful password change"""
        data = {
            'old_password': 'OldPass123!',
            'new_password': 'NewPass123!',
            'new_password_confirm': 'NewPass123!'
        }
        
        response = self.client.post(self.change_password_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify new password works
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPass123!'))
    
    def test_change_password_wrong_old_password(self):
        """Test password change with wrong old password"""
        data = {
            'old_password': 'WrongOldPass123!',
            'new_password': 'NewPass123!',
            'new_password_confirm': 'NewPass123!'
        }
        
        response = self.client.post(self.change_password_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_change_password_mismatch(self):
        """Test password change with mismatched new passwords"""
        data = {
            'old_password': 'OldPass123!',
            'new_password': 'NewPass123!',
            'new_password_confirm': 'DifferentPass123!'
        }
        
        response = self.client.post(self.change_password_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TraditionalViewsTestCase(TestCase):
    """Test cases for traditional HTML views"""
    
    def setUp(self):
        """Set up test client"""
        self.client = Client()
        
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            role='PATIENT'
        )
    
    def test_register_view_get(self):
        """Test accessing registration page"""
        response = self.client.get(reverse('accounts:register'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'register')
    
    def test_login_view_get(self):
        """Test accessing login page"""
        response = self.client.get(reverse('accounts:login'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'login')
    
    def test_login_view_post_success(self):
        """Test successful login via HTML form"""
        data = {
            'username': 'testuser',
            'password': 'TestPass123!'
        }
        
        response = self.client.post(reverse('accounts:login'), data)
        
        # Should redirect after successful login
        self.assertEqual(response.status_code, 302)
    
    def test_profile_view_authenticated(self):
        """Test accessing profile when authenticated"""
        self.client.login(username='testuser', password='TestPass123!')
        
        response = self.client.get(reverse('accounts:profile'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
    
    def test_profile_view_unauthenticated(self):
        """Test accessing profile without authentication"""
        response = self.client.get(reverse('accounts:profile'))
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_logout_view(self):
        """Test logout"""
        self.client.login(username='testuser', password='TestPass123!')
        
        response = self.client.get(reverse('accounts:logout'))
        
        # Should redirect after logout
        self.assertEqual(response.status_code, 302)
"""
accounts/models.py

Defines the core User model and role-based authentication structure.
Extends Django's AbstractUser to add role-based access control.

Architecture:
- CustomUser: Main user model with role field
- USER_ROLES: Defines the four actor types in the system
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """
    Extended user model with role-based authentication.
    
    Roles:
    - HOSPITAL: Hospital administrators who manage doctors and departments
    - DOCTOR: Medical practitioners who manage appointments and prescriptions
    - PATIENT: End users who book appointments and manage their health
    - ADMIN: System administrators with full access
    
    Fields:
    - role: User's primary role in the system (required)
    - phone: Contact number for notifications
    - is_verified: Email/phone verification status
    - created_at: Account creation timestamp
    - updated_at: Last modification timestamp
    """
    
    USER_ROLES = (
        ('HOSPITAL', 'Hospital'),
        ('DOCTOR', 'Doctor'),
        ('PATIENT', 'Patient'),
        ('ADMIN', 'Administrator'),
    )
    
    # Core fields
    role = models.CharField(
        max_length=20,
        choices=USER_ROLES,
        help_text="Primary role of the user in the system"
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Contact number for SMS notifications"
    )
    
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether email/phone has been verified"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['role', 'is_active']),
            models.Index(fields=['email']),
            models.Index(fields=['username']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_hospital(self):
        """Check if user is a hospital administrator"""
        return self.role == 'HOSPITAL'
    
    def is_doctor(self):
        """Check if user is a doctor"""
        return self.role == 'DOCTOR'
    
    def is_patient(self):
        """Check if user is a patient"""
        return self.role == 'PATIENT'
    
    def is_admin(self):
        """Check if user is a system administrator"""
        return self.role == 'ADMIN'
    
    def get_profile(self):
        """
        Retrieve the associated profile based on role.
        
        Returns:
            Profile object (HospitalProfile, DoctorProfile, or PatientProfile)
            or None if profile doesn't exist
        """
        if self.is_hospital():
            return getattr(self, 'hospital_profile', None)
        elif self.is_doctor():
            return getattr(self, 'doctor_profile', None)
        elif self.is_patient():
            return getattr(self, 'patient_profile', None)
        return None


class VerificationToken(models.Model):
    """
    Email/Phone verification tokens.
    
    Used for:
    - Email verification after registration
    - Password reset flows
    - Phone number verification
    
    Fields:
    - user: Associated user account
    - token: Unique verification token
    - token_type: Purpose of the token
    - expires_at: Token expiration timestamp
    - is_used: Whether token has been consumed
    """
    
    TOKEN_TYPES = (
        ('EMAIL', 'Email Verification'),
        ('PHONE', 'Phone Verification'),
        ('PASSWORD_RESET', 'Password Reset'),
    )
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='verification_tokens'
    )
    
    token = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique verification token"
    )
    
    token_type = models.CharField(
        max_length=20,
        choices=TOKEN_TYPES
    )
    
    expires_at = models.DateTimeField(
        help_text="Token expiration timestamp"
    )
    
    is_used = models.BooleanField(
        default=False,
        help_text="Whether this token has been consumed"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'verification_tokens'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user', 'token_type', 'is_used']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_token_type_display()}"
    
    def is_valid(self):
        """Check if token is still valid (not expired and not used)"""
        from django.utils import timezone
        return not self.is_used and self.expires_at > timezone.now()


class UserActivity(models.Model):
    """
    Audit log for user activities.
    
    Tracks important user actions for:
    - Security monitoring
    - Compliance requirements
    - System audit trails
    
    Fields:
    - user: User who performed the action
    - action: Type of activity performed
    - ip_address: Request IP address
    - user_agent: Browser/device information
    - metadata: Additional context (JSON)
    """
    
    ACTIVITY_TYPES = (
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('REGISTER', 'Registration'),
        ('PASSWORD_CHANGE', 'Password Change'),
        ('PASSWORD_RESET', 'Password Reset'),
        ('PROFILE_UPDATE', 'Profile Update'),
        ('VERIFICATION', 'Email/Phone Verification'),
    )
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='activities'
    )
    
    action = models.CharField(
        max_length=50,
        choices=ACTIVITY_TYPES
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the request"
    )
    
    user_agent = models.TextField(
        blank=True,
        help_text="Browser/device user agent string"
    )
    
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional context about the activity"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_activities'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action', '-created_at']),
        ]
        verbose_name_plural = 'User Activities'
    
    def __str__(self):
        username = self.user.username if self.user else 'Unknown'
        return f"{username} - {self.get_action_display()} at {self.created_at}"
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    USER_ROLES = (
        ('HOSPITAL', 'Hospital'),
        ('DOCTOR', 'Doctor'),
        ('PATIENT', 'Patient'),
        ('ADMIN', 'Administrator'),
    )

    role = models.CharField(max_length=20, choices=USER_ROLES, help_text="Primary role of the user in the system")
    phone = models.CharField(max_length=20, blank=True, null=True, help_text="Contact number for SMS notifications")
    is_verified = models.BooleanField(default=False, help_text="Whether email/phone has been verified")

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
        return self.role == 'HOSPITAL'

    def is_doctor(self):
        return self.role == 'DOCTOR'

    def is_patient(self):
        return self.role == 'PATIENT'

    def is_admin(self):
        return self.role == 'ADMIN'

    def get_profile(self):
        if self.is_hospital():
            return getattr(self, 'hospital_profile', None)
        elif self.is_doctor():
            return getattr(self, 'doctor_profile', None)
        elif self.is_patient():
            return getattr(self, 'patient_profile', None)
        return None

    def normalized_email(self):
        return (self.email or "").strip().lower()


class VerificationToken(models.Model):
    TOKEN_TYPES = (
        ('EMAIL', 'Email Verification'),
        ('PHONE', 'Phone Verification'),
        ('PASSWORD_RESET', 'Password Reset'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='verification_tokens')
    token = models.CharField(max_length=100, unique=True, help_text="Unique verification token")
    token_type = models.CharField(max_length=20, choices=TOKEN_TYPES)
    expires_at = models.DateTimeField(help_text="Token expiration timestamp")
    is_used = models.BooleanField(default=False, help_text="Whether this token has been consumed")
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
        from django.utils import timezone
        return not self.is_used and self.expires_at > timezone.now()


class UserActivity(models.Model):
    ACTIVITY_TYPES = (
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('REGISTER', 'Registration'),
        ('PASSWORD_CHANGE', 'Password Change'),
        ('PASSWORD_RESET', 'Password Reset'),
        ('PROFILE_UPDATE', 'Profile Update'),
        ('VERIFICATION', 'Email/Phone Verification'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='activities')
    action = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="IP address of the request")

    # Safe defaults prevent IntegrityError
    user_agent = models.TextField(null=True, blank=True, default="unknown", help_text="Browser/device user agent string")

    metadata = models.JSONField(default=dict, blank=True, help_text="Additional context about the activity")
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


# Profiles needed across apps
class DoctorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='accounts_doctor_profile')
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50)

    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"


class PatientProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='accounts_patient_profile')
    date_of_birth = models.DateField()
    medical_history = models.TextField(blank=True)

    def __str__(self):
        return self.user.get_full_name()


class HospitalProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='accounts_hospital_profile')
    hospital_name = models.CharField(max_length=150)
    license_number = models.CharField(max_length=50)
    address = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.hospital_name


class AdminProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='accounts_admin_profile')
    full_name = models.CharField(max_length=100)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    permissions = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.full_name


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

from django.db import models
from django.contrib.auth.models import AbstractUser

# -------------------------------------------------------------------
# Custom user model
# -------------------------------------------------------------------
# We extend Django's AbstractUser so we can add extra fields
# (phone, role, is_verified, timestamps). This replaces the default
# User model, so we must tell Django about it in settings.py.
# -------------------------------------------------------------------
class CustomUser(AbstractUser):
    USER_ROLES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin', 'Admin'),
    )

    phone = models.CharField(max_length=20, blank=True, null=True)  # optional phone number
    role = models.CharField(max_length=20, choices=USER_ROLES)    # role of the user
    is_verified = models.BooleanField(default=False)                # email/phone verification flag

    created_at = models.DateTimeField(auto_now_add=True)            # auto set on creation
    updated_at = models.DateTimeField(auto_now=True)                # auto update on save

    def __str__(self):
        return self.username


# -------------------------------------------------------------------
# VerificationToken model
# -------------------------------------------------------------------
# Used for email/phone verification flows. Each token belongs to a user.
# -------------------------------------------------------------------
class VerificationToken(models.Model):
    TOKEN_TYPES = (
        ('email', 'Email'),
        ('phone', 'Phone'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token_type = models.CharField(max_length=20, choices=TOKEN_TYPES)
    token = models.CharField(max_length=255)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.token_type}"


# -------------------------------------------------------------------
# UserActivity model
# -------------------------------------------------------------------
# Keeps a log of user actions (login, logout, profile update, etc.)
# Useful for audit trails and activity history.
# -------------------------------------------------------------------
class UserActivity(models.Model):
    ACTION_CHOICES = (
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('update_profile', 'Update Profile'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)  # flexible extra info
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action}"

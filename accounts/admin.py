# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser,
    VerificationToken,
    UserActivity,
    DoctorProfile,
    PatientProfile
)

# -------------------------------
# Admin registration for CustomUser
# -------------------------------
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Admin panel configuration for CustomUser.
    Extends Django's built-in UserAdmin to support role-based access.
    """
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_verified', 'is_staff', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('role', 'is_verified', 'is_staff', 'is_active', 'date_joined')
    ordering = ('-created_at',)

# -------------------------------
# Admin registration for VerificationToken
# -------------------------------
@admin.register(VerificationToken)
class VerificationTokenAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for VerificationToken.
    Tracks email/phone/password reset tokens for users.
    """
    list_display = ('user', 'token', 'token_type', 'is_used', 'expires_at', 'created_at')
    search_fields = ('user__username', 'token')
    list_filter = ('token_type', 'is_used', 'expires_at', 'created_at')

# -------------------------------
# Admin registration for UserActivity
# -------------------------------
@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for UserActivity.
    Displays audit logs of user actions for security and compliance.
    """
    list_display = ('user', 'action', 'ip_address', 'created_at')
    search_fields = ('user__username', 'action', 'ip_address')
    list_filter = ('action', 'created_at')

# -------------------------------
# Admin registration for DoctorProfile
# -------------------------------
@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for DoctorProfile.
    Displays doctor-specific data linked to CustomUser.
    """
    list_display = ('user', 'specialization', 'license_number')
    search_fields = ('user__username', 'specialization', 'license_number')
    list_filter = ('specialization',)

# -------------------------------
# Admin registration for PatientProfile
# -------------------------------
@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    """
    Admin panel configuration for PatientProfile.
    Displays patient-specific data linked to CustomUser.
    """
    list_display = ('user', 'date_of_birth')
    search_fields = ('user__username',)
    list_filter = ('date_of_birth',)

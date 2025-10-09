"""
accounts/services.py

Business logic layer for accounts operations.
Contains all account-related business rules and orchestration.
"""

import secrets
from django.utils import timezone
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from datetime import timedelta
from typing import Optional, Dict, Tuple
from .models import CustomUser, VerificationToken
from .repositories import UserRepository, VerificationTokenRepository, UserActivityRepository


class UserService:
    """
    Service for user account management.
    Handles registration, authentication, and profile operations.
    """
    
    @staticmethod
    @transaction.atomic
    def register_user(username: str, email: str, password: str, role: str, **extra_fields) -> Tuple[CustomUser, str]:
        """
        Register a new user and send verification email.
        
        Args:
            username: Unique username
            email: User's email address
            password: Plain text password
            role: User role (HOSPITAL, DOCTOR, PATIENT, ADMIN)
            **extra_fields: Additional fields (first_name, last_name, phone)
        
        Returns:
            Tuple of (user, verification_token)
        
        Raises:
            ValueError: If username or email already exists
        """
        # Validate uniqueness
        if UserRepository.username_exists(username):
            raise ValueError("Username already exists")
        
        if UserRepository.email_exists(email):
            raise ValueError("Email already exists")
        
        # Create user
        user = UserRepository.create_user(
            username=username,
            email=email,
            password=password,
            role=role,
            **extra_fields
        )
        
        # Generate verification token
        token = VerificationService.create_email_verification_token(user)
        
        # Log activity
        UserActivityRepository.log_activity(
            user=user,
            action='REGISTER',
            metadata={'role': role}
        )
        
        # Send verification email (async in production)
        NotificationService.send_verification_email(user, token)
        
        return user, token
    
    @staticmethod
    def authenticate_user(username_or_email: str, password: str, 
                         ip_address: str = None, user_agent: str = None) -> Optional[CustomUser]:
        """
        Authenticate user with username/email and password.
        
        Args:
            username_or_email: Username or email
            password: Plain text password
            ip_address: Request IP address
            user_agent: Browser user agent
        
        Returns:
            Authenticated user or None if authentication fails
        """
        # Get user by username or email
        user = UserRepository.get_by_username_or_email(username_or_email)
        
        if not user:
            # Log failed attempt (user not found)
            return None
        
        # Check rate limiting (prevent brute force)
        failed_attempts = UserActivityRepository.get_failed_login_attempts(user, minutes=30)
        if failed_attempts >= 5:
            raise ValueError("Too many failed login attempts. Please try again later.")
        
        # Authenticate
        authenticated_user = authenticate(username=user.username, password=password)
        
        # Log activity
        success = authenticated_user is not None
        UserActivityRepository.log_activity(
            user=user,
            action='LOGIN',
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={'success': success}
        )
        
        return authenticated_user
    
    @staticmethod
    def update_profile(user: CustomUser, **fields) -> CustomUser:
        """
        Update user profile information.
        
        Args:
            user: User to update
            **fields: Fields to update (first_name, last_name, email, phone)
        
        Returns:
            Updated user
        
        Raises:
            ValueError: If email already exists
        """
        # Check email uniqueness if being updated
        new_email = fields.get('email')
        if new_email and new_email != user.email:
            if UserRepository.email_exists(new_email):
                raise ValueError("Email already in use")
        
        # Update user
        updated_user = UserRepository.update_user(user, **fields)
        
        # Log activity
        UserActivityRepository.log_activity(
            user=user,
            action='PROFILE_UPDATE',
            metadata={'updated_fields': list(fields.keys())}
        )
        
        return updated_user
    
    @staticmethod
    def change_password(user: CustomUser, old_password: str, new_password: str) -> bool:
        """
        Change user password with verification.
        
        Args:
            user: User changing password
            old_password: Current password for verification
            new_password: New password to set
        
        Returns:
            True if password changed successfully
        
        Raises:
            ValueError: If old password is incorrect
        """
        # Verify old password
        if not user.check_password(old_password):
            raise ValueError("Current password is incorrect")
        
        # Set new password
        user.set_password(new_password)
        user.save()
        
        # Log activity
        UserActivityRepository.log_activity(
            user=user,
            action='PASSWORD_CHANGE'
        )
        
        return True
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[CustomUser]:
        """Get user by ID"""
        return UserRepository.get_by_id(user_id)
    
    @staticmethod
    def get_users_by_role(role: str) -> list:
        """Get all users with specific role"""
        return UserRepository.get_users_by_role(role)
    
    @staticmethod
    def deactivate_account(user: CustomUser) -> CustomUser:
        """
        Deactivate user account.
        
        Args:
            user: User to deactivate
        
        Returns:
            Deactivated user
        """
        deactivated_user = UserRepository.deactivate_user(user)
        
        # Log activity
        UserActivityRepository.log_activity(
            user=user,
            action='PROFILE_UPDATE',
            metadata={'deactivated': True}
        )
        
        return deactivated_user


class VerificationService:
    """
    Service for email/phone verification and password reset.
    """
    
    @staticmethod
    def create_email_verification_token(user: CustomUser) -> str:
        """
        Create an email verification token.
        
        Args:
            user: User to create token for
        
        Returns:
            Token string
        """
        # Generate secure token
        token = secrets.token_urlsafe(32)
        
        # Set expiration (24 hours)
        expires_at = timezone.now() + timedelta(hours=24)
        
        # Create token record
        VerificationTokenRepository.create_token(
            user=user,
            token=token,
            token_type='EMAIL',
            expires_at=expires_at
        )
        
        return token
    
    @staticmethod
    @transaction.atomic
    def verify_email(token: str) -> Optional[CustomUser]:
        """
        Verify user email with token.
        
        Args:
            token: Verification token
        
        Returns:
            Verified user or None if token invalid
        """
        # Get valid token
        token_obj = VerificationTokenRepository.get_valid_token(token, 'EMAIL')
        
        if not token_obj:
            return None
        
        # Mark user as verified
        user = UserRepository.mark_as_verified(token_obj.user)
        
        # Mark token as used
        VerificationTokenRepository.mark_as_used(token_obj)
        
        # Log activity
        UserActivityRepository.log_activity(
            user=user,
            action='VERIFICATION',
            metadata={'type': 'email'}
        )
        
        return user
    
    @staticmethod
    def create_phone_verification_token(user: CustomUser) -> str:
        """
        Create a phone verification token.
        
        Args:
            user: User to create token for
        
        Returns:
            6-digit verification code
        """
        # Generate 6-digit code
        token = str(secrets.randbelow(1000000)).zfill(6)
        
        # Set expiration (10 minutes)
        expires_at = timezone.now() + timedelta(minutes=10)
        
        # Create token record
        VerificationTokenRepository.create_token(
            user=user,
            token=token,
            token_type='PHONE',
            expires_at=expires_at
        )
        
        return token
    
    @staticmethod
    @transaction.atomic
    def verify_phone(token: str) -> Optional[CustomUser]:
        """
        Verify user phone with token.
        
        Args:
            token: Verification code
        
        Returns:
            Verified user or None if code invalid
        """
        # Get valid token
        token_obj = VerificationTokenRepository.get_valid_token(token, 'PHONE')
        
        if not token_obj:
            return None
        
        # Mark user as verified
        user = UserRepository.mark_as_verified(token_obj.user)
        
        # Mark token as used
        VerificationTokenRepository.mark_as_used(token_obj)
        
        # Log activity
        UserActivityRepository.log_activity(
            user=user,
            action='VERIFICATION',
            metadata={'type': 'phone'}
        )
        
        return user
    
    @staticmethod
    def create_password_reset_token(email: str) -> Optional[str]:
        """
        Create password reset token for email.
        
        Args:
            email: User's email address
        
        Returns:
            Token string or None if user not found
        """
        user = UserRepository.get_by_email(email)
        
        if not user:
            # Don't reveal if email exists for security
            return None
        
        # Delete old password reset tokens
        VerificationTokenRepository.delete_user_tokens(user, 'PASSWORD_RESET')
        
        # Generate secure token
        token = secrets.token_urlsafe(32)
        
        # Set expiration (1 hour)
        expires_at = timezone.now() + timedelta(hours=1)
        
        # Create token record
        VerificationTokenRepository.create_token(
            user=user,
            token=token,
            token_type='PASSWORD_RESET',
            expires_at=expires_at
        )
        
        # Send reset email
        NotificationService.send_password_reset_email(user, token)
        
        return token
    
    @staticmethod
    @transaction.atomic
    def reset_password(token: str, new_password: str) -> Optional[CustomUser]:
        """
        Reset user password with token.
        
        Args:
            token: Password reset token
            new_password: New password to set
        
        Returns:
            User with reset password or None if token invalid
        """
        # Get valid token
        token_obj = VerificationTokenRepository.get_valid_token(token, 'PASSWORD_RESET')
        
        if not token_obj:
            return None
        
        # Set new password
        user = token_obj.user
        user.set_password(new_password)
        user.save()
        
        # Mark token as used
        VerificationTokenRepository.mark_as_used(token_obj)
        
        # Log activity
        UserActivityRepository.log_activity(
            user=user,
            action='PASSWORD_RESET'
        )
        
        return user


class NotificationService:
    """
    Service for sending notifications (email, SMS).
    In production, this should use Celery tasks for async processing.
    """
    
    @staticmethod
    def send_verification_email(user: CustomUser, token: str):
        """Send email verification link"""
        verification_url = f"{settings.FRONTEND_URL}/verify-email/{token}"
        
        subject = "Verify your MedApp account"
        message = f"""
        Hello {user.first_name},
        
        Thank you for registering with MedApp!
        
        Please verify your email address by clicking the link below:
        {verification_url}
        
        This link will expire in 24 hours.
        
        If you did not create this account, please ignore this email.
        
        Best regards,
        MedApp Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )
    
    @staticmethod
    def send_password_reset_email(user: CustomUser, token: str):
        """Send password reset link"""
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{token}"
        
        subject = "Reset your MedApp password"
        message = f"""
        Hello {user.first_name},
        
        We received a request to reset your MedApp password.
        
        Click the link below to reset your password:
        {reset_url}
        
        This link will expire in 1 hour.
        
        If you did not request a password reset, please ignore this email.
        
        Best regards,
        MedApp Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False
        )
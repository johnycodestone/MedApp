"""
accounts/repositories.py

Data access layer for user-related database operations.
Encapsulates all ORM queries in a single place for better maintainability.
"""

from django.db.models import Q, Count, Prefetch
from django.utils import timezone
from datetime import timedelta
from typing import Optional, List
from .models import CustomUser, VerificationToken, UserActivity


class UserRepository:
    """
    Repository for CustomUser model operations.
    Handles all database queries related to users.
    """
    
    @staticmethod
    def create_user(username: str, email: str, password: str, role: str, **extra_fields) -> CustomUser:
        """
        Create a new user with the given credentials.
        
        Args:
            username: Unique username
            email: User's email address
            password: Plain text password (will be hashed)
            role: User's role (HOSPITAL, DOCTOR, PATIENT, ADMIN)
            **extra_fields: Additional fields (first_name, last_name, phone, etc.)
        
        Returns:
            Created CustomUser instance
        """
        user = CustomUser.objects.create_user(
            username=username,
            email=email.lower(),
            password=password,
            role=role,
            **extra_fields
        )
        return user
    
    @staticmethod
    def get_by_id(user_id: int) -> Optional[CustomUser]:
        """Get user by ID"""
        try:
            return CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_username(username: str) -> Optional[CustomUser]:
        """Get user by username"""
        try:
            return CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_email(email: str) -> Optional[CustomUser]:
        """Get user by email"""
        try:
            return CustomUser.objects.get(email=email.lower())
        except CustomUser.DoesNotExist:
            return None
    
    @staticmethod
    def get_by_username_or_email(identifier: str) -> Optional[CustomUser]:
        """
        Get user by username or email.
        Useful for login where user can enter either.
        """
        try:
            return CustomUser.objects.get(
                Q(username=identifier) | Q(email=identifier.lower())
            )
        except CustomUser.DoesNotExist:
            return None
    
    @staticmethod
    def email_exists(email: str) -> bool:
        """Check if email already exists"""
        return CustomUser.objects.filter(email=email.lower()).exists()
    
    @staticmethod
    def username_exists(username: str) -> bool:
        """Check if username already exists"""
        return CustomUser.objects.filter(username=username).exists()
    
    @staticmethod
    def get_users_by_role(role: str, is_active: bool = True) -> List[CustomUser]:
        """
        Get all users with a specific role.
        
        Args:
            role: User role to filter by
            is_active: Filter by active status (default: True)
        
        Returns:
            List of CustomUser instances
        """
        return CustomUser.objects.filter(role=role, is_active=is_active)
    
    @staticmethod
    def get_verified_users() -> List[CustomUser]:
        """Get all verified users"""
        return CustomUser.objects.filter(is_verified=True, is_active=True)
    
    @staticmethod
    def get_unverified_users() -> List[CustomUser]:
        """Get all unverified users"""
        return CustomUser.objects.filter(is_verified=False, is_active=True)
    
    @staticmethod
    def update_user(user: CustomUser, **fields) -> CustomUser:
        """
        Update user fields.
        
        Args:
            user: User instance to update
            **fields: Fields to update
        
        Returns:
            Updated user instance
        """
        for field, value in fields.items():
            if field == 'email' and value:
                value = value.lower()
            setattr(user, field, value)
        user.save()
        return user
    
    @staticmethod
    def mark_as_verified(user: CustomUser) -> CustomUser:
        """Mark user as verified"""
        user.is_verified = True
        user.save()
        return user
    
    @staticmethod
    def deactivate_user(user: CustomUser) -> CustomUser:
        """Deactivate user account"""
        user.is_active = False
        user.save()
        return user
    
    @staticmethod
    def activate_user(user: CustomUser) -> CustomUser:
        """Activate user account"""
        user.is_active = True
        user.save()
        return user
    
    @staticmethod
    def get_recent_users(days: int = 7) -> List[CustomUser]:
        """
        Get users registered in the last N days.
        
        Args:
            days: Number of days to look back (default: 7)
        
        Returns:
            List of recently registered users
        """
        since = timezone.now() - timedelta(days=days)
        return CustomUser.objects.filter(created_at__gte=since).order_by('-created_at')
    
    @staticmethod
    def get_user_count_by_role() -> dict:
        """
        Get count of users grouped by role.
        
        Returns:
            Dictionary with role counts
        """
        result = CustomUser.objects.values('role').annotate(count=Count('id'))
        return {item['role']: item['count'] for item in result}


class VerificationTokenRepository:
    """
    Repository for VerificationToken model operations.
    Handles token creation, validation, and cleanup.
    """
    
    @staticmethod
    def create_token(user: CustomUser, token: str, token_type: str, expires_at) -> VerificationToken:
        """
        Create a new verification token.
        
        Args:
            user: User the token is for
            token: Unique token string
            token_type: Type of token (EMAIL, PHONE, PASSWORD_RESET)
            expires_at: Token expiration datetime
        
        Returns:
            Created VerificationToken instance
        """
        return VerificationToken.objects.create(
            user=user,
            token=token,
            token_type=token_type,
            expires_at=expires_at
        )
    
    @staticmethod
    def get_by_token(token: str) -> Optional[VerificationToken]:
        """Get verification token by token string"""
        try:
            return VerificationToken.objects.select_related('user').get(token=token)
        except VerificationToken.DoesNotExist:
            return None
    
    @staticmethod
    def get_valid_token(token: str, token_type: str) -> Optional[VerificationToken]:
        """
        Get a valid (not expired, not used) token.
        
        Args:
            token: Token string
            token_type: Expected token type
        
        Returns:
            VerificationToken if valid, None otherwise
        """
        try:
            token_obj = VerificationToken.objects.select_related('user').get(
                token=token,
                token_type=token_type,
                is_used=False,
                expires_at__gt=timezone.now()
            )
            return token_obj
        except VerificationToken.DoesNotExist:
            return None
    
    @staticmethod
    def mark_as_used(token: VerificationToken) -> VerificationToken:
        """Mark token as used"""
        token.is_used = True
        token.save()
        return token
    
    @staticmethod
    def get_user_tokens(user: CustomUser, token_type: str = None) -> List[VerificationToken]:
        """
        Get all tokens for a user, optionally filtered by type.
        
        Args:
            user: User to get tokens for
            token_type: Optional token type filter
        
        Returns:
            List of VerificationToken instances
        """
        queryset = VerificationToken.objects.filter(user=user)
        if token_type:
            queryset = queryset.filter(token_type=token_type)
        return queryset.order_by('-created_at')
    
    @staticmethod
    def delete_expired_tokens():
        """Delete all expired tokens (cleanup task)"""
        expired_count = VerificationToken.objects.filter(
            expires_at__lt=timezone.now()
        ).delete()[0]
        return expired_count
    
    @staticmethod
    def delete_user_tokens(user: CustomUser, token_type: str = None):
        """
        Delete all tokens for a user.
        
        Args:
            user: User whose tokens to delete
            token_type: Optional token type filter
        """
        queryset = VerificationToken.objects.filter(user=user)
        if token_type:
            queryset = queryset.filter(token_type=token_type)
        return queryset.delete()[0]


class UserActivityRepository:
    """
    Repository for UserActivity model operations.
    Handles activity logging and audit trail queries.
    """
    
    @staticmethod
    def log_activity(user: CustomUser, action: str, ip_address: str = None, 
                     user_agent: str = None, metadata: dict = None) -> UserActivity:
        """
        Log a user activity.
        
        Args:
            user: User who performed the action
            action: Type of activity
            ip_address: IP address of the request
            user_agent: Browser/device user agent
            metadata: Additional context data
        
        Returns:
            Created UserActivity instance
        """
        return UserActivity.objects.create(
            user=user,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata or {}
        )
    
    @staticmethod
    def get_user_activities(user: CustomUser, limit: int = 50) -> List[UserActivity]:
        """
        Get recent activities for a user.
        
        Args:
            user: User to get activities for
            limit: Maximum number of activities to return
        
        Returns:
            List of UserActivity instances
        """
        return UserActivity.objects.filter(user=user).order_by('-created_at')[:limit]
    
    @staticmethod
    def get_activities_by_action(action: str, limit: int = 100) -> List[UserActivity]:
        """
        Get recent activities of a specific type.
        
        Args:
            action: Activity type to filter by
            limit: Maximum number of activities to return
        
        Returns:
            List of UserActivity instances
        """
        return UserActivity.objects.filter(action=action).order_by('-created_at')[:limit]
    
    @staticmethod
    def get_recent_logins(days: int = 7) -> List[UserActivity]:
        """
        Get all login activities in the last N days.
        
        Args:
            days: Number of days to look back
        
        Returns:
            List of login activities
        """
        since = timezone.now() - timedelta(days=days)
        return UserActivity.objects.filter(
            action='LOGIN',
            created_at__gte=since
        ).select_related('user').order_by('-created_at')
    
    @staticmethod
    def get_failed_login_attempts(user: CustomUser, minutes: int = 30) -> int:
        """
        Count failed login attempts for a user in the last N minutes.
        Useful for rate limiting.
        
        Args:
            user: User to check
            minutes: Time window in minutes
        
        Returns:
            Count of failed login attempts
        """
        since = timezone.now() - timedelta(minutes=minutes)
        return UserActivity.objects.filter(
            user=user,
            action='LOGIN',
            metadata__success=False,
            created_at__gte=since
        ).count()
    
    @staticmethod
    def cleanup_old_activities(days: int = 90):
        """
        Delete activity logs older than N days.
        
        Args:
            days: Age threshold in days
        
        Returns:
            Number of deleted records
        """
        cutoff = timezone.now() - timedelta(days=days)
        return UserActivity.objects.filter(created_at__lt=cutoff).delete()[0]
    
    @staticmethod
    def get_activity_count_by_action() -> dict:
        """
        Get activity counts grouped by action type.
        
        Returns:
            Dictionary with action counts
        """
        result = UserActivity.objects.values('action').annotate(count=Count('id'))
        return {item['action']: item['count'] for item in result}
"""
accounts/serializers.py

DRF serializers for user registration, authentication, and profile management.
Handles validation and data transformation for API endpoints.
"""

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import CustomUser, VerificationToken, UserActivity


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    
    Validates:
    - Password strength and confirmation
    - Email uniqueness
    - Username uniqueness
    - Required fields based on role
    """
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone', 'role'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'role': {'required': True}
        }
    
    def validate_email(self, value):
        """Ensure email is unique"""
        if CustomUser.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value.lower()
    
    def validate_username(self, value):
        """Ensure username is unique"""
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value
    
    def validate(self, attrs):
        """Validate password match and strength"""
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm', None)
        
        # Check password match
        if password != password_confirm:
            raise serializers.ValidationError({
                'password_confirm': "Passwords do not match."
            })
        
        # Validate password strength
        try:
            validate_password(password)
        except DjangoValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        
        return attrs
    
    def create(self, validated_data):
        """Create user with hashed password"""
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone=validated_data.get('phone', ''),
            role=validated_data['role']
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    
    Accepts either username or email for authentication.
    """
    
    username_or_email = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Validate credentials without authenticating yet (done in view)"""
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """
    Standard user serializer for displaying user information.
    Used in API responses and user profile views.
    """
    
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone', 'role', 'role_display', 'is_verified',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_verified']


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile information.
    Excludes sensitive fields like password and role.
    """
    
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 'phone'
        ]
    
    def validate_email(self, value):
        """Ensure email is unique (excluding current user)"""
        user = self.instance
        if CustomUser.objects.filter(email=value.lower()).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value.lower()


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for changing user password.
    Requires current password for security.
    """
    
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate_old_password(self, value):
        """Verify old password is correct"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value
    
    def validate(self, attrs):
        """Validate new password match and strength"""
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')
        
        if new_password != new_password_confirm:
            raise serializers.ValidationError({
                'new_password_confirm': "New passwords do not match."
            })
        
        # Validate password strength
        try:
            validate_password(new_password, user=self.context['request'].user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({'new_password': list(e.messages)})
        
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for requesting password reset.
    Accepts email to send reset link.
    """
    
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Check if email exists in system"""
        if not CustomUser.objects.filter(email=value.lower()).exists():
            # For security, don't reveal if email exists
            # But we still validate format
            pass
        return value.lower()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for confirming password reset with token.
    """
    
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Validate password match and strength"""
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')
        
        if new_password != new_password_confirm:
            raise serializers.ValidationError({
                'new_password_confirm': "Passwords do not match."
            })
        
        # Validate password strength
        try:
            validate_password(new_password)
        except DjangoValidationError as e:
            raise serializers.ValidationError({'new_password': list(e.messages)})
        
        return attrs


class VerificationTokenSerializer(serializers.ModelSerializer):
    """
    Serializer for verification tokens.
    Used in email/phone verification flows.
    """
    
    class Meta:
        model = VerificationToken
        fields = ['id', 'token_type', 'expires_at', 'is_used', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserActivitySerializer(serializers.ModelSerializer):
    """
    Serializer for user activity logs.
    Used in audit trails and activity history.
    """
    
    user_username = serializers.CharField(source='user.username', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = UserActivity
        fields = [
            'id', 'user', 'user_username', 'action', 'action_display',
            'ip_address', 'user_agent', 'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class EmailVerificationSerializer(serializers.Serializer):
    """
    Serializer for email verification.
    """
    
    token = serializers.CharField(required=True)


class PhoneVerificationSerializer(serializers.Serializer):
    """
    Serializer for phone verification.
    """
    
    token = serializers.CharField(required=True)
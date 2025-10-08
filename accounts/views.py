"""
accounts/views.py

HTTP request handlers for accounts operations.
Keeps views thin - delegates to services for business logic.
"""

from rest_framework import status, generics, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.views.generic import FormView
from django.urls import reverse_lazy

from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    UserUpdateSerializer, PasswordChangeSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer, EmailVerificationSerializer, UserActivitySerializer
)
from .forms import (
    CustomUserRegistrationForm, CustomAuthenticationForm,
    UserProfileUpdateForm, PasswordChangeForm as DjangoPasswordChangeForm,
    PasswordResetRequestForm, PasswordResetConfirmForm
)
from .services import UserService, VerificationService
from .repositories import UserActivityRepository
from .permissions import IsOwnerOrAdmin


# ============================================
# REST API Views (DRF)
# ============================================

class UserRegistrationAPIView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    
    POST /api/accounts/register/
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        """Handle user registration"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Register user via service
            user, token = UserService.register_user(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
                role=serializer.validated_data['role'],
                first_name=serializer.validated_data.get('first_name', ''),
                last_name=serializer.validated_data.get('last_name', ''),
                phone=serializer.validated_data.get('phone', '')
            )
            
            return Response({
                'message': 'Registration successful. Please check your email to verify your account.',
                'user': UserSerializer(user).data,
                'verification_token': token
            }, status=status.HTTP_201_CREATED)
        
        except ValueError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class UserLoginAPIView(views.APIView):
    """
    API endpoint for user login.
    
    POST /api/accounts/login/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Handle user login and return JWT tokens"""
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Authenticate user
            user = UserService.authenticate_user(
                username_or_email=serializer.validated_data['username_or_email'],
                password=serializer.validated_data['password'],
                ip_address=self.get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
            
            if not user:
                return Response({
                    'error': 'Invalid credentials'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            if not user.is_active:
                return Response({
                    'error': 'Account is deactivated'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Login successful',
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token)
                }
            }, status=status.HTTP_200_OK)
        
        except ValueError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class UserLogoutAPIView(views.APIView):
    """
    API endpoint for user logout.
    
    POST /api/accounts/logout/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Handle user logout"""
        # Log activity
        UserActivityRepository.log_activity(
            user=request.user,
            action='LOGOUT'
        )
        
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)


class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for viewing and updating user profile.
    
    GET /api/accounts/profile/
    PUT /api/accounts/profile/
    PATCH /api/accounts/profile/
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Return current user"""
        return self.request.user
    
    def get_serializer_class(self):
        """Use different serializer for updates"""
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return UserSerializer
    
    def update(self, request, *args, **kwargs):
        """Handle profile update"""
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Update via service
            updated_user = UserService.update_profile(
                user=request.user,
                **serializer.validated_data
            )
            
            return Response({
                'message': 'Profile updated successfully',
                'user': UserSerializer(updated_user).data
            }, status=status.HTTP_200_OK)
        
        except ValueError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeAPIView(views.APIView):
    """
    API endpoint for changing password.
    
    POST /api/accounts/change-password/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Handle password change"""
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        try:
            UserService.change_password(
                user=request.user,
                old_password=serializer.validated_data['old_password'],
                new_password=serializer.validated_data['new_password']
            )
            
            return Response({
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)
        
        except ValueError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestAPIView(views.APIView):
    """
    API endpoint for requesting password reset.
    
    POST /api/accounts/password-reset/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Handle password reset request"""
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Always return success (don't reveal if email exists)
        VerificationService.create_password_reset_token(
            email=serializer.validated_data['email']
        )
        
        return Response({
            'message': 'If an account exists with this email, a password reset link has been sent.'
        }, status=status.HTTP_200_OK)


class PasswordResetConfirmAPIView(views.APIView):
    """
    API endpoint for confirming password reset.
    
    POST /api/accounts/password-reset/confirm/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Handle password reset confirmation"""
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = VerificationService.reset_password(
            token=serializer.validated_data['token'],
            new_password=serializer.validated_data['new_password']
        )
        
        if not user:
            return Response({
                'error': 'Invalid or expired token'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'message': 'Password reset successful'
        }, status=status.HTTP_200_OK)


class EmailVerificationAPIView(views.APIView):
    """
    API endpoint for verifying email.
    
    POST /api/accounts/verify-email/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Handle email verification"""
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = VerificationService.verify_email(
            token=serializer.validated_data['token']
        )
        
        if not user:
            return Response({
                'error': 'Invalid or expired verification token'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'message': 'Email verified successfully',
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)


class UserActivityListAPIView(generics.ListAPIView):
    """
    API endpoint for listing user activities.
    
    GET /api/accounts/activities/
    """
    serializer_class = UserActivitySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return activities for current user"""
        return UserActivityRepository.get_user_activities(
            user=self.request.user,
            limit=50
        )


# ============================================
# Traditional Django Views (HTML Templates)
# ============================================

class RegisterView(FormView):
    """
    Traditional registration view with HTML form.
    
    GET/POST /accounts/register/
    """
    template_name = 'accounts/register.html'
    form_class = CustomUserRegistrationForm
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        """Handle successful registration"""
        try:
            user, token = UserService.register_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                role=form.cleaned_data['role'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                phone=form.cleaned_data.get('phone', '')
            )
            
            messages.success(
                self.request,
                'Registration successful! Please check your email to verify your account.'
            )
            return super().form_valid(form)
        
        except ValueError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)


class LoginView(FormView):
    """
    Traditional login view with HTML form.
    
    GET/POST /accounts/login/
    """
    template_name = 'accounts/login.html'
    form_class = CustomAuthenticationForm
    success_url = reverse_lazy('accounts:dashboard')
    
    def form_valid(self, form):
        """Handle successful login"""
        try:
            user = UserService.authenticate_user(
                username_or_email=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                ip_address=self.get_client_ip(),
                user_agent=self.request.META.get('HTTP_USER_AGENT', '')
            )
            
            if not user:
                messages.error(self.request, 'Invalid credentials')
                return self.form_invalid(form)
            
            if not user.is_active:
                messages.error(self.request, 'Account is deactivated')
                return self.form_invalid(form)
            
            # Login user (create session)
            login(self.request, user)
            messages.success(self.request, f'Welcome back, {user.first_name}!')
            
            # Redirect based on role
            if user.is_hospital():
                return redirect('hospitals:dashboard')
            elif user.is_doctor():
                return redirect('doctors:dashboard')
            elif user.is_patient():
                return redirect('patients:dashboard')
            elif user.is_admin():
                return redirect('adminpanel:dashboard')
            
            return super().form_valid(form)
        
        except ValueError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
    
    def get_client_ip(self):
        """Extract client IP address from request"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class LogoutView(View):
    """
    Traditional logout view.
    
    GET/POST /accounts/logout/
    """
    
    def get(self, request):
        """Handle logout"""
        if request.user.is_authenticated:
            UserActivityRepository.log_activity(
                user=request.user,
                action='LOGOUT'
            )
            logout(request)
            messages.success(request, 'You have been logged out successfully.')
        
        return redirect('accounts:login')
    
    def post(self, request):
        """Handle logout (POST)"""
        return self.get(request)


class ProfileView(View):
    """
    Traditional profile view with HTML template.
    
    GET /accounts/profile/
    """
    template_name = 'accounts/profile.html'
    
    def get(self, request):
        """Display user profile"""
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        
        # Get recent activities
        activities = UserActivityRepository.get_user_activities(request.user, limit=10)
        
        context = {
            'user': request.user,
            'activities': activities
        }
        return render(request, self.template_name, context)


class ProfileUpdateView(FormView):
    """
    Traditional profile update view.
    
    GET/POST /accounts/profile/edit/
    """
    template_name = 'accounts/profile_edit.html'
    form_class = UserProfileUpdateForm
    success_url = reverse_lazy('accounts:profile')
    
    def dispatch(self, request, *args, **kwargs):
        """Ensure user is authenticated"""
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        """Pass current user instance to form"""
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        """Handle profile update"""
        try:
            UserService.update_profile(
                user=self.request.user,
                **form.cleaned_data
            )
            messages.success(self.request, 'Profile updated successfully!')
            return super().form_valid(form)
        
        except ValueError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)


class PasswordChangeView(FormView):
    """
    Traditional password change view.
    
    GET/POST /accounts/password/change/
    """
    template_name = 'accounts/password_change.html'
    form_class = DjangoPasswordChangeForm
    success_url = reverse_lazy('accounts:profile')
    
    def dispatch(self, request, *args, **kwargs):
        """Ensure user is authenticated"""
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        """Pass current user to form"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        """Handle password change"""
        try:
            UserService.change_password(
                user=self.request.user,
                old_password=form.cleaned_data['old_password'],
                new_password=form.cleaned_data['new_password1']
            )
            messages.success(self.request, 'Password changed successfully!')
            return super().form_valid(form)
        
        except ValueError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)


class PasswordResetRequestView(FormView):
    """
    Traditional password reset request view.
    
    GET/POST /accounts/password/reset/
    """
    template_name = 'accounts/password_reset.html'
    form_class = PasswordResetRequestForm
    success_url = reverse_lazy('accounts:password_reset_done')
    
    def form_valid(self, form):
        """Handle password reset request"""
        VerificationService.create_password_reset_token(
            email=form.cleaned_data['email']
        )
        return super().form_valid(form)


class PasswordResetDoneView(View):
    """
    View shown after password reset request.
    
    GET /accounts/password/reset/done/
    """
    template_name = 'accounts/password_reset_done.html'
    
    def get(self, request):
        """Display confirmation message"""
        return render(request, self.template_name)


class PasswordResetConfirmView(FormView):
    """
    Traditional password reset confirmation view.
    
    GET/POST /accounts/password/reset/confirm/<token>/
    """
    template_name = 'accounts/password_reset_confirm.html'
    form_class = PasswordResetConfirmForm
    success_url = reverse_lazy('accounts:password_reset_complete')
    
    def get_context_data(self, **kwargs):
        """Add token to context"""
        context = super().get_context_data(**kwargs)
        context['token'] = self.kwargs.get('token')
        return context
    
    def form_valid(self, form):
        """Handle password reset confirmation"""
        token = self.kwargs.get('token')
        
        user = VerificationService.reset_password(
            token=token,
            new_password=form.cleaned_data['new_password1']
        )
        
        if not user:
            messages.error(self.request, 'Invalid or expired reset link.')
            return self.form_invalid(form)
        
        messages.success(self.request, 'Password reset successful! You can now log in.')
        return super().form_valid(form)


class PasswordResetCompleteView(View):
    """
    View shown after successful password reset.
    
    GET /accounts/password/reset/complete/
    """
    template_name = 'accounts/password_reset_complete.html'
    
    def get(self, request):
        """Display success message"""
        return render(request, self.template_name)


class EmailVerificationView(View):
    """
    Email verification view.
    
    GET /accounts/verify-email/<token>/
    """
    template_name = 'accounts/email_verification.html'
    
    def get(self, request, token):
        """Handle email verification"""
        user = VerificationService.verify_email(token)
        
        if user:
            messages.success(request, 'Email verified successfully! You can now log in.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Invalid or expired verification link.')
            return render(request, self.template_name, {'success': False})
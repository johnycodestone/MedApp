"""
accounts/urls.py

URL routing for accounts app.
Includes both API endpoints and traditional HTML views.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'accounts'

# API endpoints (REST)
api_patterns = [
    # Authentication
    path('api/register/', views.UserRegistrationAPIView.as_view(), name='api_register'),
    path('api/login/', views.UserLoginAPIView.as_view(), name='api_login'),
    path('api/logout/', views.UserLogoutAPIView.as_view(), name='api_logout'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='api_token_refresh'),
    
    # Profile management
    path('api/profile/', views.UserProfileAPIView.as_view(), name='api_profile'),
    path('api/change-password/', views.PasswordChangeAPIView.as_view(), name='api_change_password'),
    
    # Password reset
    path('api/password-reset/', views.PasswordResetRequestAPIView.as_view(), name='api_password_reset'),
    path('api/password-reset/confirm/', views.PasswordResetConfirmAPIView.as_view(), name='api_password_reset_confirm'),
    
    # Email verification
    path('api/verify-email/', views.EmailVerificationAPIView.as_view(), name='api_verify_email'),
    
    # Activity logs
    path('api/activities/', views.UserActivityListAPIView.as_view(), name='api_activities'),
]

# Traditional HTML views
html_patterns = [
    # Authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # Profile
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    
    # Password management
    path('password/change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('password/reset/', views.PasswordResetRequestView.as_view(), name='password_reset'),
    path('password/reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password/reset/confirm/<str:token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password/reset/complete/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    # Email verification
    path('verify-email/<str:token>/', views.EmailVerificationView.as_view(), name='verify_email'),
]

# Combine all patterns
urlpatterns = api_patterns + html_patterns
# Accounts App Documentation

## Overview

The `accounts` app handles user authentication, registration, and profile management for the MedApp system. It supports four user roles: Hospital, Doctor, Patient, and Administrator.

## Architecture

The app follows a clean architecture pattern with clear separation of concerns:

```
accounts/
├── models.py           # Data models (User, Tokens, Activities)
├── serializers.py      # DRF serializers for API validation
├── forms.py            # Django forms for HTML views
├── views.py            # Request handlers (API + HTML)
├── services.py         # Business logic layer
├── repositories.py     # Data access layer
├── permissions.py      # Custom permission classes
├── urls.py             # URL routing
├── tasks.py            # Background tasks (Celery)
├── signals.py          # Model signal handlers
├── utils.py            # Helper functions
└── tests/              # Test suite
```

## Models

### CustomUser
Extended Django user model with role-based authentication.

**Fields:**
- `username` - Unique username
- `email` - Email address (unique, lowercase)
- `role` - User role (HOSPITAL, DOCTOR, PATIENT, ADMIN)
- `phone` - Contact phone number
- `is_verified` - Email/phone verification status
- `created_at` - Registration timestamp
- `updated_at` - Last modification timestamp

**Methods:**
- `is_hospital()` - Check if user is a hospital
- `is_doctor()` - Check if user is a doctor
- `is_patient()` - Check if user is a patient
- `is_admin()` - Check if user is an admin
- `get_profile()` - Get role-specific profile

### VerificationToken
Manages email/phone verification and password reset tokens.

**Fields:**
- `user` - Associated user
- `token` - Unique token string
- `token_type` - EMAIL, PHONE, or PASSWORD_RESET
- `expires_at` - Expiration timestamp
- `is_used` - Usage status

**Methods:**
- `is_valid()` - Check if token is still valid

### UserActivity
Audit log for user activities and security monitoring.

**Fields:**
- `user` - User who performed action
- `action` - Activity type (LOGIN, LOGOUT, etc.)
- `ip_address` - Request IP
- `user_agent` - Browser/device info
- `metadata` - Additional context (JSON)

## API Endpoints

### Authentication

#### Register
```http
POST /api/accounts/register/
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "role": "PATIENT",
  "phone": "+1234567890"
}

Response: 201 Created
{
  "message": "Registration successful...",
  "user": {...},
  "verification_token": "..."
}
```

#### Login
```http
POST /api/accounts/login/
Content-Type: application/json

{
  "username_or_email": "johndoe",
  "password": "SecurePass123!"
}

Response: 200 OK
{
  "message": "Login successful",
  "user": {...},
  "tokens": {
    "access": "...",
    "refresh": "..."
  }
}
```

#### Logout
```http
POST /api/accounts/logout/
Authorization: Bearer {access_token}

Response: 200 OK
{
  "message": "Logout successful"
}
```

### Profile Management

#### Get Profile
```http
GET /api/accounts/profile/
Authorization: Bearer {access_token}

Response: 200 OK
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "PATIENT",
  ...
}
```

#### Update Profile
```http
PATCH /api/accounts/profile/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "first_name": "Jonathan",
  "phone": "+9876543210"
}

Response: 200 OK
{
  "message": "Profile updated successfully",
  "user": {...}
}
```

#### Change Password
```http
POST /api/accounts/change-password/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "old_password": "OldPass123!",
  "new_password": "NewPass123!",
  "new_password_confirm": "NewPass123!"
}

Response: 200 OK
{
  "message": "Password changed successfully"
}
```

### Password Reset

#### Request Reset
```http
POST /api/accounts/password-reset/
Content-Type: application/json

{
  "email": "john@example.com"
}

Response: 200 OK
{
  "message": "If an account exists..."
}
```

#### Confirm Reset
```http
POST /api/accounts/password-reset/confirm/
Content-Type: application/json

{
  "token": "...",
  "new_password": "NewPass123!",
  "new_password_confirm": "NewPass123!"
}

Response: 200 OK
{
  "message": "Password reset successful"
}
```

### Email Verification

```http
POST /api/accounts/verify-email/
Content-Type: application/json

{
  "token": "..."
}

Response: 200 OK
{
  "message": "Email verified successfully",
  "user": {...}
}
```

## Services

### UserService

Main service for user account operations.

**Methods:**
- `register_user()` - Register new user with verification
- `authenticate_user()` - Authenticate and log activity
- `update_profile()` - Update user information
- `change_password()` - Change password with validation
- `get_user_by_id()` - Retrieve user by ID
- `get_users_by_role()` - Get users by role
- `deactivate_account()` - Deactivate user account

### VerificationService

Handles email/phone verification and password resets.

**Methods:**
- `create_email_verification_token()` - Generate email token
- `verify_email()` - Verify email with token
- `create_phone_verification_token()` - Generate phone code
- `verify_phone()` - Verify phone with code
- `create_password_reset_token()` - Generate reset token
- `reset_password()` - Reset password with token

### NotificationService

Manages email notifications (uses Celery in production).

**Methods:**
- `send_verification_email()` - Send email verification
- `send_password_reset_email()` - Send password reset
- `send_welcome_email()` - Send welcome message

## Permissions

Custom permission classes for role-based access:

- `IsOwnerOrAdmin` - Object owner or admin
- `IsHospital` - Hospital users only
- `IsDoctor` - Doctor users only
- `IsPatient` - Patient users only
- `IsAdmin` - Admin users only
- `IsVerified` - Verified users only
- `IsActiveUser` - Active users only
- `IsHospitalOrDoctor` - Hospital or doctor
- `IsDoctorOrPatient` - Doctor or patient

## Signals

Automatic actions triggered by model events:

- `create_user_profile` - Create role-specific profile on user creation
- `log_profile_creation` - Log registration activity
- `cleanup_user_data` - Clean up related data before deletion
- `send_welcome_email_on_verification` - Send welcome email when verified
- `notify_admin_on_new_registration` - Notify admins of new users

## Background Tasks

Celery tasks for async processing:

- `send_verification_email_task` - Send verification email
- `send_password_reset_email_task` - Send reset email
- `send_welcome_email_task` - Send welcome email
- `cleanup_expired_tokens_task` - Delete expired tokens (daily)
- `cleanup_old_activities_task` - Archive old logs (weekly)
- `send_bulk_notification_task` - Bulk email notifications
- `generate_user_activity_report_task` - Activity reports

## Usage Examples

### Register a New Patient

```python
from accounts.services import UserService

user, token = UserService.register_user(
    username='newpatient',
    email='patient@example.com',
    password='SecurePass123!',
    role='PATIENT',
    first_name='Jane',
    last_name='Doe',
    phone='+1234567890'
)
```

### Authenticate User

```python
from accounts.services import UserService

user = UserService.authenticate_user(
    username_or_email='newpatient',
    password='SecurePass123!',
    ip_address='192.168.1.1',
    user_agent='Mozilla/5.0...'
)
```

### Verify Email

```python
from accounts.services import VerificationService

user = VerificationService.verify_email(token='...')
if user:
    print(f"Email verified for {user.username}")
```

### Change Password

```python
from accounts.services import UserService

UserService.change_password(
    user=request.user,
    old_password='OldPass123!',
    new_password='NewPass123!'
)
```

## Testing

Run tests with:

```bash
python manage.py test accounts
```

Test coverage includes:
- Model creation and validation
- Service business logic
- API endpoints
- Authentication flows
- Permission checks

## Configuration

### Settings Required

```python
# settings.py

AUTH_USER_MODEL = 'accounts.CustomUser'

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

# Email Settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@medapp.com'

# Frontend URL for email links
FRONTEND_URL = 'https://medapp.com'

# Celery for async tasks
CELERY_BROKER_URL = 'redis://localhost:6379/0'
```

## Security Considerations

1. **Password Security**
   - Passwords are hashed using Django's PBKDF2 algorithm
   - Minimum 8 characters with complexity requirements
   - Password history not stored in plain text

2. **Token Security**
   - Verification tokens expire after 24 hours
   - Reset tokens expire after 1 hour
   - Tokens are single-use only

3. **Rate Limiting**
   - Failed login attempts tracked
   - Maximum 5 attempts per 30 minutes
   - Account temporarily locked after threshold

4. **Activity Logging**
   - All authentication events logged
   - IP addresses and user agents tracked
   - Audit trail maintained for compliance

5. **Email Security**
   - Emails converted to lowercase
   - Verification required for sensitive actions
   - No email enumeration in error messages

## Integration with Other Apps

The accounts app integrates with:

- **hospitals/** - HospitalProfile creation via signals
- **doctors/** - DoctorProfile creation via signals
- **patients/** - PatientProfile creation via signals
- **adminpanel/** - Admin user management

## Maintenance

### Regular Tasks

1. **Daily**
   - Clean up expired tokens
   - Monitor failed login attempts

2. **Weekly**
   - Archive old activity logs
   - Review security alerts

3. **Monthly**
   - Generate user activity reports
   - Review inactive accounts

## Troubleshooting

### Common Issues

**Issue:** User can't verify email
- Check token expiration
- Verify email service is working
- Check spam folder

**Issue:** Login fails with correct credentials
- Check account is active
- Verify user isn't rate-limited
- Check password was set correctly

**Issue:** Password reset not working
- Verify email delivery
- Check token hasn't expired
- Ensure frontend URL is correct

## Future Enhancements

- [ ] Two-factor authentication (2FA)
- [ ] Social authentication (Google, Facebook)
- [ ] Biometric authentication support
- [ ] Advanced password policies
- [ ] Session management dashboard
- [ ] Real-time activity monitoring
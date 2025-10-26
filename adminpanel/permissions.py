# adminpanel/permissions.py

from rest_framework import permissions

# -------------------------------
# Permission: Admin or Read-Only
# -------------------------------
class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allows full access to admin users.
    Authenticated non-admins get read-only access.
    Intended for system-level models like configurations and logs.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff

# -------------------------------
# Permission: Strict Admin Access
# -------------------------------
class StrictAdminAccess(permissions.BasePermission):
    """
    Allows access only to active admin users.
    Used for sensitive system operations like backups and audit logs.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff and request.user.is_active

# -------------------------------
# Permission: Superuser Only
# -------------------------------
class SuperAdminOnly(permissions.BasePermission):
    """
    Allows access only to superusers.
    Used for critical system actions like configuration overrides.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

# -------------------------------
# Helper: Is Admin User
# -------------------------------
def is_admin_user(user):
    """
    Returns True if user is an active admin.
    """
    return user.is_staff and user.is_active

# -------------------------------
# Helper: Is Superuser
# -------------------------------
def is_superuser(user):
    """
    Returns True if user is a superuser.
    """
    return user.is_superuser

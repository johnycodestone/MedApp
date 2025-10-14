from rest_framework import permissions

class IsDoctorUser(permissions.BasePermission):
    """Allow access only to users with a doctor profile."""
    def has_permission(self, request, view):
        return hasattr(request.user, "doctor_profile")

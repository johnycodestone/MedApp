from rest_framework import permissions

class IsHospitalOrAdmin(permissions.BasePermission):
    """Allow access to hospital staff or admin users."""
    def has_permission(self, request, view):
        return request.user.is_staff or hasattr(request.user, "hospital_profile")

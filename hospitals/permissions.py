from rest_framework import permissions

class IsHospitalUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "hospital_profile")

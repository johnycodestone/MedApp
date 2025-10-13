from rest_framework import permissions

class IsDoctorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.method in permissions.SAFE_METHODS or request.user.groups.filter(name='Doctor').exists())

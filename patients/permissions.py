from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Example permission: allow if user is owner of resource or has admin role.
    Implement role checks according to your core user model.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return getattr(obj, 'user', None) == request.user

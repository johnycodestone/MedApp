from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to edit objects.
    Read-only access for other authenticated users.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any authenticated request
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions are only allowed to admin users
        return request.user and request.user.is_staff

class IsAdminOrOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admin users to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Admin always has permission
        if request.user.is_staff:
            return True
        
        # Check if the user is the owner of the object
        # This assumes the object has a 'user' or similar attribute
        return hasattr(obj, 'user') and obj.user == request.user

class StrictAdminAccess(permissions.BasePermission):
    """
    Strict permission class that only allows admin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff and request.user.is_active

class SuperAdminOnly(permissions.BasePermission):
    """
    Permission class that only allows superusers.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

def is_admin_user(user):
    """
    Helper function to check if a user is an admin.
    """
    return user.is_staff and user.is_active

def is_superuser(user):
    """
    Helper function to check if a user is a superuser.
    """
    return user.is_superuser

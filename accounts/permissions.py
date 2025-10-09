"""
accounts/permissions.py

Custom permission classes for API access control.
Implements role-based and ownership-based permissions.
"""

from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to only allow owners of an object or admins to edit/view it.
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user is the owner or an admin.
        
        Args:
            request: HTTP request
            view: View being accessed
            obj: Object being accessed
        
        Returns:
            True if user has permission, False otherwise
        """
        # Admins have full access
        if request.user.is_admin():
            return True
        
        # Check if obj is the user themselves
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # If obj is a User instance
        return obj == request.user


class IsHospital(permissions.BasePermission):
    """
    Permission to only allow hospital users.
    """
    
    def has_permission(self, request, view):
        """Check if user is a hospital"""
        return request.user.is_authenticated and request.user.is_hospital()


class IsDoctor(permissions.BasePermission):
    """
    Permission to only allow doctor users.
    """
    
    def has_permission(self, request, view):
        """Check if user is a doctor"""
        return request.user.is_authenticated and request.user.is_doctor()


class IsPatient(permissions.BasePermission):
    """
    Permission to only allow patient users.
    """
    
    def has_permission(self, request, view):
        """Check if user is a patient"""
        return request.user.is_authenticated and request.user.is_patient()


class IsAdmin(permissions.BasePermission):
    """
    Permission to only allow administrator users.
    """
    
    def has_permission(self, request, view):
        """Check if user is an admin"""
        return request.user.is_authenticated and request.user.is_admin()


class IsVerified(permissions.BasePermission):
    """
    Permission to only allow verified users.
    """
    
    def has_permission(self, request, view):
        """Check if user is verified"""
        return request.user.is_authenticated and request.user.is_verified


class IsActiveUser(permissions.BasePermission):
    """
    Permission to only allow active users.
    """
    
    def has_permission(self, request, view):
        """Check if user is active"""
        return request.user.is_authenticated and request.user.is_active


class ReadOnly(permissions.BasePermission):
    """
    Permission to only allow read-only access.
    """
    
    def has_permission(self, request, view):
        """Check if request is a safe method (GET, HEAD, OPTIONS)"""
        return request.method in permissions.SAFE_METHODS


class IsHospitalOrDoctor(permissions.BasePermission):
    """
    Permission to allow both hospital and doctor users.
    """
    
    def has_permission(self, request, view):
        """Check if user is hospital or doctor"""
        return request.user.is_authenticated and (
            request.user.is_hospital() or request.user.is_doctor()
        )


class IsDoctorOrPatient(permissions.BasePermission):
    """
    Permission to allow both doctor and patient users.
    """
    
    def has_permission(self, request, view):
        """Check if user is doctor or patient"""
        return request.user.is_authenticated and (
            request.user.is_doctor() or request.user.is_patient()
        )
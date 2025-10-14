from rest_framework import permissions

class IsAdminOrReportOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a report or admin users to edit it.
    """
    def has_permission(self, request, view):
        # Allow read access to authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write methods are only allowed to staff
        return request.user and request.user.is_staff
    
    def has_object_permission(self, request, view, obj):
        # Admin always has permission
        if request.user.is_staff:
            return True
        
        # Check if the user is the report owner or related to the report
        return (
            obj.generated_by == request.user or 
            (obj.doctor and obj.doctor.user == request.user) or 
            (obj.patient and obj.patient.user == request.user)
        )

class StrictReportAccess(permissions.BasePermission):
    """
    Strict permission class that only allows staff users to access reports.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff and request.user.is_active

class ReportReadOnly(permissions.BasePermission):
    """
    Permission class that allows read-only access to reports.
    """
    def has_permission(self, request, view):
        # Allow read-only access to authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write methods are restricted to staff
        return request.user and request.user.is_staff

def can_generate_reports(user):
    """
    Helper function to check if a user can generate reports
    """
    return user.is_staff and user.is_active

def can_view_reports(user):
    """
    Helper function to check if a user can view reports
    """
    return user.is_authenticated

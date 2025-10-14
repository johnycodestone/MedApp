from rest_framework import permissions

class IsScheduleOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of a schedule or admin users to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Admin always has permission
        if request.user.is_staff:
            return True
        
        # Check if the user is the doctor or patient of the schedule
        return (
            obj.doctor.user == request.user or 
            obj.patient.user == request.user
        )

class ScheduleReadOnly(permissions.BasePermission):
    """
    Permission class that allows read-only access to schedules.
    """
    def has_permission(self, request, view):
        # Allow read-only access to authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write methods are restricted to staff
        return request.user and request.user.is_staff

class StrictScheduleAccess(permissions.BasePermission):
    """
    Strict permission class that only allows staff users to access schedules.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff and request.user.is_active

class ScheduleReminderPermission(permissions.BasePermission):
    """
    Permission class for schedule reminders.
    """
    def has_permission(self, request, view):
        # Allow read-only access to authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write methods are restricted to staff
        return request.user and request.user.is_staff
    
    def has_object_permission(self, request, view, obj):
        # Admin always has permission
        if request.user.is_staff:
            return True
        
        # Check if the user is the doctor or patient of the schedule
        return (
            obj.schedule.doctor.user == request.user or 
            obj.schedule.patient.user == request.user
        )

def can_manage_schedules(user):
    """
    Helper function to check if a user can manage schedules.
    """
    return user.is_staff and user.is_active

def can_view_schedules(user):
    """
    Helper function to check if a user can view schedules.
    """
    return user.is_authenticated

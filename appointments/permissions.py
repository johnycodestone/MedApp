from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrDoctor(BasePermission):
    """
    Custom permission:
    - Patients can access their own appointments.
    - Doctors can access appointments where they are the doctor.
    - Admin/staff can access all appointments.
    - Only patient/doctor involved can modify (cancel/reschedule).
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Admin/staff override
        if hasattr(user, "is_staff") and user.is_staff:
            return True

        # Read-only access (GET, HEAD, OPTIONS)
        if request.method in SAFE_METHODS:
            return obj.patient == user or obj.doctor == user

        # Write access (PATCH, DELETE, etc.)
        return obj.patient == user or obj.doctor == user

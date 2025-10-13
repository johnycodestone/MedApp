from rest_framework.permissions import BasePermission

class IsOwnerOrDoctor(BasePermission):
    """
    Custom permission to allow only the patient or doctor involved to modify the appointment.
    """
    def has_object_permission(self, request, view, obj):
        return obj.patient == request.user or obj.doctor == request.user

# prescriptions/permissions.py
from rest_framework import permissions

class IsDoctorOrOwner(permissions.BasePermission):
    """
    Allow access if user is:
      - staff, or
      - the doctor on the prescription, or
      - the patient on the prescription.
    """

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        user_id = getattr(request.user, "id", None)
        if user_id is None:
            return False
        return (obj.patient_id == user_id) or (obj.doctor_id == user_id)

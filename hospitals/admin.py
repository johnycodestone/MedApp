from django.contrib import admin
from .models import Hospital, Department, DoctorAssignment, Report

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "created_at")
    search_fields = ("name", "address")

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "hospital", "description")
    search_fields = ("name",)

@admin.register(DoctorAssignment)
class DoctorAssignmentAdmin(admin.ModelAdmin):
    list_display = ("hospital", "doctor_id", "department", "duty_status")

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("title", "hospital", "created_at")

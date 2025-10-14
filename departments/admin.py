#from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Department

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "hospital_id", "head_doctor_id", "created_at")
    search_fields = ("name",)
    list_filter = ("hospital_id",)

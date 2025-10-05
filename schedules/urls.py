# schedules/urls.py

from django.urls import path
from . import views

# Below are basically our use cases for schedules that we want to access and we do that via URLs.

urlpatterns = [
    path('create/', views.create_schedule_view, name='create_schedule'), # create/ → Add a new duty or shift schedule
    path('list/', views.list_schedules_view, name='list_schedules'), # list/ → View all schedules (hospital-wide or doctor-specific)
    path('update/<int:schedule_id>/', views.update_schedule_view, name='update_schedule'), # update/<id>/ → Modify an existing schedule
    path('delete/<int:schedule_id>/', views.delete_schedule_view, name='delete_schedule'), # delete/<id>/ → Remove a schedule entry
]

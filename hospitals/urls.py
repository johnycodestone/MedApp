# hospitals/urls.py

from django.urls import path
from . import views

# Below are basically our use cases for hospitals that we want to access and we do that via URLs.

urlpatterns = [
    path('create/', views.create_hospital_view, name='create_hospital'), # create/ → Add a new hospital
    path('list/', views.list_hospitals_view, name='list_hospitals'), # list/ → View all hospitals
    path('update/<int:hospital_id>/', views.update_hospital_view, name='update_hospital'), # update/<id>/ → Modify hospital details
    path('delete/<int:hospital_id>/', views.delete_hospital_view, name='delete_hospital'), # delete/<id>/ → Remove a hospital
    path('assign-duty/<int:hospital_id>/', views.assign_duty_view, name='assign_duty'), # assign-duty/<id>/ → Assign doctors or staff to duty shifts
]

# departments/urls.py

from django.urls import path
from . import views

# Below are basically our use cases for departments that we want to access and we do that via URLs.

urlpatterns = [
    path('create/', views.create_department_view, name='create_department'), # create/ → Add a new department
    path('list/', views.list_departments_view, name='list_departments'), # list/ → View all departments
    path('update/<int:dept_id>/', views.update_department_view, name='update_department'), # update/<id>/ → Modify department details
    path('delete/<int:dept_id>/', views.delete_department_view, name='delete_department'), # delete/<id>/ → Remove a department
]

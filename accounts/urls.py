# accounts/urls.py

from django.urls import path
from . import views

# Below are basically our use cases for accounts that we want to access and we do that via URLs.

urlpatterns = [
    path('login/', views.login_view, name='login'), # login/ → user login
    path('register/', views.register_view, name='register'), # register/ → new user registration
    path('logout/', views.logout_view, name='logout'), # logout/ → session termination
    path('dashboard/', views.dashboard_view, name='dashboard'), # dashboard/ → role-based landing page (Doctor, Patient, Admin, etc.)
]

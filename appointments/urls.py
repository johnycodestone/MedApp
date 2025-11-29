from django.urls import path
from .views import (
    AppointmentViewSet,
    AppointmentCreateView,
    appointment_list_view,
    AppointmentCancelView,  # ✅ added for cancellation
    appointment_detail_view,
)
from . import views  # ✅ import views module directly
app_name = "appointments"

urlpatterns = [
    # -------------------------------
    # Template-based views (frontend)
    # -------------------------------
    path('', appointment_list_view, name='appointment-list'),
    path('create/', AppointmentCreateView.as_view(), name='create'),
    path('<int:pk>/cancel/', AppointmentCancelView.as_view(), name='appointment-cancel'),  # ✅ new cancel route
    path('<int:pk>/', appointment_detail_view, name='detail'),  # ✅ now resolves correctly
    # -------------------------------
    # API endpoints (DRF)
    # -------------------------------
    path('api/', AppointmentViewSet.as_view({'get': 'list'}), name='appointment-api-list'),
    path('api/<int:pk>/', AppointmentViewSet.as_view({'get': 'retrieve'}), name='appointment-api-detail'),
]

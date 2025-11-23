'''from django.urls import path
from .views import AppointmentViewSet,AppointmentCreateView

app_name = "appointments"

urlpatterns = [
    path('', AppointmentViewSet.as_view({'get': 'list'}), name='appointment-list'),
    path('<int:pk>/', AppointmentViewSet.as_view({'get': 'retrieve'}), name='appointment-detail'),
    path('create/', AppointmentCreateView.as_view(), name='create'),  # ✅ new route
]'''

from django.urls import path
from .views import (
    AppointmentViewSet,
    AppointmentCreateView,
    appointment_list_view  # ✅ import your template view
)

app_name = "appointments"

urlpatterns = [
    # ✅ Route to template-based list view
    path('', appointment_list_view, name='appointment-list'),

    # DRF endpoints (optional, keep if needed for API)
    path('api/', AppointmentViewSet.as_view({'get': 'list'}), name='appointment-api-list'),
    path('api/<int:pk>/', AppointmentViewSet.as_view({'get': 'retrieve'}), name='appointment-api-detail'),

    # Create view
    path('create/', AppointmentCreateView.as_view(), name='create'),
]


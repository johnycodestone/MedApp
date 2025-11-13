from django.urls import path
from .views import AppointmentViewSet,AppointmentCreateView

app_name = "appointments"

urlpatterns = [
    path('', AppointmentViewSet.as_view({'get': 'list'}), name='appointment-list'),
    path('<int:pk>/', AppointmentViewSet.as_view({'get': 'retrieve'}), name='appointment-detail'),
    path('create/', AppointmentCreateView.as_view(), name='create'),  # ✅ new route
]

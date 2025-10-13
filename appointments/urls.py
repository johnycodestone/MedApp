from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppointmentViewSet

router = DefaultRouter()
router.register(r'', AppointmentViewSet, basename='appointments')  # ✅ Use empty string here

urlpatterns = [
    path('', include(router.urls)),  # ✅ This mounts POST /appointments/
]

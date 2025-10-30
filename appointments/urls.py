from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AppointmentViewSet
app_name = "appointments"
router = DefaultRouter()
#router.register(r'', AppointmentViewSet, basename='appointments')  # ✅ Use empty string here

#urlpatterns = [
 #   path('', include(router.urls)),  # ✅ This mounts POST /appointments/
#]

router = DefaultRouter()
router.register(r'api', AppointmentViewSet, basename='appointment')

urlpatterns = [
    # UI Routes
    path('', AppointmentViewSet.as_view({'get': 'list'}), name='list'),
    path('<int:pk>/', AppointmentViewSet.as_view({'get': 'retrieve'}), name='detail'),
    
    # API Routes
    path('', include(router.urls)),
]
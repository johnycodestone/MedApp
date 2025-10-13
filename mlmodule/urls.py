# mlmodule/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MLModelViewSet,
    PredictionViewSet,
    urgency_triage_view,
    diabetes_prediction_view,
    health_tips_view
)

router = DefaultRouter()
router.register(r'models', MLModelViewSet)
router.register(r'predictions', PredictionViewSet, basename='predictions')

urlpatterns = [
    path('', include(router.urls)),  # Enables /predictions/ and /models/
    path('triage/', urgency_triage_view, name='urgency_triage'),
    path('predict-diabetes/', diabetes_prediction_view, name='diabetes_prediction'),
    path('health-tips/', health_tips_view, name='health_tips'),
]

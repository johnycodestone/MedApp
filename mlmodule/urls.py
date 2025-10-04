# mlmodule/urls.py

from django.urls import path
from . import views

# Below are basically our use cases for the ML module that we want to access and we do that via URLs.

urlpatterns = [
    path('triage/', views.urgency_triage_view, name='urgency_triage'), # triage/ → Predict urgency level based on symptoms
    path('predict-diabetes/', views.diabetes_prediction_view, name='diabetes_prediction'), # predict-diabetes/ → ML-based diabetes risk classifier
    path('health-tips/', views.health_tips_view, name='health_tips'),  # health-tips/ → Serve awareness content or model-generated advice
]

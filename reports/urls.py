from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReportCategoryViewSet,
    ReportViewSet,
    ReportTemplateViewSet,
    ReportDashboardView,
    report_export_view,
)

app_name = "reports"

# Use DRF router for your ViewSets
router = DefaultRouter()
router.register(r'categories', ReportCategoryViewSet, basename='report-category')
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'templates', ReportTemplateViewSet, basename='report-template')

urlpatterns = [
    # Dashboard (UI)
    path('dashboard/', ReportDashboardView.as_view(), name='dashboard'),

    # Export view (UI)
    path('export/', report_export_view, name='export'),

    # API routes from DRF ViewSets
    path('', include(router.urls)),
]

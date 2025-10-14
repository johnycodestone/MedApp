# reports/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReportCategoryViewSet,
    ReportViewSet,
    ReportTemplateViewSet,
    ReportDashboardView,
    report_export_view
)

# Create a router for API viewsets
router = DefaultRouter()
router.register(r'categories', ReportCategoryViewSet, basename='report-category')
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'templates', ReportTemplateViewSet, basename='report-template')

urlpatterns = [
    # Dashboard and Main Views
    path('', ReportDashboardView.as_view(), name='report-dashboard'),
    path('export/', report_export_view, name='report-export'),
    
    # API Routes
    path('api/', include(router.urls)),
    
    # Additional Report-specific routes
    path('api/stats/', include([
        path('category-reports/<int:pk>/', 
             ReportCategoryViewSet.as_view({'get': 'category_reports'}), 
             name='category-reports'),
        path('recent/', 
             ReportViewSet.as_view({'get': 'recent_reports'}), 
             name='recent-reports'),
        path('report-summary/', 
             ReportViewSet.as_view({'get': 'report_stats'}), 
             name='report-stats'),
        path('template-preview/<int:pk>/', 
             ReportTemplateViewSet.as_view({'get': 'template_preview'}), 
             name='template-preview'),
    ])),
]

# Optional: Custom error handlers for report views
handler400 = 'reports.views.bad_request'
handler403 = 'reports.views.permission_denied'
handler404 = 'reports.views.page_not_found'
handler500 = 'reports.views.server_error'

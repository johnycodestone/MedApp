from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView, ListView, DetailView
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from django.utils import timezone

from .models import ReportCategory, Report, ReportTemplate
from .serializers import (
    ReportCategorySerializer, 
    ReportSerializer, 
    ReportTemplateSerializer
)
from .permissions import (
    IsAdminOrReportOwner, 
    StrictReportAccess
)

class ReportCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Report Categories
    """
    queryset = ReportCategory.objects.all()
    serializer_class = ReportCategorySerializer
    permission_classes = [StrictReportAccess]
    
    @action(detail=True, methods=['GET'])
    def category_reports(self, request, pk=None):
        """
        Get all reports for a specific category
        """
        category = self.get_object()
        reports = category.reports.all()
        serializer = ReportSerializer(reports, many=True)
        return Response(serializer.data)

class ReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Reports
    """
    queryset = Report.objects.select_related(
        'doctor', 
        'patient', 
        'category', 
        'generated_by', 
        'reviewed_by'
    )
    serializer_class = ReportSerializer
    permission_classes = [IsAdminOrReportOwner]
    
    def get_queryset(self):
        """
        Customize queryset based on user permissions
        """
        user = self.request.user
        if user.is_staff:
            return self.queryset
        return self.queryset.filter(
            Q(generated_by=user) | 
            Q(doctor__user=user) | 
            Q(patient__user=user)
        )
    
    @action(detail=False, methods=['GET'])
    def recent_reports(self, request):
        """
        Get recent reports
        """
        recent = self.queryset.filter(
            generated_at__gte=timezone.now() - timezone.timedelta(days=30)
        ).order_by('-generated_at')[:10]
        
        serializer = self.get_serializer(recent, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def report_stats(self, request):
        """
        Get report statistics
        """
        total_reports = self.queryset.count()
        status_breakdown = self.queryset.values('status').annotate(count=Count('status'))
        priority_breakdown = self.queryset.values('priority').annotate(count=Count('priority'))
        
        return Response({
            'total_reports': total_reports,
            'status_breakdown': list(status_breakdown),
            'priority_breakdown': list(priority_breakdown)
        })

class ReportTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Report Templates
    """
    queryset = ReportTemplate.objects.select_related('category')
    serializer_class = ReportTemplateSerializer
    permission_classes = [StrictReportAccess]
    
    @action(detail=True, methods=['GET'])
    def template_preview(self, request, pk=None):
        """
        Get a preview of the report template
        """
        template = self.get_object()
        return Response({
            'name': template.name,
            'structure': template.template_structure
        })

# Dashboard and Utility Views
class ReportDashboardView(TemplateView):
    """
    Main dashboard for reports
    """
    template_name = 'reports/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_reports'] = Report.objects.count()
        context['recent_reports'] = Report.objects.order_by('-generated_at')[:5]
        context['report_categories'] = ReportCategory.objects.all()
        return context

# Utility Function Views
@login_required
def report_export_view(request):
    """
    Render report export view
    """
    reports = Report.objects.filter(
        Q(generated_by=request.user) | 
        Q(doctor__user=request.user) | 
        Q(patient__user=request.user)
    )
    return render(request, 'reports/export.html', {'reports': reports})

# Error Handler Views
def bad_request(request, exception):
    """
    Custom 400 error handler for reports
    """
    return render(request, 'reports/errors/400.html', status=400)

def permission_denied(request, exception):
    """
    Custom 403 error handler for reports
    """
    return render(request, 'reports/errors/403.html', status=403)

def page_not_found(request, exception):
    """
    Custom 404 error handler for reports
    """
    return render(request, 'reports/errors/404.html', status=404)

def server_error(request):
    """
    Custom 500 error handler for reports
    """
    return render(request, 'reports/errors/500.html', status=500)


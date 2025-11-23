# reports/views.py
#
# Purpose:
#   - Provide both API endpoints (via DRF ViewSets) and frontend HTML views.
#   - API endpoints are preserved exactly (no breaking changes).
#   - Frontend views (dashboard, export, error handlers) integrate with root-level templates.
#
# Structure:
#   Section A: DRF ViewSets (Categories, Reports, Templates)
#   Section B: Frontend HTML views (Dashboard, Export)
#   Section C: Error handler views
#

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
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

# ---------------------------------------------------------------------------
# Section A: DRF ViewSets
# ---------------------------------------------------------------------------

class ReportCategoryViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Report Categories.
    Provides CRUD operations and a custom action to fetch reports in a category.
    """
    queryset = ReportCategory.objects.all()
    serializer_class = ReportCategorySerializer
    permission_classes = [StrictReportAccess]

    @action(detail=True, methods=['GET'])
    def category_reports(self, request, pk=None):
        """
        Custom action:
        GET /report-categories/{id}/category_reports/
        Returns all reports belonging to a specific category.
        """
        category = self.get_object()
        reports = category.reports.all()
        serializer = ReportSerializer(reports, many=True)
        return Response(serializer.data)


class ReportViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Reports.
    Provides CRUD operations and custom actions for recent reports and statistics.
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
        Scope queryset based on user permissions:
        - Staff users see all reports.
        - Normal users see only reports they generated, reviewed, or are linked to.
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
        Custom action:
        GET /reports/recent_reports/
        Returns the 10 most recent reports generated in the last 30 days.
        """
        recent = self.queryset.filter(
            generated_at__gte=timezone.now() - timezone.timedelta(days=30)
        ).order_by('-generated_at')[:10]

        serializer = self.get_serializer(recent, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def report_stats(self, request):
        """
        Custom action:
        GET /reports/report_stats/
        Returns statistics: total count, breakdown by status and priority.
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
    API ViewSet for Report Templates.
    Provides CRUD operations and a custom preview action.
    """
    queryset = ReportTemplate.objects.select_related('category')
    serializer_class = ReportTemplateSerializer
    permission_classes = [StrictReportAccess]

    @action(detail=True, methods=['GET'])
    def template_preview(self, request, pk=None):
        """
        Custom action:
        GET /report-templates/{id}/template_preview/
        Returns a preview of the template structure.
        """
        template = self.get_object()
        return Response({
            'name': template.name,
            'structure': template.template_structure
        })


# ---------------------------------------------------------------------------
# Section B: Frontend HTML Views
# ---------------------------------------------------------------------------

class ReportDashboardView(TemplateView):
    """
    Frontend dashboard for reports.
    Renders reports/templates/reports/dashboard.html.
    """
    template_name = 'reports/dashboard.html'

    def get_context_data(self, **kwargs):
        """
        Context variables for the dashboard template:
        - total_reports: total number of reports in the system
        - recent_reports: last 5 reports (ordered by generated_at)
        - report_categories: all categories
        - crumbs: breadcrumb trail for includes/breadcrumbs.html
        """
        context = super().get_context_data(**kwargs)
        context['total_reports'] = Report.objects.count()
        context['recent_reports'] = Report.objects.order_by('-generated_at')[:5]
        context['report_categories'] = ReportCategory.objects.all()
        context['crumbs'] = [
            {"label": "Home", "url": "/"},
            {"label": "Reports", "url": None},
        ]
        return context


@login_required
def report_export_view(request):
    """
    Frontend export view.
    Renders reports/templates/reports/export.html.
    Filters reports accessible to the current user.
    """
    reports = Report.objects.filter(
        Q(generated_by=request.user) |
        Q(doctor__user=request.user) |
        Q(patient__user=request.user)
    )
    return render(request, 'reports/export.html', {'reports': reports})


# ---------------------------------------------------------------------------
# Section C: Error Handler Views
# ---------------------------------------------------------------------------

def bad_request(request, exception):
    """Custom 400 error handler for reports."""
    return render(request, 'reports/errors/400.html', status=400)

def permission_denied(request, exception):
    """Custom 403 error handler for reports."""
    return render(request, 'reports/errors/403.html', status=403)

def page_not_found(request, exception):
    """Custom 404 error handler for reports."""
    return render(request, 'reports/errors/404.html', status=404)

def server_error(request):
    """Custom 500 error handler for reports."""
    return render(request, 'reports/errors/500.html', status=500)

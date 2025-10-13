from rest_framework import serializers
from django.utils import timezone
from .models import ReportCategory, Report, ReportTemplate

class ReportCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Report Categories
    """
    total_reports = serializers.SerializerMethodField()
    
    class Meta:
        model = ReportCategory
        fields = ['id', 'name', 'description', 'report_type', 'total_reports']
    
    def get_total_reports(self, obj):
        """
        Get total number of reports in this category
        """
        return obj.reports.count()
    
    def validate_name(self, value):
        """
        Validate category name is unique
        """
        if ReportCategory.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("A category with this name already exists.")
        return value

class ReportSerializer(serializers.ModelSerializer):
    """
    Serializer for Reports with comprehensive details
    """
    doctor_name = serializers.CharField(source='doctor.full_name', read_only=True)
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    generated_by_username = serializers.CharField(source='generated_by.username', read_only=True)
    reviewed_by_username = serializers.CharField(source='reviewed_by.username', read_only=True)
    report_duration = serializers.SerializerMethodField()
    
    class Meta:
        model = Report
        fields = [
            'id', 
            'title', 
            'description', 
            'doctor', 
            'doctor_name',
            'patient', 
            'patient_name',
            'category', 
            'category_name',
            'content',
            'raw_data',
            'status', 
            'priority',
            'generated_at',
            'updated_at',
            'published_at',
            'generated_by',
            'generated_by_username',
            'reviewed_by',
            'reviewed_by_username',
            'report_duration'
        ]
        read_only_fields = ['generated_at', 'updated_at', 'published_at']
    
    def get_report_duration(self, obj):
        """
        Get report generation duration
        """
        duration = obj.get_report_duration()
        return str(duration) if duration else None
    
    def validate(self, data):
        """
        Validate report constraints
        """
        # Ensure generated_by is the current user if not provided
        if not data.get('generated_by'):
            user = self.context['request'].user
            data['generated_by'] = user
        
        return data

class ReportTemplateSerializer(serializers.ModelSerializer):
    """
    Serializer for Report Templates
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    total_reports = serializers.SerializerMethodField()
    
    class Meta:
        model = ReportTemplate
        fields = [
            'id', 
            'name', 
            'description', 
            'template_structure', 
            'category',
            'category_name',
            'total_reports',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_total_reports(self, obj):
        """
        Get total number of reports using this template
        """
        return Report.objects.filter(category=obj.category).count()
    
    def validate_name(self, value):
        """
        Validate template name is unique
        """
        if ReportTemplate.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("A template with this name already exists.")
        return value

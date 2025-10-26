# reports/apps.py

from django.apps import AppConfig
from django.db.models.signals import post_migrate


class ReportsConfig(AppConfig):
    """
    Configuration class for the 'reports' app.
    Handles app setup, signal registration, and post-migration tasks.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reports'
    verbose_name = 'Medical Reporting System'

    def ready(self):
        """
        Called when the app is fully loaded.
        Use this to register signals and defer database-related tasks until after migrations.
        """
        # ✅ Import signals to ensure they are registered
        import reports.signals

        # ✅ Register post-migrate hook to safely seed ReportCategory data
        try:
            from .signals import populate_report_categories
            post_migrate.connect(populate_report_categories, sender=self)
        except ImportError:
            pass  # Silently ignore if signal utility is not available

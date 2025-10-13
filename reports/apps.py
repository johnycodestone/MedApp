from django.apps import AppConfig


class ReportsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reports'
    verbose_name = 'Medical Reporting System'

    def ready(self):
        """
        Method called when the app is ready to be used.
        Can be used for importing signals, initializing app-specific configurations, etc.
        """
        # Import signals to ensure they are registered
        import reports.signals

        # Optional: Perform any startup tasks or validations
        try:
            from .utils import validate_report_configurations
            validate_report_configurations()
        except ImportError:
            pass  # Silently ignore if validation utility is not available

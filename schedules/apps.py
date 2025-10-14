from django.apps import AppConfig


class SchedulesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'schedules'
    verbose_name = 'Medical Scheduling System'

    def ready(self):
        """
        Method called when the app is ready to be used.
        Can be used for importing signals, initializing app-specific configurations, etc.
        """
        # Import signals to ensure they are registered
        import schedules.signals

        # Optional: Perform any startup tasks or validations
        try:
            from .utils import validate_schedule_configurations
            validate_schedule_configurations()
        except ImportError:
            pass  # Silently ignore if validation utility is not available

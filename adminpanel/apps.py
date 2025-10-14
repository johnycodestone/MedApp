from django.apps import AppConfig


class AdminpanelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'adminpanel'
    verbose_name = 'Medical Application Admin Panel'

    def ready(self):
        """
        Method called when the app is ready to be used.
        Can be used for importing signals, initializing app-specific configurations, etc.
        """
        # Import signals to ensure they are registered
        import adminpanel.signals

        # Optional: Perform any startup tasks or validations
        try:
            from .utils import validate_admin_configurations
            validate_admin_configurations()
        except ImportError:
            pass  # Silently ignore if validation utility is not available

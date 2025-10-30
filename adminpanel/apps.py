# adminpanel/apps.py

from django.apps import AppConfig

class AdminpanelConfig(AppConfig):
    """
    Configuration class for the adminpanel app.

    This app handles system-level administration for MedApp, including:
    - System configurations
    - Logs and metrics
    - Backup tracking
    - Audit trails
    - Role-based permissions

    It does NOT manage domain-specific models like users, doctors, or patients.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'adminpanel'
    verbose_name = 'MedApp System Administration'

    def ready(self):
        """
        Called when the app is fully loaded.

        Responsibilities:
        - Register signal handlers for system models
        - Avoid any database access here to prevent migration-time crashes
        """
        # Register signal handlers
        import adminpanel.signals

        # ⚠️ DO NOT call validate_admin_configurations() here.
        # It queries the database, which may not be ready during migrations.
        # Instead, call it from a safe runtime location (e.g., dashboard view or management command).

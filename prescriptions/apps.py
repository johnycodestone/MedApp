# prescriptions/apps.py
from django.apps import AppConfig

class PrescriptionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "prescriptions"

    def ready(self):
        # ensure signals are registered
        from . import signals  # noqa: F401

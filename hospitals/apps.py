#from django.apps import AppConfig
#
#
#class HospitalsConfig(AppConfig):
#    default_auto_field = 'django.db.models.BigAutoField'
#    name = 'hospitals'
#
from django.apps import AppConfig

class HospitalsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hospitals"
    verbose_name = "Hospital Management"

    def ready(self):
        # Import signals so they get registered when the app is loaded
        import hospitals.signals

from django.apps import AppConfig


class MedidasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.medidas'
    
    def ready(self):
        import apps.medidas.signals

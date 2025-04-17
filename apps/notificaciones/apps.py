# apps/notificaciones/apps.py
from django.apps import AppConfig


class NotificacionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notificaciones'

    def ready(self):
        import apps.notificaciones.signals

from django.apps import AppConfig


class AuditoriasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.auditorias'

    def ready(self):
        import apps.auditorias.signals
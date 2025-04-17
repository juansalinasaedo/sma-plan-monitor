# apps/usuarios/apps.py
from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.usuarios'

    def ready(self):
        """
        Importa las señales cuando la aplicación está lista.
        """
        import apps.usuarios.signals
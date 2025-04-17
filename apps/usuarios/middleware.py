# apps/usuarios/middleware.py
import re
from django.utils import timezone
from .models import HistorialAcceso


class HistorialAccesoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization

    def __call__(self, request):
        # Code to be executed for each request before the view is called
        response = self.get_response(request)
        # Code to be executed for each request/response after the view is called

        # Solo registramos inicios de sesión exitosos
        if (request.path == '/login/' or
            request.path.endswith('accounts/login/') or
            re.match(r'^/admin/login', request.path)) and \
                request.method == 'POST' and \
                response.status_code == 302 and \
                request.user.is_authenticated:

            # Extraer información de la solicitud
            ip = self.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')

            # Extraer información básica del User-Agent
            dispositivo = "Desconocido"
            navegador = "Desconocido"

            if user_agent:
                if 'Mobile' in user_agent:
                    dispositivo = "Móvil"
                elif 'Tablet' in user_agent:
                    dispositivo = "Tablet"
                else:
                    dispositivo = "Escritorio"

                if 'Chrome' in user_agent:
                    navegador = "Chrome"
                elif 'Firefox' in user_agent:
                    navegador = "Firefox"
                elif 'Safari' in user_agent:
                    navegador = "Safari"
                elif 'Edge' in user_agent:
                    navegador = "Edge"
                elif 'MSIE' in user_agent or 'Trident' in user_agent:
                    navegador = "Internet Explorer"

            # Crear registro de acceso
            HistorialAcceso.objects.create(
                usuario=request.user,
                ip=ip,
                dispositivo=dispositivo,
                navegador=navegador,
                exitoso=True
            )

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
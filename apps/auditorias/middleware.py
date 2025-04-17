import json
from django.utils import timezone
from .models import Auditoria


class AuditoriaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Procesamiento antes de la vista

        response = self.get_response(request)

        # Procesamiento después de la vista

        # Registrar accesos de inicio y cierre de sesión
        if request.path.endswith('/login/') and request.method == 'POST' and response.status_code == 302:
            if request.user.is_authenticated:
                self._registrar_login(request)

        if 'logout' in request.path and request.method == 'GET' and request.user.is_authenticated:
            self._registrar_logout(request)

        return response

    def _registrar_login(self, request):
        """Registra el inicio de sesión en la auditoría"""
        Auditoria.objects.create(
            usuario=request.user,
            accion='login',
            descripcion=f"Inicio de sesión del usuario {request.user.username}",
            ip=self._get_client_ip(request),
            navegador=request.META.get('HTTP_USER_AGENT', ''),
            datos_adicionales={
                'method': request.method,
                'path': request.path,
            }
        )

    def _registrar_logout(self, request):
        """Registra el cierre de sesión en la auditoría"""
        Auditoria.objects.create(
            usuario=request.user,
            accion='logout',
            descripcion=f"Cierre de sesión del usuario {request.user.username}",
            ip=self._get_client_ip(request),
            navegador=request.META.get('HTTP_USER_AGENT', ''),
            datos_adicionales={
                'method': request.method,
                'path': request.path,
            }
        )

    def _get_client_ip(self, request):
        """Obtiene la dirección IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
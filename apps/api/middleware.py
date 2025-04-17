import time
from django.utils import timezone
from apps.auditorias.models import Auditoria


class APILoggingMiddleware:
    """
    Middleware para registrar todas las llamadas a la API.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Solo procesar peticiones a la API
        if not request.path.startswith('/api/'):
            return self.get_response(request)

        # tiempo de inicio
        start_time = time.time()

        # Procesar la petición
        response = self.get_response(request)

        # Calcular tiempo de respuesta
        duration = time.time() - start_time

        # llamada a la API en auditoría
        try:
            # información de la petición
            ip = self._get_client_ip(request)
            method = request.method
            path = request.path
            user = request.user if request.user.is_authenticated else None
            status_code = response.status_code

            # Registrar en auditoría
            Auditoria.objects.create(
                usuario=user,
                accion='api_call',
                descripcion=f"Llamada a la API: {method} {path}",
                ip=ip,
                navegador=request.META.get('HTTP_USER_AGENT', ''),
                datos_adicionales={
                    'method': method,
                    'path': path,
                    'status_code': status_code,
                    'duration_ms': round(duration * 1000, 2),
                    'response_size': len(response.content) if hasattr(response, 'content') else 0,
                }
            )
        except Exception as e:
            # No interrumpir la respuesta por errores en el registro
            print(f"Error al registrar llamada a la API: {str(e)}")

        return response

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class TokenPrefixMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header and 'Token ' not in auth_header:
            request.META['HTTP_AUTHORIZATION'] = f'Token {auth_header}'
        return self.get_response(request)

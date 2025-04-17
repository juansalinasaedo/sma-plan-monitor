from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def enviar_notificacion_email(notificacion):
    """Envía una notificación por email"""
    if not notificacion.usuario.email:
        return False

    # Preparar contexto para la plantilla
    context = {
        'usuario': notificacion.usuario,
        'titulo': notificacion.titulo,
        'mensaje': notificacion.mensaje,
        'tipo': notificacion.tipo.nombre,
        'fecha': notificacion.fecha_envio,
        'enlace': f"{settings.SITE_URL}{notificacion.enlace}" if notificacion.enlace else None,
        'color': notificacion.tipo.color or '#007bff'
    }

    # Renderizar el contenido HTML
    html_message = render_to_string('notificaciones/email/notificacion.html', context)
    plain_message = strip_tags(html_message)

    # Enviar el email
    try:
        send_mail(
            subject=notificacion.titulo,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notificacion.usuario.email],
            html_message=html_message,
            fail_silently=False
        )

        # Marcar como enviado por email
        notificacion.enviada_email = True
        notificacion.fecha_envio_email = timezone.now()
        notificacion.save(update_fields=['enviada_email', 'fecha_envio_email'])

        return True
    except Exception as e:
        print(f"Error enviando email: {str(e)}")
        return False
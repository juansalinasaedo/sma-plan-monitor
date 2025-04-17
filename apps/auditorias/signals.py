from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.forms.models import model_to_dict
from django.utils.text import camel_case_to_spaces

from .models import Auditoria, CambioDetalle, ConfiguracionAuditoria


def registrar_auditoria(instance, action, user=None, request=None):
    """
    Función central para registrar auditorías.
    """
    # Obtener el tipo de contenido del modelo
    content_type = ContentType.objects.get_for_model(instance)

    # Verificar si este modelo debe ser auditado
    try:
        config = ConfiguracionAuditoria.objects.get(content_type=content_type, activo=True)
    except ConfiguracionAuditoria.DoesNotExist:
        # Si no hay configuración, verificar si deberíamos crear una por defecto
        model_name = instance.__class__.__name__
        if model_name in ['Medida', 'Organismo', 'Usuario', 'RegistroAvance']:
            # Modelos críticos se auditan por defecto
            config = ConfiguracionAuditoria.objects.create(
                content_type=content_type,
                auditar_creacion=True,
                auditar_modificacion=True,
                auditar_eliminacion=True
            )
        else:
            # No auditar este modelo
            return None

    # Verificar si esta acción debe ser auditada
    if action == 'creacion' and not config.auditar_creacion:
        return None
    if action == 'modificacion' and not config.auditar_modificacion:
        return None
    if action == 'eliminacion' and not config.auditar_eliminacion:
        return None

    # Obtener información para la descripción
    model_name = camel_case_to_spaces(instance.__class__.__name__).capitalize()
    instance_id = instance.pk
    try:
        instance_str = str(instance)
    except:
        instance_str = f"{model_name} #{instance_id}"

    # Crear descripción
    if action == 'creacion':
        descripcion = f"Creación de {model_name}: {instance_str}"
    elif action == 'modificacion':
        descripcion = f"Modificación de {model_name}: {instance_str}"
    else:  # eliminacion
        descripcion = f"Eliminación de {model_name}: {instance_str}"

    # Datos adicionales
    datos_adicionales = {}
    if hasattr(instance, 'get_absolute_url'):
        datos_adicionales['url'] = instance.get_absolute_url()

    # Obtener IP y navegador si hay request disponible
    ip = None
    navegador = request.META.get('HTTP_USER_AGENT', 'desconocido') if request else 'desconocido'

    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        navegador = request.META.get('HTTP_USER_AGENT', '')

    # Crear registro de auditoría
    auditoria = Auditoria.objects.create(
        usuario=user,
        accion=action,
        descripcion=descripcion,
        content_type=content_type,
        object_id=instance_id,
        ip=ip,
        navegador=navegador,
        datos_adicionales=datos_adicionales
    )

    # Si es una modificación, registrar los cambios en campos
    if action == 'modificacion' and hasattr(instance, '_original_state'):
        original_dict = instance._original_state
        current_dict = model_to_dict(instance)

        # Campos a auditar
        campos_auditados = config.campos_auditados or []

        for campo, valor_nuevo in current_dict.items():
            # Si hay campos específicos configurados y este no está incluido, saltarlo
            if campos_auditados and campo not in campos_auditados:
                continue

            # Skip some fields
            if campo in ['id', 'pk', 'created_at', 'updated_at']:
                continue

            valor_anterior = original_dict.get(campo)

            # Solo registrar si hubo cambio
            if valor_anterior != valor_nuevo:
                CambioDetalle.objects.create(
                    auditoria=auditoria,
                    campo=campo,
                    valor_anterior=str(valor_anterior) if valor_anterior is not None else None,
                    valor_nuevo=str(valor_nuevo) if valor_nuevo is not None else None
                )

    return auditoria


@receiver(post_save)
def auditoria_post_save(sender, instance, created, **kwargs):
    """Auditar creación y modificación de modelos."""
    # Ignorar modelos de la propia app de auditoría para evitar recursión
    if sender.__module__.startswith('apps.auditorias.'):
        return

    # Ignorar modelos del admin de Django y otras apps del sistema
    if sender.__module__.startswith('django.'):
        return

    # Capturar el estado original si es una modificación (para la próxima vez)
    if not created:
        instance._original_state = model_to_dict(instance)

    # Registrar la auditoría
    user = None
    if hasattr(instance, '_audit_user'):
        user = instance._audit_user

    request = None
    if hasattr(instance, '_audit_request'):
        request = instance._audit_request

    action = 'creacion' if created else 'modificacion'
    registrar_auditoria(instance, action, user, request)


@receiver(post_delete)
def auditoria_post_delete(sender, instance, **kwargs):
    """Auditar eliminación de modelos."""
    # Ignorar modelos de la propia app de auditoría para evitar recursión
    if sender.__module__.startswith('apps.auditorias.'):
        return

    # Ignorar modelos del admin de Django y otras apps del sistema
    if sender.__module__.startswith('django.'):
        return

    # Registrar la auditoría
    user = None
    if hasattr(instance, '_audit_user'):
        user = instance._audit_user

    request = None
    if hasattr(instance, '_audit_request'):
        request = instance._audit_request

    registrar_auditoria(instance, 'eliminacion', user, request)
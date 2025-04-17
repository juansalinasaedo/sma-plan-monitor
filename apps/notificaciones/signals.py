from django.dispatch import receiver
from apps.usuarios.models import Usuario
from .models import ConfiguracionNotificaciones, TipoNotificacion
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

from apps.medidas.models import Medida, RegistroAvance, AsignacionMedida
from .models import Notificacion, TipoNotificacion


@receiver(post_save, sender=Usuario)
def crear_configuracion_notificaciones(sender, instance, created, **kwargs):
    """
    Crea una configuración de notificaciones para cada usuario nuevo.
    """
    if created:
        # Crear configuración básica
        config = ConfiguracionNotificaciones.objects.create(
            usuario=instance,
            recibir_email=instance.recibir_notificaciones_email,
            recibir_sistema=instance.recibir_notificaciones_sistema
        )

        # Añadir todos los tipos de notificación relevantes según el rol del usuario
        tipos_relevantes = []

        if instance.is_superadmin:
            tipos_relevantes.extend(TipoNotificacion.objects.filter(para_superadmin=True))
        elif instance.is_admin_sma:
            tipos_relevantes.extend(TipoNotificacion.objects.filter(para_admin_sma=True))
        elif instance.is_organismo:
            tipos_relevantes.extend(TipoNotificacion.objects.filter(para_organismos=True))
        elif instance.is_ciudadano:
            tipos_relevantes.extend(TipoNotificacion.objects.filter(para_ciudadanos=True))

        # Añadir los tipos encontrados a la configuración
        config.tipos_habilitados.add(*tipos_relevantes)


@receiver(post_save, sender=RegistroAvance)
def notificar_nuevo_avance(sender, instance, created, **kwargs):
    """Envía notificaciones cuando se registra un nuevo avance"""
    if created:
        # Obtener el tipo de notificación (crearlo si no existe)
        tipo, _ = TipoNotificacion.objects.get_or_create(
            codigo="nuevo_avance",
            defaults={
                'nombre': "Nuevo avance registrado",
                'descripcion': "Se ha registrado un nuevo avance en una medida",
                'icono': "chart-line",
                'color': "#28a745",
                'para_admin_sma': True
            }
        )

        # Crear notificación para administradores SMA
        from apps.usuarios.models import Usuario
        admins_sma = Usuario.objects.filter(rol='admin_sma')

        for admin in admins_sma:
            Notificacion.objects.create(
                tipo=tipo,
                usuario=admin,
                titulo=f"Nuevo avance en {instance.medida.codigo}",
                mensaje=f"El organismo {instance.organismo.nombre} ha registrado un avance del {instance.porcentaje_avance}% en la medida {instance.medida.nombre}.",
                medida=instance.medida,
                organismo=instance.organismo,
                enlace=f"/medidas/{instance.medida.id}/"  # URL a la página de detalle de la medida
            )


@receiver(post_save, sender=AsignacionMedida)
def notificar_nueva_asignacion(sender, instance, created, **kwargs):
    """Envía notificaciones cuando se asigna una medida a un organismo"""
    if created:
        # Obtener el tipo de notificación
        tipo, _ = TipoNotificacion.objects.get_or_create(
            codigo="nueva_asignacion",
            defaults={
                'nombre': "Nueva medida asignada",
                'descripcion': "Se ha asignado una nueva medida a tu organismo",
                'icono': "clipboard-check",
                'color': "#007bff",
                'para_organismos': True
            }
        )

        # Crear notificación para usuarios del organismo
        from apps.usuarios.models import Usuario
        usuarios_organismo = Usuario.objects.filter(organismo=instance.organismo)

        for usuario in usuarios_organismo:
            Notificacion.objects.create(
                tipo=tipo,
                usuario=usuario,
                titulo=f"Nueva medida asignada: {instance.medida.codigo}",
                mensaje=f"Se ha asignado a tu organismo la medida '{instance.medida.nombre}'. " +
                        f"Fecha límite: {instance.medida.fecha_termino.strftime('%d/%m/%Y')}",
                medida=instance.medida,
                organismo=instance.organismo,
                enlace=f"/medidas/{instance.medida.id}/"
            )


# Función auxiliar para verificar medidas próximas a vencer
def verificar_medidas_proximas_vencer():
    """Verifica medidas que vencen en los próximos 30 días y envía notificaciones"""
    # Obtener el tipo de notificación
    tipo, _ = TipoNotificacion.objects.get_or_create(
        codigo="medida_proxima_vencer",
        defaults={
            'nombre': "Medida próxima a vencer",
            'descripcion': "Una medida está próxima a alcanzar su fecha límite",
            'icono': "clock",
            'color': "#ffc107",
            'para_organismos': True,
            'para_admin_sma': True
        }
    )

    # Calcular fechas relevantes
    hoy = timezone.now().date()
    en_30_dias = hoy + timedelta(days=30)

    # Buscar medidas que vencen en los próximos 30 días y no están completadas
    medidas_proximas = Medida.objects.filter(
        fecha_termino__gt=hoy,
        fecha_termino__lte=en_30_dias,
        estado__in=['pendiente', 'en_proceso']
    )

    for medida in medidas_proximas:
        # Notificar a los organismos responsables
        for asignacion in medida.asignaciones.all():
            usuarios_organismo = asignacion.organismo.usuarios.all()

            for usuario in usuarios_organismo:
                # Verificar si ya existe una notificación similar no leída
                notif_existente = Notificacion.objects.filter(
                    tipo=tipo,
                    usuario=usuario,
                    medida=medida,
                    leida=False
                ).exists()

                if not notif_existente:
                    dias_restantes = (medida.fecha_termino - hoy).days
                    Notificacion.objects.create(
                        tipo=tipo,
                        usuario=usuario,
                        titulo=f"Medida próxima a vencer: {medida.codigo}",
                        mensaje=f"La medida '{medida.nombre}' vence en {dias_restantes} días. " +
                                f"El avance actual es del {medida.porcentaje_avance}%.",
                        medida=medida,
                        organismo=asignacion.organismo,
                        enlace=f"/medidas/{medida.id}/"
                    )

        # Notificar también a los administradores SMA
        from apps.usuarios.models import Usuario
        admins_sma = Usuario.objects.filter(rol='admin_sma')

        for admin in admins_sma:
            notif_existente = Notificacion.objects.filter(
                tipo=tipo,
                usuario=admin,
                medida=medida,
                leida=False
            ).exists()

            if not notif_existente:
                dias_restantes = (medida.fecha_termino - hoy).days
                Notificacion.objects.create(
                    tipo=tipo,
                    usuario=admin,
                    titulo=f"Medida próxima a vencer: {medida.codigo}",
                    mensaje=f"La medida '{medida.nombre}' vence en {dias_restantes} días. " +
                            f"El avance actual es del {medida.porcentaje_avance}%.",
                    medida=medida,
                    enlace=f"/medidas/{medida.id}/"
                )
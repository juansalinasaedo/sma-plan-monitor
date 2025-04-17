from django.db import models

# apps/notificaciones/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.usuarios.models import Usuario
from apps.organismos.models import Organismo
from apps.medidas.models import Medida


class TipoNotificacion(models.Model):
    """
    Define los diferentes tipos de notificaciones que el sistema puede generar.
    """
    nombre = models.CharField(_("Nombre"), max_length=100)
    descripcion = models.TextField(_("Descripción"))
    codigo = models.CharField(_("Código"), max_length=50, unique=True)
    icono = models.CharField(_("Icono"), max_length=50, blank=True)
    color = models.CharField(_("Color"), max_length=7, blank=True,
                             help_text=_("Código hexadecimal del color, ej: #FF5733"))

    # Define si este tipo de notificación está activo en el sistema
    activo = models.BooleanField(_("Activo"), default=True)

    # Define quiénes pueden recibir este tipo de notificación
    para_superadmin = models.BooleanField(_("Para Super Admin"), default=False)
    para_admin_sma = models.BooleanField(_("Para Admin SMA"), default=False)
    para_organismos = models.BooleanField(_("Para Organismos"), default=False)
    para_ciudadanos = models.BooleanField(_("Para Ciudadanos"), default=False)

    created_at = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Fecha de actualización"), auto_now=True)

    class Meta:
        verbose_name = _("Tipo de Notificación")
        verbose_name_plural = _("Tipos de Notificaciones")
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Notificacion(models.Model):
    """
    Representa una notificación específica enviada a un usuario.
    """
    tipo = models.ForeignKey(
        TipoNotificacion,
        on_delete=models.CASCADE,
        verbose_name=_("Tipo"),
        related_name="notificaciones"
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        verbose_name=_("Usuario"),
        related_name="notificaciones"
    )

    titulo = models.CharField(_("Título"), max_length=200)
    mensaje = models.TextField(_("Mensaje"))
    enlace = models.CharField(_("Enlace"), max_length=255, blank=True,
                              help_text=_("URL a la que dirigir al usuario al hacer clic en la notificación"))

    # Referencias opcionales a otros modelos
    medida = models.ForeignKey(
        Medida,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Medida"),
        related_name="notificaciones"
    )
    organismo = models.ForeignKey(
        Organismo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Organismo"),
        related_name="notificaciones"
    )

    # Estados de la notificación
    fecha_envio = models.DateTimeField(_("Fecha de envío"), auto_now_add=True)
    leida = models.BooleanField(_("Leída"), default=False)
    fecha_lectura = models.DateTimeField(_("Fecha de lectura"), null=True, blank=True)

    # Si se envió por email
    enviada_email = models.BooleanField(_("Enviada por email"), default=False)
    fecha_envio_email = models.DateTimeField(_("Fecha de envío por email"), null=True, blank=True)

    class Meta:
        verbose_name = _("Notificación")
        verbose_name_plural = _("Notificaciones")
        ordering = ['-fecha_envio']

    def __str__(self):
        return f"{self.tipo.nombre} - {self.usuario.username} - {self.fecha_envio}"


class ConfiguracionNotificaciones(models.Model):
    """
    Permite a los usuarios configurar qué notificaciones desean recibir.
    """
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        verbose_name=_("Usuario"),
        related_name="configuracion_notificaciones"
    )

    # Canales de notificación
    recibir_email = models.BooleanField(_("Recibir por email"), default=True)
    recibir_sistema = models.BooleanField(_("Recibir en el sistema"), default=True)

    # Frecuencia para emails resumen
    FRECUENCIA_CHOICES = [
        ('inmediata', _('Inmediata')),
        ('diaria', _('Resumen diario')),
        ('semanal', _('Resumen semanal')),
    ]
    frecuencia_email = models.CharField(_("Frecuencia de emails"), max_length=20,
                                        choices=FRECUENCIA_CHOICES, default='inmediata')

    # Tipos específicos de notificaciones que desea recibir
    tipos_habilitados = models.ManyToManyField(
        TipoNotificacion,
        verbose_name=_("Tipos habilitados"),
        related_name="configuraciones",
        help_text=_("Tipos de notificaciones que el usuario desea recibir")
    )

    created_at = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Fecha de actualización"), auto_now=True)

    class Meta:
        verbose_name = _("Configuración de Notificaciones")
        verbose_name_plural = _("Configuraciones de Notificaciones")

    def __str__(self):
        return f"Configuración de {self.usuario.username}"


class Recordatorio(models.Model):
    """
    Permite programar recordatorios para fechas importantes.
    """
    titulo = models.CharField(_("Título"), max_length=200)
    descripcion = models.TextField(_("Descripción"))

    # A quién se enviará
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        verbose_name=_("Usuario"),
        related_name="recordatorios",
        null=True,
        blank=True
    )
    organismo = models.ForeignKey(
        Organismo,
        on_delete=models.CASCADE,
        verbose_name=_("Organismo"),
        related_name="recordatorios",
        null=True,
        blank=True,
        help_text=_("Si se especifica, el recordatorio se enviará a todos los usuarios de este organismo")
    )

    # Referencias opcionales
    medida = models.ForeignKey(
        Medida,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Medida"),
        related_name="recordatorios"
    )

    # Fechas
    fecha_programada = models.DateTimeField(_("Fecha programada"))
    fecha_enviado = models.DateTimeField(_("Fecha de envío"), null=True, blank=True)

    # Estado
    ESTADO_CHOICES = [
        ('pendiente', _('Pendiente')),
        ('enviado', _('Enviado')),
        ('cancelado', _('Cancelado')),
    ]
    estado = models.CharField(_("Estado"), max_length=20, choices=ESTADO_CHOICES, default='pendiente')

    # Repetición
    REPETICION_CHOICES = [
        ('ninguna', _('No repetir')),
        ('diaria', _('Diariamente')),
        ('semanal', _('Semanalmente')),
        ('mensual', _('Mensualmente')),
        ('anual', _('Anualmente')),
    ]
    repeticion = models.CharField(_("Repetición"), max_length=20, choices=REPETICION_CHOICES, default='ninguna')

    created_by = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name="recordatorios_creados",
        verbose_name=_("Creado por")
    )
    created_at = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Fecha de actualización"), auto_now=True)

    class Meta:
        verbose_name = _("Recordatorio")
        verbose_name_plural = _("Recordatorios")
        ordering = ['fecha_programada']

    def __str__(self):
        return f"{self.titulo} - {self.fecha_programada}"
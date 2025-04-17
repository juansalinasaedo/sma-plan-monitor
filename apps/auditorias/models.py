from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from apps.usuarios.models import Usuario


class Auditoria(models.Model):
    """
    Registro principal de auditoría para todas las acciones realizadas en el sistema.
    """
    ACCIONES = [
        ('creacion', _('Creación')),
        ('modificacion', _('Modificación')),
        ('eliminacion', _('Eliminación')),
        ('login', _('Inicio de sesión')),
        ('logout', _('Cierre de sesión')),
        ('exportacion', _('Exportación de datos')),
        ('importacion', _('Importación de datos')),
        ('descarga', _('Descarga de archivo')),
        ('validacion', _('Validación de datos')),
        ('rechazo', _('Rechazo de datos')),
        ('planificacion', _('Planificación')),
        ('configuracion', _('Configuración del sistema')),
    ]

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Usuario"),
        related_name="auditorias"
    )
    fecha_hora = models.DateTimeField(_("Fecha y hora"), auto_now_add=True)
    accion = models.CharField(_("Acción"), max_length=20, choices=ACCIONES)
    descripcion = models.TextField(_("Descripción"))

    # Para vincular con cualquier modelo
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    objeto_relacionado = GenericForeignKey('content_type', 'object_id')

    # Información adicional
    ip = models.GenericIPAddressField(_("Dirección IP"), blank=True, null=True)
    navegador = models.CharField(_("Navegador"), max_length=255, blank=True)
    datos_adicionales = models.JSONField(_("Datos adicionales"), blank=True, null=True)

    class Meta:
        verbose_name = _("Auditoría")
        verbose_name_plural = _("Auditorías")
        ordering = ['-fecha_hora']

    def __str__(self):
        usuario_str = self.usuario.username if self.usuario else "Sistema"
        return f"{usuario_str} - {self.get_accion_display()} - {self.fecha_hora}"


class CambioDetalle(models.Model):
    """
    Almacena detalles específicos de cambios en campos de modelos.
    """
    auditoria = models.ForeignKey(
        Auditoria,
        on_delete=models.CASCADE,
        related_name="detalles",
        verbose_name=_("Auditoría")
    )

    campo = models.CharField(_("Campo"), max_length=100)
    valor_anterior = models.TextField(_("Valor anterior"), blank=True, null=True)
    valor_nuevo = models.TextField(_("Valor nuevo"), blank=True, null=True)

    class Meta:
        verbose_name = _("Detalle de cambio")
        verbose_name_plural = _("Detalles de cambios")

    def __str__(self):
        return f"{self.campo}: {self.valor_anterior} → {self.valor_nuevo}"


class ConfiguracionAuditoria(models.Model):
    """
    Configuración de qué modelos y acciones se auditan.
    """
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_("Tipo de contenido")
    )

    auditar_creacion = models.BooleanField(_("Auditar creación"), default=True)
    auditar_modificacion = models.BooleanField(_("Auditar modificación"), default=True)
    auditar_eliminacion = models.BooleanField(_("Auditar eliminación"), default=True)

    # Campos específicos a auditar (vacío = todos)
    campos_auditados = models.JSONField(
        _("Campos auditados"),
        blank=True,
        null=True,
        help_text=_("Lista de campos a auditar. Dejar en blanco para auditar todos los campos.")
    )

    activo = models.BooleanField(_("Activo"), default=True)
    created_at = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Fecha de actualización"), auto_now=True)

    class Meta:
        verbose_name = _("Configuración de auditoría")
        verbose_name_plural = _("Configuraciones de auditoría")
        unique_together = ['content_type']

    def __str__(self):
        return f"Auditoría para {self.content_type.app_labeled_name}"

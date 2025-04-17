from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from apps.organismos.models import Organismo


class Usuario(AbstractUser):
    """
    Extiende el modelo de usuario de Django para añadir campos específicos
    para el sistema de monitoreo ambiental.
    """
    ROLES = [
        ('superadmin', _('Super Administrador')),
        ('admin_sma', _('Administrador SMA')),
        ('organismo', _('Usuario de Organismo')),
        ('ciudadano', _('Ciudadano')),
    ]

    organismo = models.ForeignKey(
        Organismo,
        on_delete=models.PROTECT,
        verbose_name=_("Organismo"),
        related_name="usuarios",
        null=True,
        blank=True,
        help_text=_("Organismo al que pertenece el usuario (solo para usuarios de organismos)")
    )

    rol = models.CharField(
        _("Rol"),
        max_length=20,
        choices=ROLES,
        default='ciudadano'
    )

    cargo = models.CharField(_("Cargo"), max_length=100, blank=True)
    telefono = models.CharField(_("Teléfono"), max_length=20, blank=True)

    # Para notificaciones
    recibir_notificaciones_email = models.BooleanField(_("Recibir notificaciones por email"), default=True)
    recibir_notificaciones_sistema = models.BooleanField(_("Recibir notificaciones en el sistema"), default=True)

    # Campos para seguimiento
    created_at = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Fecha de actualización"), auto_now=True)

    class Meta:
        verbose_name = _("Usuario")
        verbose_name_plural = _("Usuarios")

    def __str__(self):
        if self.organismo:
            return f"{self.username} - {self.get_rol_display()} - {self.organismo.nombre}"
        return f"{self.username} - {self.get_rol_display()}"

    @property
    def is_superadmin(self):
        """Verifica si el usuario es superadmin"""
        return self.rol == 'superadmin'

    @property
    def is_admin_sma(self):
        """Verifica si el usuario es admin de SMA"""
        return self.rol == 'admin_sma'

    @property
    def is_organismo(self):
        """Verifica si el usuario pertenece a un organismo"""
        return self.rol == 'organismo'

    @property
    def is_ciudadano(self):
        """Verifica si el usuario es ciudadano"""
        return self.rol == 'ciudadano'


class Perfil(models.Model):
    """
    Modelo para almacenar preferencias y configuraciones adicionales del usuario
    que no son esenciales para la autenticación.
    """
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name="perfil",
        verbose_name=_("Usuario")
    )

    foto = models.ImageField(_("Foto de perfil"), upload_to="perfiles/", null=True, blank=True)
    tema = models.CharField(_("Tema preferido"), max_length=20, default="light", choices=[
        ('light', _('Claro')),
        ('dark', _('Oscuro')),
        ('system', _('Sistema'))
    ])

    ultimo_acceso = models.DateTimeField(_("Último acceso"), null=True, blank=True)
    token_notificaciones = models.CharField(_("Token de notificaciones"), max_length=255, blank=True)

    created_at = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Fecha de actualización"), auto_now=True)

    class Meta:
        verbose_name = _("Perfil")
        verbose_name_plural = _("Perfiles")

    def __str__(self):
        return f"Perfil de {self.usuario.username}"


class HistorialAcceso(models.Model):
    """
    Registra cada acceso de los usuarios al sistema.
    """
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="historial_accesos",
        verbose_name=_("Usuario")
    )

    fecha_hora = models.DateTimeField(_("Fecha y hora"), auto_now_add=True)
    ip = models.GenericIPAddressField(_("Dirección IP"), blank=True, null=True)
    dispositivo = models.CharField(_("Dispositivo"), max_length=255, blank=True)
    navegador = models.CharField(_("Navegador"), max_length=255, blank=True)
    exitoso = models.BooleanField(_("Acceso exitoso"), default=True)

    class Meta:
        verbose_name = _("Historial de acceso")
        verbose_name_plural = _("Historial de accesos")
        ordering = ['-fecha_hora']

    def __str__(self):
        estado = "exitoso" if self.exitoso else "fallido"
        return f"Acceso {estado} de {self.usuario.username} - {self.fecha_hora}"
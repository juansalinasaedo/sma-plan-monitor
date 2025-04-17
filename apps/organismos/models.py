from django.db import models
from django.utils.translation import gettext_lazy as _


class TipoOrganismo(models.Model):
    """
    Modelo para categorizar los tipos de organismos que interactúan con el sistema.
    Ej: Municipalidad, Ministerio, Servicio público, Empresa privada, etc.
    """
    nombre = models.CharField(_("Nombre"), max_length=100)
    descripcion = models.TextField(_("Descripción"), blank=True)
    activo = models.BooleanField(_("Activo"), default=True)

    created_at = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Fecha de actualización"), auto_now=True)

    class Meta:
        verbose_name = _("Tipo de Organismo")
        verbose_name_plural = _("Tipos de Organismos")
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Organismo(models.Model):
    """
    Modelo principal para los organismos que participan en el plan de descontaminación.
    Incluye entidades gubernamentales, municipalidades, empresas, etc.
    """
    nombre = models.CharField(_("Nombre"), max_length=200)
    tipo = models.ForeignKey(
        TipoOrganismo,
        on_delete=models.PROTECT,
        verbose_name=_("Tipo de organismo"),
        related_name="organismos"
    )
    rut = models.CharField(_("RUT"), max_length=12, blank=True)
    direccion = models.CharField(_("Dirección"), max_length=255, blank=True)
    comuna = models.CharField(_("Comuna"), max_length=100, blank=True)
    region = models.CharField(_("Región"), max_length=100, blank=True)
    telefono = models.CharField(_("Teléfono"), max_length=20, blank=True)
    email_contacto = models.EmailField(_("Email de contacto"), blank=True)
    sitio_web = models.URLField(_("Sitio web"), blank=True)
    activo = models.BooleanField(_("Activo"), default=True)

    created_at = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Fecha de actualización"), auto_now=True)

    class Meta:
        verbose_name = _("Organismo")
        verbose_name_plural = _("Organismos")
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class ContactoOrganismo(models.Model):
    """
    Modelo para registrar personas de contacto dentro de cada organismo.
    """
    organismo = models.ForeignKey(
        Organismo,
        on_delete=models.CASCADE,
        verbose_name=_("Organismo"),
        related_name="contactos"
    )
    nombre = models.CharField(_("Nombre"), max_length=100)
    apellido = models.CharField(_("Apellido"), max_length=100)
    cargo = models.CharField(_("Cargo"), max_length=100, blank=True)
    email = models.EmailField(_("Email"))
    telefono = models.CharField(_("Teléfono"), max_length=20, blank=True)
    es_principal = models.BooleanField(_("Contacto principal"), default=False)
    activo = models.BooleanField(_("Activo"), default=True)

    created_at = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Fecha de actualización"), auto_now=True)

    class Meta:
        verbose_name = _("Contacto de Organismo")
        verbose_name_plural = _("Contactos de Organismos")
        ordering = ['organismo', '-es_principal', 'nombre']

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.organismo.nombre}"
# apps/medidas/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.organismos.models import Organismo


class Componente(models.Model):
    """
    Representa un componente o área temática del plan de descontaminación.
    Por ejemplo: Calidad del Aire, Gestión de Residuos, etc.
    """
    nombre = models.CharField(_("Nombre"), max_length=200)
    descripcion = models.TextField(_("Descripción"))
    codigo = models.CharField(_("Código"), max_length=20, blank=True)
    color = models.CharField(_("Color"), max_length=7, blank=True,
                             help_text=_("Código hexadecimal del color, ej: #FF5733"))
    activo = models.BooleanField(_("Activo"), default=True)

    created_at = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Fecha de actualización"), auto_now=True)

    class Meta:
        verbose_name = _("Componente")
        verbose_name_plural = _("Componentes")
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Medida(models.Model):
    """
    Representa una medida específica dentro del plan de descontaminación.
    """
    ESTADO_CHOICES = [
        ('pendiente', _('Pendiente')),
        ('en_proceso', _('En Proceso')),
        ('completada', _('Completada')),
        ('retrasada', _('Retrasada')),
        ('suspendida', _('Suspendida')),
    ]

    PRIORIDAD_CHOICES = [
        ('alta', _('Alta')),
        ('media', _('Media')),
        ('baja', _('Baja')),
    ]
    activo = models.BooleanField(_("Activo"), default=True)
    codigo = models.CharField(_("Código"), max_length=30, unique=True)
    nombre = models.CharField(_("Nombre"), max_length=255)
    descripcion = models.TextField(_("Descripción"))
    componente = models.ForeignKey(
        Componente,
        on_delete=models.CASCADE,
        verbose_name=_("Componente"),
        related_name="medidas"
    )
    fecha_inicio = models.DateField(_("Fecha de inicio"))
    fecha_termino = models.DateField(_("Fecha de término"))
    estado = models.CharField(_("Estado"), max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    prioridad = models.CharField(_("Prioridad"), max_length=10, choices=PRIORIDAD_CHOICES, default='media')
    porcentaje_avance = models.DecimalField(_("Porcentaje de avance"), max_digits=5, decimal_places=2, default=0)
    responsables = models.ManyToManyField(
        Organismo,
        through='AsignacionMedida',
        related_name='medidas_asignadas',
        verbose_name=_("Organismos responsables")
    )

    created_at = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Fecha de actualización"), auto_now=True)

    class Meta:
        verbose_name = _("Medida")
        verbose_name_plural = _("Medidas")
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class AsignacionMedida(models.Model):
    """
    Relación entre una medida y un organismo responsable,
    incluyendo detalles específicos de la responsabilidad.
    """
    medida = models.ForeignKey(
        Medida,
        on_delete=models.CASCADE,
        verbose_name=_("Medida"),
        related_name="asignaciones"
    )
    organismo = models.ForeignKey(
        Organismo,
        on_delete=models.CASCADE,
        verbose_name=_("Organismo"),
        related_name="asignaciones_medidas"
    )
    es_coordinador = models.BooleanField(_("Es coordinador"), default=False,
                                         help_text=_(
                                             "Indica si el organismo es el coordinador principal de esta medida"))
    descripcion_responsabilidad = models.TextField(_("Descripción de responsabilidad"), blank=True)
    fecha_asignacion = models.DateField(_("Fecha de asignación"), auto_now_add=True)

    created_at = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Fecha de actualización"), auto_now=True)

    class Meta:
        verbose_name = _("Asignación de Medida")
        verbose_name_plural = _("Asignaciones de Medidas")
        unique_together = ['medida', 'organismo']

    def __str__(self):
        return f"{self.medida.codigo} - {self.organismo.nombre}"


class RegistroAvance(models.Model):
    """
    Registra los avances periódicos de una medida específica.
    """
    medida = models.ForeignKey(
        Medida,
        on_delete=models.CASCADE,
        verbose_name=_("Medida"),
        related_name="registros_avance"
    )
    organismo = models.ForeignKey(
        Organismo,
        on_delete=models.CASCADE,
        verbose_name=_("Organismo"),
        related_name="registros_avance"
    )
    fecha_registro = models.DateField(_("Fecha de registro"))
    porcentaje_avance = models.DecimalField(_("Porcentaje de avance"), max_digits=5, decimal_places=2)
    descripcion = models.TextField(_("Descripción del avance"))
    evidencia = models.FileField(_("Archivo de evidencia"), upload_to='evidencias/', blank=True, null=True)

    created_at = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Fecha de actualización"), auto_now=True)
    created_by = models.ForeignKey('usuarios.Usuario', on_delete=models.SET_NULL, null=True,
                                   related_name='registros_creados', verbose_name=_("Creado por"))

    class Meta:
        verbose_name = _("Registro de Avance")
        verbose_name_plural = _("Registros de Avance")
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"{self.medida.codigo} - {self.fecha_registro} - {self.porcentaje_avance}%"


class LogMedida(models.Model):
    """
    Registra un historial de cambios en las medidas.
    """
    medida = models.ForeignKey(
        Medida,
        on_delete=models.CASCADE,
        verbose_name=_("Medida"),
        related_name="logs"
    )
    fecha = models.DateTimeField(_("Fecha"), auto_now_add=True)
    accion = models.CharField(_("Acción"), max_length=50)
    descripcion = models.TextField(_("Descripción"))
    usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        related_name='logs_medidas',
        verbose_name=_("Usuario")
    )

    class Meta:
        verbose_name = _("Log de Medida")
        verbose_name_plural = _("Logs de Medidas")
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.medida.codigo} - {self.accion} - {self.fecha}"
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.medidas.models import Componente, Medida
from apps.organismos.models import Organismo
from apps.usuarios.models import Usuario


class TipoReporte(models.Model):
    """
    Define los diferentes tipos de reportes que pueden generarse en el sistema.
    """

    nombre = models.CharField(_("Nombre"), max_length=100)
    descripcion = models.TextField(_("Descripción"))
    slug = models.SlugField(_("Identificador"), unique=True)
    icono = models.CharField(_("Icono"), max_length=50, blank=True)
    activo = models.BooleanField(_("Activo"), default=True)
    publico = models.BooleanField(
        _("Público"),
        default=False,
        help_text=_("Indica si este tipo de reporte es accesible para ciudadanos"),
    )

    created_at = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Fecha de actualización"), auto_now=True)

    class Meta:
        verbose_name = _("Tipo de Reporte")
        verbose_name_plural = _("Tipos de Reportes")
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class ParametroReporte(models.Model):
    """
    Define los parámetros configurables para cada tipo de reporte.
    """

    TIPO_PARAMETRO_CHOICES = [
        ("texto", _("Texto")),
        ("numero", _("Número")),
        ("fecha", _("Fecha")),
        ("seleccion", _("Selección")),
        ("multiple", _("Selección Múltiple")),
        ("booleano", _("Sí/No")),
    ]

    tipo_reporte = models.ForeignKey(
        TipoReporte,
        on_delete=models.CASCADE,
        verbose_name=_("Tipo de Reporte"),
        related_name="parametros",
    )
    nombre = models.CharField(_("Nombre"), max_length=100)
    etiqueta = models.CharField(_("Etiqueta"), max_length=100)
    tipo_parametro = models.CharField(
        _("Tipo de Parámetro"), max_length=20, choices=TIPO_PARAMETRO_CHOICES
    )
    obligatorio = models.BooleanField(_("Obligatorio"), default=False)
    valor_defecto = models.CharField(_("Valor por defecto"), max_length=255, blank=True)
    opciones = models.JSONField(
        _("Opciones"),
        blank=True,
        null=True,
        help_text=_("Opciones para tipos de selección, en formato JSON"),
    )
    orden = models.PositiveSmallIntegerField(_("Orden"), default=0)

    class Meta:
        verbose_name = _("Parámetro de Reporte")
        verbose_name_plural = _("Parámetros de Reportes")
        ordering = ["tipo_reporte", "orden"]
        unique_together = ["tipo_reporte", "nombre"]

    def __str__(self):
        return f"{self.tipo_reporte.nombre} - {self.etiqueta}"


class ReporteGenerado(models.Model):
    """
    Almacena los reportes generados por los usuarios.
    """

    ESTADO_CHOICES = [
        ("pendiente", _("Pendiente")),
        ("generando", _("Generando")),
        ("completado", _("Completado")),
        ("error", _("Error")),
    ]

    tipo_reporte = models.ForeignKey(
        TipoReporte,
        on_delete=models.CASCADE,
        verbose_name=_("Tipo de Reporte"),
        related_name="reportes",
    )
    titulo = models.CharField(_("Título"), max_length=200)
    descripcion = models.TextField(_("Descripción"), blank=True)
    parametros = models.JSONField(_("Parámetros"), blank=True, null=True)

    fecha_solicitud = models.DateTimeField(_("Fecha de solicitud"), auto_now_add=True)
    fecha_generacion = models.DateTimeField(
        _("Fecha de generación"), null=True, blank=True
    )

    estado = models.CharField(
        _("Estado"), max_length=20, choices=ESTADO_CHOICES, default="pendiente"
    )
    mensaje_error = models.TextField(_("Mensaje de error"), blank=True)

    archivo = models.FileField(
        _("Archivo generado"), upload_to="reportes/", null=True, blank=True
    )

    activo = models.BooleanField(_("Activo"), default=True)

    solicitado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name="reportes_solicitados",
        verbose_name=_("Solicitado por"),
    )

    # Filtros aplicados al reporte
    componentes = models.ManyToManyField(
        Componente, blank=True, verbose_name=_("Componentes"), related_name="reportes"
    )
    organismos = models.ManyToManyField(
        Organismo, blank=True, verbose_name=_("Organismos"), related_name="reportes"
    )
    publico = models.BooleanField(
        _("Público"),
        default=False,
        help_text=_("Indica si este reporte es accesible para ciudadanos"),
    )

    created_at = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Fecha de actualización"), auto_now=True)

    class Meta:
        verbose_name = _("Reporte Generado")
        verbose_name_plural = _("Reportes Generados")
        ordering = ["-fecha_solicitud"]

    def __str__(self):
        return f"{self.titulo} ({self.get_estado_display()})"


class Visualizacion(models.Model):
    """
    Define visualizaciones predefinidas para el dashboard.
    """

    TIPO_CHOICES = [
        ("grafico_barras", _("Gráfico de Barras")),
        ("grafico_lineas", _("Gráfico de Líneas")),
        ("grafico_torta", _("Gráfico de Torta")),
        ("tabla", _("Tabla")),
        ("contador", _("Contador")),
        ("mapa", _("Mapa")),
    ]

    nombre = models.CharField(_("Nombre"), max_length=100)
    descripcion = models.TextField(_("Descripción"), blank=True)
    tipo = models.CharField(_("Tipo"), max_length=20, choices=TIPO_CHOICES)
    configuracion = models.JSONField(
        _("Configuración"),
        help_text=_("Configuración de la visualización en formato JSON"),
    )

    activo = models.BooleanField(_("Activo"), default=True)
    publico = models.BooleanField(_("Público"), default=False)
    destacado = models.BooleanField(_("Destacado"), default=False)

    # Filtros predefinidos
    componentes = models.ManyToManyField(
        Componente,
        blank=True,
        verbose_name=_("Componentes"),
        related_name="visualizaciones",
    )
    organismos = models.ManyToManyField(
        Organismo,
        blank=True,
        verbose_name=_("Organismos"),
        related_name="visualizaciones",
    )

    created_at = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Fecha de actualización"), auto_now=True)
    created_by = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name="visualizaciones_creadas",
        verbose_name=_("Creado por"),
    )

    class Meta:
        verbose_name = _("Visualización")
        verbose_name_plural = _("Visualizaciones")
        ordering = ["-destacado", "nombre"]

    def __str__(self):
        return self.nombre

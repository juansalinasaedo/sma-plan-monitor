from django.contrib import admin
from .models import TipoReporte, ParametroReporte, ReporteGenerado, Visualizacion


class ParametroReporteInline(admin.TabularInline):
    model = ParametroReporte
    extra = 1


@admin.register(TipoReporte)
class TipoReporteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'publico', 'activo')
    list_filter = ('publico', 'activo')
    search_fields = ('nombre', 'descripcion', 'slug')
    prepopulated_fields = {'slug': ('nombre',)}
    inlines = [ParametroReporteInline]


@admin.register(ParametroReporte)
class ParametroReporteAdmin(admin.ModelAdmin):
    list_display = ('etiqueta', 'tipo_reporte', 'tipo_parametro', 'obligatorio', 'orden')
    list_filter = ('tipo_reporte', 'tipo_parametro', 'obligatorio')
    search_fields = ('nombre', 'etiqueta', 'tipo_reporte__nombre')


@admin.register(ReporteGenerado)
class ReporteGeneradoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo_reporte', 'estado', 'solicitado_por', 'fecha_solicitud', 'publico')
    list_filter = ('tipo_reporte', 'estado', 'publico')
    search_fields = ('titulo', 'descripcion', 'solicitado_por__username')
    readonly_fields = ('fecha_solicitud', 'fecha_generacion', 'parametros', 'mensaje_error')
    date_hierarchy = 'fecha_solicitud'
    filter_horizontal = ('componentes', 'organismos')


@admin.register(Visualizacion)
class VisualizacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'activo', 'publico', 'destacado', 'created_by')
    list_filter = ('tipo', 'activo', 'publico', 'destacado')
    search_fields = ('nombre', 'descripcion')
    readonly_fields = ('created_by', 'created_at', 'updated_at')
    filter_horizontal = ('componentes', 'organismos')

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
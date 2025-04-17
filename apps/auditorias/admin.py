from django.contrib import admin
from django.utils.html import format_html
from .models import Auditoria, CambioDetalle, ConfiguracionAuditoria


class CambioDetalleInline(admin.TabularInline):
    model = CambioDetalle
    extra = 0
    readonly_fields = ('campo', 'valor_anterior', 'valor_nuevo')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ('usuario_display', 'accion_display', 'objeto_relacionado_display',
                    'fecha_hora', 'ip')
    list_filter = ('accion', 'fecha_hora', 'content_type')
    search_fields = ('descripcion', 'usuario__username', 'ip')
    date_hierarchy = 'fecha_hora'
    readonly_fields = ('usuario', 'fecha_hora', 'accion', 'descripcion', 'content_type',
                       'object_id', 'ip', 'navegador', 'datos_adicionales')
    inlines = [CambioDetalleInline]

    def usuario_display(self, obj):
        if obj.usuario:
            return obj.usuario.username
        return "Sistema"

    usuario_display.short_description = "Usuario"

    def accion_display(self, obj):
        colors = {
            'creacion': 'success',
            'modificacion': 'primary',
            'eliminacion': 'danger',
            'login': 'info',
            'logout': 'secondary',
            'exportacion': 'warning',
            'importacion': 'warning',
            'descarga': 'info',
            'validacion': 'success',
            'rechazo': 'danger',
        }
        color = colors.get(obj.accion, 'secondary')
        return format_html('<span class="badge badge-{}">{}</span>',
                           color, obj.get_accion_display())

    accion_display.short_description = "Acción"

    def objeto_relacionado_display(self, obj):
        if obj.content_type and obj.object_id:
            return f"{obj.content_type.model.capitalize()} (ID: {obj.object_id})"
        return "-"

    objeto_relacionado_display.short_description = "Objeto"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ConfiguracionAuditoria)
class ConfiguracionAuditoriaAdmin(admin.ModelAdmin):
    list_display = ('content_type', 'auditar_creacion', 'auditar_modificacion',
                    'auditar_eliminacion', 'activo')
    list_filter = ('auditar_creacion', 'auditar_modificacion',
                   'auditar_eliminacion', 'activo')
    search_fields = ('content_type__model', 'content_type__app_label')

from django.contrib import admin

# apps/notificaciones/admin.py
from django.contrib import admin
from .models import TipoNotificacion, Notificacion, ConfiguracionNotificaciones, Recordatorio


@admin.register(TipoNotificacion)
class TipoNotificacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'para_superadmin', 'para_admin_sma',
                    'para_organismos', 'para_ciudadanos', 'activo')
    list_filter = ('activo', 'para_superadmin', 'para_admin_sma',
                   'para_organismos', 'para_ciudadanos')
    search_fields = ('nombre', 'descripcion', 'codigo')


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'usuario', 'titulo', 'fecha_envio', 'leida', 'enviada_email')
    list_filter = ('tipo', 'leida', 'enviada_email')
    search_fields = ('titulo', 'mensaje', 'usuario__username', 'tipo__nombre')
    date_hierarchy = 'fecha_envio'
    readonly_fields = ('fecha_envio', 'fecha_lectura', 'fecha_envio_email')


@admin.register(ConfiguracionNotificaciones)
class ConfiguracionNotificacionesAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'recibir_email', 'recibir_sistema', 'frecuencia_email')
    list_filter = ('recibir_email', 'recibir_sistema', 'frecuencia_email')
    search_fields = ('usuario__username',)
    filter_horizontal = ('tipos_habilitados',)


@admin.register(Recordatorio)
class RecordatorioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'organismo', 'fecha_programada',
                    'estado', 'repeticion', 'created_by')
    list_filter = ('estado', 'repeticion')
    search_fields = ('titulo', 'descripcion', 'usuario__username', 'organismo__nombre')
    date_hierarchy = 'fecha_programada'
    readonly_fields = ('created_by', 'fecha_enviado')

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

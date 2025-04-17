from django.contrib import admin
from .models import Medida

# apps/medidas/admin.py
from django.contrib import admin
from .models import Componente, Medida, AsignacionMedida, RegistroAvance

@admin.register(Componente)
class ComponenteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'codigo', 'descripcion')

class AsignacionMedidaInline(admin.TabularInline):
    model = AsignacionMedida
    extra = 1

@admin.register(Medida)
class MedidaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'componente', 'estado', 'prioridad',
                    'fecha_inicio', 'fecha_termino', 'porcentaje_avance')
    list_filter = ('componente', 'estado', 'prioridad')
    search_fields = ('codigo', 'nombre', 'descripcion')
    inlines = [AsignacionMedidaInline]
    date_hierarchy = 'fecha_inicio'

@admin.register(AsignacionMedida)
class AsignacionMedidaAdmin(admin.ModelAdmin):
    list_display = ('medida', 'organismo', 'es_coordinador', 'fecha_asignacion')
    list_filter = ('es_coordinador', 'organismo')
    search_fields = ('medida__codigo', 'medida__nombre', 'organismo__nombre')

@admin.register(RegistroAvance)
class RegistroAvanceAdmin(admin.ModelAdmin):
    list_display = ('medida', 'organismo', 'fecha_registro', 'porcentaje_avance', 'created_by')
    list_filter = ('medida__componente', 'organismo', 'fecha_registro')
    search_fields = ('medida__codigo', 'medida__nombre', 'descripcion')
    date_hierarchy = 'fecha_registro'


from django.contrib import admin
# apps/usuarios/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import Usuario, Perfil, HistorialAcceso


class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = 'Perfil'


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Información personal'), {'fields': ('first_name', 'last_name', 'email', 'telefono', 'cargo')}),
        (_('Asignación'), {'fields': ('organismo', 'rol')}),
        (_('Notificaciones'), {'fields': ('recibir_notificaciones_email', 'recibir_notificaciones_sistema')}),
        (_('Permisos'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Fechas importantes'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'organismo', 'rol'),
        }),
    )

    list_display = ('username', 'email', 'first_name', 'last_name', 'organismo', 'rol', 'is_active')
    list_filter = ('is_active', 'rol', 'organismo')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    inlines = [PerfilInline]


@admin.register(HistorialAcceso)
class HistorialAccesoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fecha_hora', 'ip', 'dispositivo', 'navegador', 'exitoso')
    list_filter = ('exitoso', 'fecha_hora')
    search_fields = ('usuario__username', 'ip', 'dispositivo')
    date_hierarchy = 'fecha_hora'
    readonly_fields = ('usuario', 'fecha_hora', 'ip', 'dispositivo', 'navegador', 'exitoso')




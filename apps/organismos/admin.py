from django.contrib import admin
from .models import TipoOrganismo, Organismo, ContactoOrganismo

@admin.register(TipoOrganismo)
class TipoOrganismoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'activo')
    list_filter = ('activo',)
    search_fields = ('nombre', 'descripcion')


class ContactoOrganismoInline(admin.TabularInline):
    model = ContactoOrganismo
    extra = 1


@admin.register(Organismo)
class OrganismoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'comuna', 'email_contacto', 'activo')
    list_filter = ('tipo', 'region', 'comuna', 'activo')
    search_fields = ('nombre', 'rut', 'email_contacto')
    inlines = [ContactoOrganismoInline]

    def save_model(self, request, obj, form, change):
        obj._audit_user = request.user
        obj._audit_request = request
        super().save_model(request, obj, form, change)


@admin.register(ContactoOrganismo)
class ContactoOrganismoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'organismo', 'cargo', 'email', 'es_principal', 'activo')
    list_filter = ('organismo', 'es_principal', 'activo')
    search_fields = ('nombre', 'apellido', 'email', 'organismo__nombre')
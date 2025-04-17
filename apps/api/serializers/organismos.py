from rest_framework import serializers
from apps.organismos.models import Organismo, TipoOrganismo, ContactoOrganismo


class TipoOrganismoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoOrganismo
        fields = ['id', 'nombre', 'descripcion']


class ContactoOrganismoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactoOrganismo
        fields = ['id', 'nombre', 'apellido', 'cargo', 'email', 'telefono', 'es_principal']


class OrganismoSimpleSerializer(serializers.ModelSerializer):
    """Versión simple de organismos"""

    class Meta:
        model = Organismo
        fields = ['id', 'nombre']


class OrganismoDetailSerializer(serializers.ModelSerializer):
    """Versión completa del organismo con toda la información"""
    tipo = TipoOrganismoSerializer(read_only=True)
    contactos = ContactoOrganismoSerializer(many=True, read_only=True)

    class Meta:
        model = Organismo
        fields = ['id', 'nombre', 'tipo', 'rut', 'direccion', 'comuna', 'region',
                  'telefono', 'email_contacto', 'sitio_web', 'contactos']
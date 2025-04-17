from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from apps.organismos.models import Organismo, TipoOrganismo
from ..serializers.organismos import (
    OrganismoDetailSerializer,
    OrganismoSimpleSerializer,
    TipoOrganismoSerializer
)
from apps.organismos.serializers import OrganismoSerializer
from ..permissions import IsPublicEndpoint, IsAdminSMA, IsSuperAdmin
from rest_framework import status
from rest_framework.response import Response


@extend_schema_view(
    list=extend_schema(description="Listar todos los tipos de organismos"),
    retrieve=extend_schema(description="Obtener un tipo de organismo específico")
)
class TipoOrganismoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint para consultar tipos de organismos.
    """
    queryset = TipoOrganismo.objects.filter(activo=True)
    serializer_class = TipoOrganismoSerializer
    permission_classes = [IsPublicEndpoint]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['nombre']


@extend_schema_view(
    list=extend_schema(description="Listar todos los organismos"),
    retrieve=extend_schema(description="Obtener un organismo específico"),
    create=extend_schema(description="Crear un nuevo organismo", request=OrganismoSerializer, responses={201: OrganismoDetailSerializer}),
    update=extend_schema(description="Actualizar un organismo existente"),
    partial_update=extend_schema(description="Actualizar parcialmente un organismo"),
    destroy=extend_schema(description="Eliminar un organismo")
)
class OrganismoViewSet(viewsets.ModelViewSet):
    """
    API endpoint para consultar y gestionar organismos.
    """
    queryset = Organismo.objects.filter(activo=True)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tipo', 'comuna', 'region']
    search_fields = ['nombre', 'rut', 'email_contacto']

    def get_serializer_class(self):
        if self.action == 'list':
            return OrganismoSimpleSerializer
        elif self.action == 'create':
            return OrganismoSerializer
        return OrganismoDetailSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsPublicEndpoint]
        else:
            permission_classes = [IsSuperAdmin | IsAdminSMA]
        return [permission() for permission in permission_classes]
    
    def destroy(self, request, *args, **kwargs):
        """Desactivar un Organismo: Cambiar el estado de un organismo a Inactivo en lugar de borrar."""
        instance = self.get_object()
        instance.activo = False
        instance.save()
        
        return Response({"message":"Organismo desactivado con éxito."},
                        status=status.HTTP_204_NO_CONTENT)
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view
from django_filters.rest_framework import DjangoFilterBackend

from apps.reportes.models import TipoReporte, ReporteGenerado, Visualizacion
from ..serializers.reportes import (
    TipoReporteSerializer,
    ReporteGeneradoSerializer,
    ReporteGeneradoCreateSerializer,
    VisualizacionSerializer
)
from ..permissions import IsPublicEndpoint, IsAdminSMA, IsSuperAdmin


@extend_schema_view(
    list=extend_schema(description="Listar todos los tipos de reporte disponibles"),
    retrieve=extend_schema(description="Obtener un tipo de reporte específico")
)
class TipoReporteViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint para consultar tipos de reporte disponibles.
    """
    queryset = TipoReporte.objects.filter(activo=True)
    serializer_class = TipoReporteSerializer
    permission_classes = [IsPublicEndpoint]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['publico']


@extend_schema_view(
    list=extend_schema(description="Listar todos los reportes generados"),
    retrieve=extend_schema(description="Obtener un reporte generado específico"),
    create=extend_schema(description="Solicitar la generación de un nuevo reporte"),
)
class ReporteGeneradoViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar reportes generados.
    """
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tipo_reporte', 'estado', 'publico']

    def get_queryset(self):
        user = self.request.user

        # Si es administrador, ve todos los reportes
        if user.is_authenticated and (user.is_superadmin or user.is_admin_sma):
            return ReporteGenerado.objects.all()

        # Si está autenticado, ve reportes públicos o propios
        if user.is_authenticated:
            return ReporteGenerado.objects.filter(
                publico=True
            ) | ReporteGenerado.objects.filter(
                solicitado_por=user
            )

        # Si no está autenticado, solo ve reportes públicos
        return ReporteGenerado.objects.filter(publico=True)

    def get_serializer_class(self):
        if self.action == 'create':
            return ReporteGeneradoCreateSerializer
        return ReporteGeneradoSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsPublicEndpoint]
        else:
            permission_classes = [IsAdminSMA | IsSuperAdmin]
        return [permission() for permission in permission_classes]
    
    def destroy(self, request, *args, **kwargs):
        """Desactivar un Reporte: Cambiar el estado de un reporte a Inactivo en lugar de borrar."""
        instance = self.get_object()
        instance.activo = False
        instance.save()
        
        return Response({"message":"Reporte desactivado con éxito."},
                        status=status.HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        serializer.save(
            solicitado_por=self.request.user,
            estado='pendiente'
        )

    @extend_schema(
        description="Descargar un reporte generado"
    )
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """
        Descargar un reporte generado.
        """
        reporte = self.get_object()

        # Verificar que el reporte esté completado
        if reporte.estado != 'completado':
            return Response(
                {"detail": "El reporte aún no está listo para descarga"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar que exista el archivo
        if not reporte.archivo:
            return Response(
                {"detail": "El reporte no tiene un archivo asociado"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Incrementar contador de descargas
        reporte.contador_descargas = (reporte.contador_descargas or 0) + 1
        reporte.save(update_fields=['contador_descargas'])

        # Redireccionar a la URL del archivo
        return Response({"file_url": reporte.archivo.url})
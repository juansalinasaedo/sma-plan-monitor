from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample
)

from ..filters import MedidaFilter, RegistroAvanceFilter
from apps.medidas.models import Componente, Medida, RegistroAvance, LogMedida
from ..serializers.medidas import (
    ComponenteSerializer,
    MedidaListSerializer,
    MedidaDetailSerializer,
    RegistroAvanceSerializer,
    RegistroAvanceDetailSerializer,
)
from ..permissions import (
    IsPublicEndpoint,
    IsAdminSMA,
    IsSuperAdmin,
    IsOrganismoMember,
    IsOrganismoOwner,
)
from apps.medidas.serializers import MedidaSerializer

from ..renderers import MedidaCSVRenderer, RegistroAvanceCSVRenderer

# views.py
from rest_framework.decorators import api_view

@api_view(['GET'])
def debug_auth(request):
    return Response({
        'authenticated': request.user.is_authenticated,
        'user': str(request.user),
        'auth_header': request.META.get('HTTP_AUTHORIZATION')
    })

@extend_schema_view(
    list=extend_schema(description="Listar todos los componentes del plan"),
    retrieve=extend_schema(description="Obtener un componente específico"),
)
class ComponenteViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint para consultar componentes del plan.
    """

    queryset = Componente.objects.filter(activo=True)
    serializer_class = ComponenteSerializer
    permission_classes = [IsPublicEndpoint]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["nombre", "codigo"]


@extend_schema_view(
    list=extend_schema(description="Listar todas las medidas"),
    retrieve=extend_schema(description="Obtener una medida específica"),
    create=extend_schema(
        description="Crear una nueva medida",
        request=MedidaSerializer,
        responses={201: MedidaDetailSerializer},
    ),
    update=extend_schema(description="Actualizar una medida existente"),
    partial_update=extend_schema(description="Actualizar parcialmente una medida"),
    destroy=extend_schema(description="Eliminar una medida"),
    registrar_avance=extend_schema(
        description="Registrar un nuevo avance para esta medida",
        request=RegistroAvanceSerializer,
        responses={
            201: RegistroAvanceSerializer,
            403: OpenApiResponse(
                description="El organismo del usuario no está asignado a esta medida"
            ),
            400: OpenApiResponse(description="Datos inválidos"),
        },
    ),
)


@extend_schema_view(
    list=extend_schema(
        description="Obtiene la lista de medidas con posibilidad de filtrado.",
        parameters=[
            OpenApiParameter(
                name="codigo_contains",
                description="Filtrar por código (búsqueda parcial)",
                required=False,
                type=str
            ),
            OpenApiParameter(
                name="avance_min",
                description="Porcentaje mínimo de avance",
                required=False,
                type=float
            ),
            OpenApiParameter(
                name="retrasada",
                description="Filtrar medidas retrasadas (true/false)",
                required=False,
                type=bool
            ),
        ],
        examples=[
            OpenApiExample(
                'Ejemplo de respuesta',
                value=[
                    {
                        "id": 1,
                        "codigo": "MED-001",
                        "nombre": "Instalación de red de monitoreo",
                        "componente_nombre": "Calidad del Aire",
                        "estado": "en_proceso",
                        "porcentaje_avance": 65.0,
                        "fecha_inicio": "2025-01-01",
                        "fecha_termino": "2025-12-31"
                    }
                ]
            )
        ]
    ),
    retrieve=extend_schema(
        description="Obtiene el detalle de una medida específica por ID.",
        examples=[
            OpenApiExample(
                'Ejemplo de respuesta detallada',
                value={
                    "id": 1,
                    "codigo": "MED-001",
                    "nombre": "Instalación de red de monitoreo",
                    "descripcion": "Instalación de una red de monitoreo de calidad del aire...",
                    "componente": 1,
                    "componente_nombre": "Calidad del Aire",
                    "fecha_inicio": "2025-01-01",
                    "fecha_termino": "2025-12-31",
                    "estado": "en_proceso",
                    "prioridad": "alta",
                    "porcentaje_avance": 65.0,
                    "asignaciones": [
                        {
                            "id": 1,
                            "organismo": 1,
                            "organismo_nombre": "Ministerio del Medio Ambiente",
                            "es_coordinador": True,
                            "descripcion_responsabilidad": "Coordinación general del proyecto"
                        }
                    ],
                    "registros_recientes": [
                        {
                            "id": 1,
                            "fecha_registro": "2025-03-15",
                            "porcentaje_avance": 65.0,
                            "descripcion": "Se han instalado 6 de las 10 estaciones planificadas",
                            "organismo_nombre": "Ministerio del Medio Ambiente"
                        }
                    ]
                }
            )
        ]
    )
)

class MedidaViewSet(viewsets.ModelViewSet):
    """
    API endpoint para consultar y gestionar medidas.
    """
    authentication_classes = [TokenAuthentication]
    queryset = Medida.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["componente", "estado", "prioridad"]
    search_fields = ["codigo", "nombre", "descripcion"]
    filterset_class = MedidaFilter
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer, MedidaCSVRenderer]

    def get_queryset(self):
        user = self.request.user

        # Si es administrador, ve todas las medidas
        if user.is_authenticated and (user.is_superadmin or user.is_admin_sma):
            return Medida.objects.all()

        # Si es usuario de organismo, solo ve sus medidas asignadas
        if user.is_authenticated and user.is_organismo:
            return Medida.objects.filter(responsables=user.organismo)

        # Para usuarios no autenticados o ciudadanos
        return Medida.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return MedidaListSerializer
        elif self.action == "create":
            return MedidaSerializer
        elif self.action == "registrar_avance":
            return RegistroAvanceSerializer
        return MedidaDetailSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsPublicEndpoint]
        elif self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsSuperAdmin | IsAdminSMA]
        else:
            permission_classes = [IsPublicEndpoint]
        return [permission() for permission in permission_classes]

    def destroy(self, instance, *args, **kwargs):
        """Desactivar una Medida: Cambiar el estado de una medida a Inactivo en lugar de borrar."""
        instance = self.get_object()
        instance.activo = False
        instance.save()

        # Log the delete action
        LogMedida.objects.create(
            usuario=self.request.user, medida=instance, accion="eliminar"
        )
        return Response(
            {"message": "Medida deactivada en lugar de eliminar."},
            status=status.HTTP_204_NO_CONTENT,
        )

    @extend_schema(
        description="Obtener los avances de una medida específica",
        responses={200: RegistroAvanceSerializer(many=True)},
    )
    @action(detail=True, methods=["get"])
    def avances(self, request, pk=None):
        """
        Obtener los avances de una medida específica.
        """
        medida = self.get_object()
        avances = RegistroAvance.objects.filter(medida=medida)
        serializer = RegistroAvanceSerializer(avances, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsOrganismoMember])
    def registrar_avance(self, request, pk=None):
        """
        Registrar un nuevo avance para esta medida.
        """
        medida = self.get_object()

        # Verificar que el organismo del usuario esté asignado a esta medida
        # TODO: Revisar porque esta tomando el usuario de django admin al utilizar swagger.
        # Esto solo ocurre cuando estas logueado en Django admin...
        user = request.user
        if not medida.responsables.filter(id=user.organismo_id).exists():
            return Response(
                {"detail": "Tu organismo no está asignado a esta medida"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Crear el registro de avance
        serializer = RegistroAvanceSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            serializer.save(medida=medida, organismo=user.organismo, created_by=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(description="Listar todos los registros de avance"),
    retrieve=extend_schema(description="Obtener un registro de avance específico"),
    create=extend_schema(description="Crear un nuevo registro de avance"),
    update=extend_schema(description="Actualizar un registro de avance existente"),
    partial_update=extend_schema(
        description="Actualizar parcialmente un registro de avance"
    ),
    destroy=extend_schema(description="Eliminar un registro de avance"),
)
class RegistroAvanceViewSet(viewsets.ModelViewSet):
    """
    API endpoint para consultar y gestionar registros de avance.
    """

    queryset = RegistroAvance.objects.all()
    serializer_class = RegistroAvanceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["medida", "organismo", "fecha_registro"]
    filterset_class = RegistroAvanceFilter
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer, RegistroAvanceCSVRenderer]

    def get_queryset(self):
        user = self.request.user

        # Si es administrador, ve todos los registros
        if user.is_authenticated and (user.is_superadmin or user.is_admin_sma):
            return RegistroAvance.objects.all()

        # Si es usuario de organismo, solo ve sus propios registros
        if user.is_authenticated and user.is_organismo:
            return RegistroAvance.objects.filter(organismo=user.organismo)

        # Para usuarios no autenticados, no ver nada
        return RegistroAvance.objects.none()

    def get_serializer_class(self):
        if self.action == "create":
            return RegistroAvanceDetailSerializer
        return RegistroAvanceDetailSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [IsPublicEndpoint]
        elif self.action in ["create"]:
            permission_classes = [IsOrganismoMember]
        elif self.action in ["update", "partial_update"]:
            permission_classes = [IsOrganismoOwner | IsAdminSMA | IsSuperAdmin]
        elif self.action in ["destroy"]:
            permission_classes = [IsSuperAdmin | IsAdminSMA]
        else:
            permission_classes = [IsPublicEndpoint]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        # Verificar si se proporcionó una medida
        medida_id = self.request.data.get("medida")
        if not medida_id:
            from rest_framework.exceptions import ValidationError

            raise ValidationError({"medida": "Este campo es obligatorio"})

        # Verificar que la medida exista
        try:
            medida = Medida.objects.get(pk=medida_id)
        except Medida.DoesNotExist:
            from rest_framework.exceptions import ValidationError

            raise ValidationError({"medida": "Medida no encontrada"})

        # Guardar con todos los campos necesarios
        serializer.save(
            created_by=self.request.user,
            organismo=self.request.user.organismo,
            medida=medida,
        )

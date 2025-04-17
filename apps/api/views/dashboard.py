from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Avg, Count, Sum
from drf_spectacular.utils import extend_schema

from apps.medidas.models import Medida, Componente, RegistroAvance
from apps.organismos.models import Organismo
from ..permissions import IsPublicEndpoint


class DashboardView(APIView):
    """
    API endpoint para obtener datos resumidos para el dashboard.
    """
    permission_classes = [IsPublicEndpoint]

    @extend_schema(
        description="Obtener datos resumidos para el dashboard",
        responses={200: {
            "type": "object",
            "properties": {
                "resumen": {
                    "type": "object",
                    "properties": {
                        "total_medidas": {"type": "integer"},
                        "total_componentes": {"type": "integer"},
                        "total_organismos": {"type": "integer"},
                        "avance_global": {"type": "number", "format": "float"}
                    }
                },
                "avance_componentes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "nombre": {"type": "string"},
                            "codigo": {"type": "string"},
                            "color": {"type": "string"},
                            "total_medidas": {"type": "integer"},
                            "avance_promedio": {"type": "number", "format": "float"}
                        }
                    }
                },
                "estado_medidas": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "estado": {"type": "string"},
                            "cantidad": {"type": "integer"}
                        }
                    }
                },
                "medidas_recientes": {
                    "type": "array",
                    "items": {
                        "type": "object"
                    }
                },
                "avances_recientes": {
                    "type": "array",
                    "items": {
                        "type": "object"
                    }
                }
            }
        }}
    )
    def get(self, request):
        # Resumen general
        total_medidas = Medida.objects.count()
        total_componentes = Componente.objects.filter(activo=True).count()
        total_organismos = Organismo.objects.filter(activo=True).count()

        # Avance global
        avance_global = Medida.objects.aggregate(
            promedio=Avg('porcentaje_avance')
        )['promedio'] or 0

        # Avance por componente
        avance_componentes = Componente.objects.filter(activo=True).annotate(
            total_medidas=Count('medidas'),
            avance_promedio=Avg('medidas__porcentaje_avance')
        ).values('id', 'nombre', 'codigo', 'color', 'total_medidas', 'avance_promedio')

        # Estado de las medidas
        estado_medidas = Medida.objects.values('estado').annotate(
            cantidad=Count('id')
        ).order_by('estado')

        # Medidas recientes
        medidas_recientes = Medida.objects.order_by('-updated_at')[:5].values(
            'id', 'codigo', 'nombre', 'estado', 'porcentaje_avance', 'updated_at'
        )

        # Avances recientes
        avances_recientes = RegistroAvance.objects.order_by('-fecha_registro')[:5].values(
            'id', 'medida__codigo', 'medida__nombre', 'organismo__nombre',
            'fecha_registro', 'porcentaje_avance'
        )

        return Response({
            'resumen': {
                'total_medidas': total_medidas,
                'total_componentes': total_componentes,
                'total_organismos': total_organismos,
                'avance_global': avance_global,
            },
            'avance_componentes': list(avance_componentes),
            'estado_medidas': list(estado_medidas),
            'medidas_recientes': list(medidas_recientes),
            'avances_recientes': list(avances_recientes),
        })
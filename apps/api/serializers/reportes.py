from rest_framework import serializers
from apps.reportes.models import TipoReporte, ReporteGenerado, Visualizacion
from .medidas import ComponenteSerializer
from .organismos import OrganismoSimpleSerializer


class TipoReporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoReporte
        fields = ['id', 'nombre', 'descripcion', 'slug', 'publico']


class ReporteGeneradoSerializer(serializers.ModelSerializer):
    tipo_reporte = TipoReporteSerializer(read_only=True)
    solicitado_por = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ReporteGenerado
        fields = [
            'id', 'titulo', 'descripcion', 'tipo_reporte', 'parametros',
            'fecha_solicitud', 'fecha_generacion', 'estado', 'archivo',
            'solicitado_por', 'publico'
        ]
        read_only_fields = ['fecha_solicitud', 'fecha_generacion', 'estado', 'parametros']


class ReporteGeneradoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReporteGenerado
        fields = [
            'titulo', 'descripcion', 'tipo_reporte', 'parametros',
            'componentes', 'organismos', 'publico'
        ]

    def validate(self, data):
        # Validar que los parámetros son correctos para el tipo de reporte
        tipo_reporte = data.get('tipo_reporte')
        parametros = data.get('parametros', {})

        if tipo_reporte:
            # Obtener parámetros requeridos para este tipo de reporte
            param_obligatorios = list(tipo_reporte.parametros.filter(
                obligatorio=True
            ).values_list('nombre', flat=True))

            # Verificar que todos los parámetros obligatorios estén presentes
            for param in param_obligatorios:
                if param not in parametros:
                    raise serializers.ValidationError({
                        'parametros': f"Falta el parámetro obligatorio '{param}'"
                    })

        return data


class VisualizacionSerializer(serializers.ModelSerializer):
    componentes = ComponenteSerializer(many=True, read_only=True)
    organismos = OrganismoSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Visualizacion
        fields = [
            'id', 'nombre', 'descripcion', 'tipo', 'configuracion',
            'componentes', 'organismos', 'publico', 'destacado'
        ]
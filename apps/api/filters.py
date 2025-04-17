import django_filters
from django.db.models import Q
from apps.medidas.models import Medida, RegistroAvance
from apps.organismos.models import Organismo


class MedidaFilter(django_filters.FilterSet):
    """Filtros avanzados para las medidas"""
    codigo_contains = django_filters.CharFilter(field_name='codigo', lookup_expr='icontains')
    nombre_contains = django_filters.CharFilter(field_name='nombre', lookup_expr='icontains')
    avance_min = django_filters.NumberFilter(field_name='porcentaje_avance', lookup_expr='gte')
    avance_max = django_filters.NumberFilter(field_name='porcentaje_avance', lookup_expr='lte')
    fecha_inicio_desde = django_filters.DateFilter(field_name='fecha_inicio', lookup_expr='gte')
    fecha_inicio_hasta = django_filters.DateFilter(field_name='fecha_inicio', lookup_expr='lte')
    fecha_termino_desde = django_filters.DateFilter(field_name='fecha_termino', lookup_expr='gte')
    fecha_termino_hasta = django_filters.DateFilter(field_name='fecha_termino', lookup_expr='lte')
    organismo = django_filters.ModelChoiceFilter(
        field_name='responsables',
        queryset=Organismo.objects.filter(activo=True)
    )
    retrasada = django_filters.BooleanFilter(method='filter_retrasada')

    def filter_retrasada(self, queryset, name, value):
        from django.utils import timezone
        today = timezone.now().date()
        if value:  # Si queremos medidas retrasadas
            return queryset.filter(
                Q(fecha_termino__lt=today) &
                ~Q(estado='completada') &
                ~Q(estado='suspendida')
            )
        return queryset

    class Meta:
        model = Medida
        fields = {
            'componente': ['exact'],
            'estado': ['exact', 'in'],
            'prioridad': ['exact', 'in'],
        }


class RegistroAvanceFilter(django_filters.FilterSet):
    """Filtros avanzados para los registros de avance"""
    fecha_desde = django_filters.DateFilter(field_name='fecha_registro', lookup_expr='gte')
    fecha_hasta = django_filters.DateFilter(field_name='fecha_registro', lookup_expr='lte')
    avance_min = django_filters.NumberFilter(field_name='porcentaje_avance', lookup_expr='gte')
    avance_max = django_filters.NumberFilter(field_name='porcentaje_avance', lookup_expr='lte')
    organismo_nombre = django_filters.CharFilter(field_name='organismo__nombre', lookup_expr='icontains')

    class Meta:
        model = RegistroAvance
        fields = {
            'medida': ['exact'],
            'organismo': ['exact'],
        }


# apps/publico/views.py
from django.shortcuts import render
from django.db.models import Avg, Count
from apps.medidas.models import Componente, Medida


def inicio_portal(request):
    # Obtener datos resumidos para el portal público
    total_medidas = Medida.objects.count()
    avance_global = Medida.objects.aggregate(
        promedio=Avg('porcentaje_avance')
    )['promedio'] or 0

    # Avance por componente
    componentes = Componente.objects.filter(activo=True).annotate(
        total_medidas=Count('medidas'),
        avance_promedio=Avg('medidas__porcentaje_avance')
    )

    # Estado de las medidas
    estados = Medida.objects.values('estado').annotate(
        total=Count('id')
    ).order_by('estado')

    return render(request, 'publico/inicio.html', {
        'total_medidas': total_medidas,
        'avance_global': avance_global,
        'componentes': componentes,
        'estados': estados,
    })
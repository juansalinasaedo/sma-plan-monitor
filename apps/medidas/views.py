from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Medida, LogMedida
from .serializers import MedidaSerializer

from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Sum, Q
from django.utils import timezone
from datetime import timedelta

from .models import Componente, Medida, RegistroAvance
from apps.organismos.models import Organismo

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .forms import RegistroAvanceForm
from .models import Medida


# Create your views here.
class MedidaViewSet(viewsets.ModelViewSet):
    # TODO: we should modify this .all to follow best practices
    queryset = Medida.objects.filter(activo=True)
    serializer_class = MedidaSerializer
    #permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        medida = serializer.save(usuario=self.request.user)
        LogMedida.objects.create(usuario=self.request.user, medida=medida, accion="crear")
        
    def perform_update(self, serializer):
        medida = serializer.save()
        LogMedida.objects.create(usuario=self.request.user, medida=medida, accion="actualizar")
        
    def destroy(self, instance, *args, **kwargs):
        """Soft delete: instead of deleting, set activo=False"""
        instance = self.get_object()
        instance.activo = False
        instance.save()
        
        # Log the delete action
        LogMedida.objects.create(usuario=self.request.user, medida=instance, accion="eliminar")
        return Response({"message": "Medida archived instead of deleted"}, status=status.HTTP_204_NO_CONTENT)




@login_required
def dashboard_sma(request):
    # Resumen general
    total_medidas = Medida.objects.count()
    total_completadas = Medida.objects.filter(estado='completada').count()
    total_en_proceso = Medida.objects.filter(estado='en_proceso').count()
    total_retrasadas = Medida.objects.filter(estado='retrasada').count()

    # Avance global
    avance_global = Medida.objects.aggregate(
        promedio=Avg('porcentaje_avance')
    )['promedio'] or 0

    # Avance por componente
    componentes = Componente.objects.filter(activo=True).annotate(
        total_medidas=Count('medidas'),
        avance_promedio=Avg('medidas__porcentaje_avance')
    )

    # Organismos con más medidas asignadas
    organismos_top = Organismo.objects.annotate(
        total_medidas=Count('medidas_asignadas')
    ).order_by('-total_medidas')[:5]

    # Avances recientes
    avances_recientes = RegistroAvance.objects.select_related(
        'medida', 'organismo', 'created_by'
    ).order_by('-fecha_registro')[:10]

    # Medidas próximas a vencer
    hoy = timezone.now().date()
    proximo_mes = hoy + timedelta(days=30)
    medidas_proximas = Medida.objects.filter(
        fecha_termino__gte=hoy,
        fecha_termino__lte=proximo_mes,
        estado__in=['pendiente', 'en_proceso']
    ).order_by('fecha_termino')

    context = {
        'total_medidas': total_medidas,
        'total_completadas': total_completadas,
        'total_en_proceso': total_en_proceso,
        'total_retrasadas': total_retrasadas,
        'avance_global': avance_global,
        'componentes': componentes,
        'organismos_top': organismos_top,
        'avances_recientes': avances_recientes,
        'medidas_proximas': medidas_proximas,
    }

    return render(request, 'medidas/dashboard_sma.html', context)


@login_required
def registrar_avance(request, medida_id=None):
    # Verificar que el usuario pertenezca a un organismo
    if not hasattr(request.user, 'organismo') or not request.user.organismo:
        messages.error(request, "No tienes un organismo asignado para registrar avances.")
        return redirect('dashboard_organismo')

    organismo = request.user.organismo

    # Si se proporciona un ID de medida, pre-seleccionarla
    initial = {}
    if medida_id:
        medida = get_object_or_404(
            Medida,
            id=medida_id,
            responsables=organismo
        )
        initial['medida'] = medida

    if request.method == 'POST':
        form = RegistroAvanceForm(request.POST, request.FILES, organismo=organismo)
        if form.is_valid():
            avance = form.save(commit=False)
            avance.organismo = organismo
            avance.created_by = request.user
            avance.save()

            # Actualizar el porcentaje de avance de la medida
            medida = avance.medida
            medida.porcentaje_avance = avance.porcentaje_avance
            medida.save()

            messages.success(request, "Avance registrado correctamente.")
            return redirect('detalle_medida', medida_id=medida.id)
    else:
        form = RegistroAvanceForm(initial=initial, organismo=organismo)

    return render(request, 'medidas/registrar_avance.html', {
        'form': form,
        'medida_id': medida_id
    })
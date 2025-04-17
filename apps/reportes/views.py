from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from django.utils import timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

from apps.medidas.models import Medida, Componente, RegistroAvance


@login_required
def reporte_avance_global(request):
    """Vista para generar reporte de avance global del plan"""
    # Obtener parámetros del reporte
    formato = request.GET.get('formato', 'web')  # web, pdf, excel

    # Calcular datos para el reporte
    total_medidas = Medida.objects.count()
    avance_global = Medida.objects.aggregate(promedio=Avg('porcentaje_avance'))['promedio'] or 0

    # Avance por componente
    componentes = Componente.objects.annotate(
        total_medidas=Count('medidas'),
        avance=Avg('medidas__porcentaje_avance')
    ).order_by('nombre')

    # Avance por estado
    estados = Medida.objects.values('estado').annotate(
        total=Count('id'),
        avance_promedio=Avg('porcentaje_avance')
    ).order_by('estado')

    # Si el formato es PDF, generar el PDF
    if formato == 'pdf':
        # Crear el documento PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="reporte_avance_global.pdf"'

        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []

        # Estilos
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        subtitle_style = styles['Heading2']
        normal_style = styles['Normal']

        # Título del reporte
        elements.append(Paragraph("Reporte de Avance Global", title_style))
        elements.append(Paragraph(f"Fecha: {timezone.now().strftime('%d/%m/%Y')}", normal_style))
        elements.append(Spacer(1, 0.5 * inch))

        # Resumen general
        elements.append(Paragraph("Resumen General", subtitle_style))
        data = [
            ["Total de Medidas", str(total_medidas)],
            ["Avance Global", f"{avance_global:.1f}%"]
        ]
        t = Table(data, colWidths=[3 * inch, 1.5 * inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.3 * inch))

        # Avance por componente
        elements.append(Paragraph("Avance por Componente", subtitle_style))
        data = [["Componente", "Total Medidas", "Avance"]]
        for comp in componentes:
            data.append([
                comp.nombre,
                str(comp.total_medidas),
                f"{comp.avance or 0:.1f}%"
            ])
        t = Table(data, colWidths=[3 * inch, 1.5 * inch, 1 * inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.3 * inch))

        # Avance por estado
        elements.append(Paragraph("Estado de las Medidas", subtitle_style))
        data = [["Estado", "Total", "Avance Promedio"]]
        for est in estados:
            data.append([
                est['estado'].replace('_', ' ').title(),
                str(est['total']),
                f"{est['avance_promedio'] or 0:.1f}%"
            ])
        t = Table(data, colWidths=[2 * inch, 1.5 * inch, 2 * inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t)

        # Construir el PDF
        doc.build(elements)
        return response

    # Si el formato es web, renderizar la plantilla
    return render(request, 'reportes/avance_global.html', {
        'total_medidas': total_medidas,
        'avance_global': avance_global,
        'componentes': componentes,
        'estados': estados,
        'now': timezone.now()
    })


@login_required
def reporte_avance_organismo(request, organismo_id=None):
    """Vista para generar reporte de avance por organismo"""
    from apps.organismos.models import Organismo

    # Si no se especifica un organismo, usamos el del usuario actual
    if organismo_id is None and hasattr(request.user, 'organismo') and request.user.organismo:
        organismo_id = request.user.organismo.id

    # Verificar permisos
    if not (hasattr(request.user, 'is_superadmin') and request.user.is_superadmin or
            hasattr(request.user, 'is_admin_sma') and request.user.is_admin_sma):
        if not hasattr(request.user, 'organismo') or request.user.organismo.id != organismo_id:
            return redirect('dashboard_sma')  # Redireccionar si no tiene permisos

    # Obtener el organismo
    organismo = get_object_or_404(Organismo, id=organismo_id)

    # Obtener parámetros del reporte
    formato = request.GET.get('formato', 'web')  # web, pdf, excel

    # Obtener medidas asignadas al organismo
    medidas = Medida.objects.filter(responsables=organismo)

    # Calcular estadísticas
    total_medidas = medidas.count()
    avance_promedio = medidas.aggregate(promedio=Avg('porcentaje_avance'))['promedio'] or 0

    # Medidas por estado
    estados = medidas.values('estado').annotate(
        total=Count('id'),
        avance_promedio=Avg('porcentaje_avance')
    ).order_by('estado')

    # Medidas por componente
    componentes = Componente.objects.filter(medidas__in=medidas).distinct().annotate(
        total_medidas=Count('medidas', filter=Q(medidas__in=medidas)),
        avance=Avg('medidas__porcentaje_avance', filter=Q(medidas__in=medidas))
    ).order_by('nombre')

    # Últimos registros de avance
    registros_recientes = RegistroAvance.objects.filter(
        organismo=organismo
    ).order_by('-fecha_registro')[:10]

    # Si el formato es PDF, generar el PDF
    if formato == 'pdf':
        # Crear el documento PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="reporte_avance_{organismo.nombre}.pdf"'

        doc = SimpleDocTemplate(response, pagesize=letter)
        elements = []

        # Estilos
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        subtitle_style = styles['Heading2']
        normal_style = styles['Normal']

        # Título del reporte
        elements.append(Paragraph(f"Reporte de Avance: {organismo.nombre}", title_style))
        elements.append(Paragraph(f"Fecha: {timezone.now().strftime('%d/%m/%Y')}", normal_style))
        elements.append(Spacer(1, 0.5 * inch))

        # Resumen general
        elements.append(Paragraph("Resumen General", subtitle_style))
        data = [
            ["Total de Medidas Asignadas", str(total_medidas)],
            ["Avance Promedio", f"{avance_promedio:.1f}%"]
        ]
        t = Table(data, colWidths=[3 * inch, 1.5 * inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.3 * inch))

        # Medidas por estado
        elements.append(Paragraph("Medidas por Estado", subtitle_style))
        data = [["Estado", "Total", "Avance Promedio"]]
        for est in estados:
            data.append([
                est['estado'].replace('_', ' ').title(),
                str(est['total']),
                f"{est['avance_promedio'] or 0:.1f}%"
            ])
        t = Table(data, colWidths=[2 * inch, 1.5 * inch, 2 * inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.3 * inch))

        # Avance por componente
        elements.append(Paragraph("Avance por Componente", subtitle_style))
        data = [["Componente", "Total Medidas", "Avance"]]
        for comp in componentes:
            data.append([
                comp.nombre,
                str(comp.total_medidas),
                f"{comp.avance or 0:.1f}%"
            ])
        t = Table(data, colWidths=[3 * inch, 1.5 * inch, 1 * inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t)

        # Construir el PDF
        doc.build(elements)
        return response

    # Si el formato es web, renderizar la plantilla
    return render(request, 'reportes/avance_organismo.html', {
        'organismo': organismo,
        'total_medidas': total_medidas,
        'avance_promedio': avance_promedio,
        'estados': estados,
        'componentes': componentes,
        'registros_recientes': registros_recientes,
        'now': timezone.now()
    })


@login_required
def dashboard_interactivo(request):
    """Vista para el dashboard interactivo"""
    return render(request, 'reportes/dashboard_interactivo.html')
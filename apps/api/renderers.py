# apps/api/renderers.py
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework_csv.renderers import CSVRenderer

class MedidaCSVRenderer(CSVRenderer):
    header = ['codigo', 'nombre', 'componente_nombre', 'estado', 'porcentaje_avance',
              'fecha_inicio', 'fecha_termino']
    labels = {
        'codigo': 'Código',
        'nombre': 'Nombre de la Medida',
        'componente_nombre': 'Componente',
        'estado': 'Estado',
        'porcentaje_avance': 'Avance (%)',
        'fecha_inicio': 'Fecha Inicio',
        'fecha_termino': 'Fecha Término'
    }

class RegistroAvanceCSVRenderer(CSVRenderer):
    header = ['medida__codigo', 'medida__nombre', 'organismo__nombre',
              'fecha_registro', 'porcentaje_avance', 'descripcion']
    labels = {
        'medida__codigo': 'Código Medida',
        'medida__nombre': 'Medida',
        'organismo__nombre': 'Organismo',
        'fecha_registro': 'Fecha',
        'porcentaje_avance': 'Avance (%)',
        'descripcion': 'Descripción'
    }
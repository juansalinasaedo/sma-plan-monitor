from django.urls import path
from . import views

urlpatterns = [
    path('avance-global/', views.reporte_avance_global, name='reporte_avance_global'),
    path('avance-organismo/<int:organismo_id>/', views.reporte_avance_organismo, name='reporte_avance_organismo'),
    path('avance-organismo/', views.reporte_avance_organismo, name='reporte_mi_organismo'),
    path('dashboard-interactivo/', views.dashboard_interactivo, name='dashboard_interactivo'),
]
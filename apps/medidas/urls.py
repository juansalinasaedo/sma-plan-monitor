# apps/medidas/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/sma/', views.dashboard_sma, name='dashboard_sma'),
    path('avance/registrar/', views.registrar_avance, name='registrar_avance'),
    path('avance/registrar/<int:medida_id>/', views.registrar_avance, name='registrar_avance_medida'),
]
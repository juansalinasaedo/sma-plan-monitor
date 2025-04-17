# apps/publico/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio_portal, name='inicio_portal'),
]
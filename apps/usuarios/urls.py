from django.urls import path
from apps.usuarios import views as usuarios_views
from . import views

urlpatterns = [
    # ... otras URLs ...
    #path('logout/', views.logout_view, name='logout'),
    path('manual_logout/', usuarios_views.manual_logout, name='manual_logout'),
]
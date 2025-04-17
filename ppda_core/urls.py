"""
URL configuration for ppda_core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # API Endpoint
    path('api/v1/', include('apps.api.urls')),
    path('medidas/', include('apps.medidas.urls')),
    # path('organismos/', include('apps.organismos.urls')),
    #path('usuarios/', include('apps.usuarios.urls')),
    path('reportes/', include('apps.reportes.urls')),
    # path('notificaciones/', include('apps.notificaciones.urls')),
    # path('auditorias/', include('apps.auditorias.urls')),
    #path('accounts/', include('django.contrib.auth.urls')),
    # URLs de autenticación explícitas
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='registration/logged_out.html'), name='logout'),
    # Recuperar contraseña
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),


    # El portal público se mapea a la raíz del sitio
    path('', include('apps.publico.urls')),
]
# Agregar URLs para archivos estáticos y media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
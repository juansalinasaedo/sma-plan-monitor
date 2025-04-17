from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from .views.organismos import OrganismoViewSet, TipoOrganismoViewSet
from .views.medidas import ComponenteViewSet, MedidaViewSet, RegistroAvanceViewSet, debug_auth
from .views.dashboard import DashboardView

from .views.auth import CustomAuthToken, LogoutView

# Pendiente por la app Reporte
from .views.reportes import TipoReporteViewSet, ReporteGeneradoViewSet

from rest_framework.authtoken.views import obtain_auth_token
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view
from rest_framework.authentication import TokenAuthentication

schema_view = get_schema_view(
    openapi.Info(
        title="API Plan de Descontaminación",
        default_version='v1',
        description="API para el sistema de monitoreo del Plan de Descontaminación",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="grupo5@algo.com"),
        license=openapi.License(name="License ... algo"),
    ),
    public=True,
    permission_classes=(AllowAny,),
    authentication_classes=[]
)
# Configuración del router para las vistas basadas en viewsets
router = DefaultRouter()
router.register(r'organismos', OrganismoViewSet)
router.register(r'tipos-organismo', TipoOrganismoViewSet)
router.register(r'componentes', ComponenteViewSet)
router.register(r'medidas', MedidaViewSet)
router.register(r'registros-avance', RegistroAvanceViewSet)




router.register(r'tipos-reporte', TipoReporteViewSet)
router.register(r'reportes', ReporteGeneradoViewSet, basename='reportes')

# URLs de la API
urlpatterns = [

    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Endpoints drf-yasg (Swagger)
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Endpoints de la API
    path('', include(router.urls)),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    # Autenticación
    path('auth/token/', CustomAuthToken.as_view(), name='api-token'),
    path('auth/logout/', LogoutView.as_view(), name='api-logout'),
    
    path('debug-auth/', debug_auth),
]




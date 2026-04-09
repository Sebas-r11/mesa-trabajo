"""
URL configuration for flexop project - FLEX-OP Platform
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Configuración de Swagger/OpenAPI
schema_view = get_schema_view(
    openapi.Info(
        title="FLEX-OP API",
        default_version='v1',
        description="API REST para FLEX-OP - Flexible Operations Platform",
        contact=openapi.Contact(email="admin@flexop.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API JWT Authentication
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # API Modules - Modulos principales de FLEX-OP
    path('api/', include('usuarios.urls')),       # Usuarios y empresas
    path('api/', include('maquinas.urls')),       # Maquinas y productos
    path('api/', include('operaciones.urls')),    # Turnos, operarios, asignaciones
    path('api/', include('metricas.urls')),       # Produccion y metricas
    path('api/', include('alertas.urls')),        # Alertas y notificaciones
    path('api/', include('reasignaciones.urls')), # Sugerencias de reasignacion
    path('api/', include('reportes.urls')),       # Dashboards y reportes
    path('api/', include('ordenes.urls')),        # Ordenes de produccion
    
    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Personalización del admin
admin.site.site_header = "FLEX-OP Administración"
admin.site.site_title = "FLEX-OP Admin"
admin.site.index_title = "Panel de Administración"


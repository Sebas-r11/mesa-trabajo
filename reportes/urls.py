"""
URLs del modulo de Reportes para FLEX-OP

Este archivo define las rutas para los endpoints de reportes y dashboards.
Cada dashboard esta optimizado para el rol del usuario.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReporteGeneradoViewSet,
    DashboardOperarioView,
    DashboardSupervisorView,
    DashboardGerenteView,
    ExportarCSVView
)

# Router para el ViewSet de reportes generados
router = DefaultRouter()
router.register('reportes-generados', ReporteGeneradoViewSet, basename='reportes-generados')

urlpatterns = [
    # URLs del router (CRUD de reportes generados)
    path('', include(router.urls)),
    
    # Dashboards segun rol
    # Cada dashboard proporciona la informacion relevante para el rol
    path('dashboard/operario/', DashboardOperarioView.as_view(), name='dashboard-operario'),
    path('dashboard/supervisor/', DashboardSupervisorView.as_view(), name='dashboard-supervisor'),
    path('dashboard/gerente/', DashboardGerenteView.as_view(), name='dashboard-gerente'),
    
    # Exportacion de reportes
    path('exportar-csv/', ExportarCSVView.as_view(), name='exportar-csv'),
]

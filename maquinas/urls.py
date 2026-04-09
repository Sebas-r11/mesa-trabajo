"""
URLs de la app maquinas de FLEX-OP
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TipoMaquinaViewSet, MaquinaViewSet, UnidadEficienciaViewSet

# Router para ViewSets
router = DefaultRouter()
router.register(r'tipos-maquina', TipoMaquinaViewSet, basename='tipo-maquina')
router.register(r'maquinas', MaquinaViewSet, basename='maquina')
router.register(r'unidades-eficiencia', UnidadEficienciaViewSet, basename='unidad-eficiencia')

urlpatterns = [
    path('', include(router.urls)),
]

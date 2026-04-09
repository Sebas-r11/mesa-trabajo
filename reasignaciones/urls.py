"""
URLs de la app reasignaciones de FLEX-OP

Este archivo define las rutas URL para los endpoints del modulo
de reasignaciones.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SugerenciaReasignacionViewSet

# Router para ViewSets - genera automaticamente las URLs REST
router = DefaultRouter()
router.register(r'sugerencias', SugerenciaReasignacionViewSet, basename='sugerencia')

urlpatterns = [
    path('', include(router.urls)),
]

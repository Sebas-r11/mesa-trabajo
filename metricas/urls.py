"""
URLs de la app metricas de FLEX-OP

Este archivo define las rutas URL para todos los endpoints del modulo
de metricas, incluyendo registros de produccion, metricas de eficiencia
y objetivos de produccion.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegistroProduccionViewSet,
    MetricaEficienciaViewSet,
    ObjetivoProduccionViewSet
)

# Router para ViewSets - genera automaticamente las URLs REST
router = DefaultRouter()
router.register(r'produccion', RegistroProduccionViewSet, basename='produccion')
router.register(r'metricas', MetricaEficienciaViewSet, basename='metrica')
router.register(r'objetivos', ObjetivoProduccionViewSet, basename='objetivo')

urlpatterns = [
    path('', include(router.urls)),
]

"""
URLs del modulo de Ordenes de Produccion para FLEX-OP

Este archivo define las rutas para los endpoints de ordenes y cola de despacho.
Las ordenes son el nucleo del sistema de produccion.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrdenProduccionViewSet, ColaDespachoViewSet

# Router para los ViewSets
router = DefaultRouter()
router.register('ordenes', OrdenProduccionViewSet, basename='ordenes')
router.register('cola-despacho', ColaDespachoViewSet, basename='cola-despacho')

urlpatterns = [
    path('', include(router.urls)),
]

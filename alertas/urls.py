"""
URLs de la app alertas de FLEX-OP

Este archivo define las rutas URL para todos los endpoints del modulo
de alertas, incluyendo reglas, alertas y notificaciones.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReglaAlertaViewSet,
    AlertaViewSet,
    NotificacionViewSet
)

# Router para ViewSets - genera automaticamente las URLs REST
router = DefaultRouter()
router.register(r'reglas-alerta', ReglaAlertaViewSet, basename='regla-alerta')
router.register(r'alertas', AlertaViewSet, basename='alerta')
router.register(r'notificaciones', NotificacionViewSet, basename='notificacion')

urlpatterns = [
    path('', include(router.urls)),
]

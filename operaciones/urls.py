"""
URLs de la app operaciones de FLEX-OP

Este archivo define las rutas URL para todos los endpoints del modulo
de operaciones, incluyendo turnos, habilidades, operarios, asignaciones,
eventos e incidencias.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TurnoViewSet, 
    HabilidadViewSet, 
    OperarioViewSet,
    AsignacionViewSet,
    EventoViewSet,
    IncidenciaViewSet
)

# Router para ViewSets - genera automaticamente las URLs REST
router = DefaultRouter()
router.register(r'turnos', TurnoViewSet, basename='turno')
router.register(r'habilidades', HabilidadViewSet, basename='habilidad')
router.register(r'operarios', OperarioViewSet, basename='operario')
router.register(r'asignaciones', AsignacionViewSet, basename='asignacion')
router.register(r'eventos', EventoViewSet, basename='evento')
router.register(r'incidencias', IncidenciaViewSet, basename='incidencia')

urlpatterns = [
    path('', include(router.urls)),
]


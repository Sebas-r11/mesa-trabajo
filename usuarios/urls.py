"""
URLs de la app usuarios de FLEX-OP
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, EmpresaViewSet

# Router para ViewSets
router = DefaultRouter()
router.register(r'usuarios', UserViewSet, basename='usuario')
router.register(r'empresas', EmpresaViewSet, basename='empresa')

urlpatterns = [
    path('', include(router.urls)),
]

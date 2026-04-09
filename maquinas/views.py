"""
ViewSets del módulo de Máquinas para FLEX-OP
"""
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import TipoMaquina, Maquina, UnidadEficiencia
from .serializers import TipoMaquinaSerializer, MaquinaSerializer, UnidadEficienciaSerializer


class TipoMaquinaViewSet(viewsets.ModelViewSet):
    # Gestiona el CRUD de tipos de máquina (alta, baja, modificación, listado)
    """ViewSet para gestionar tipos de máquina"""
    
    queryset = TipoMaquina.objects.all()
    serializer_class = TipoMaquinaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre']
    filterset_fields = ['empresa']


class UnidadEficienciaViewSet(viewsets.ModelViewSet):
    # Gestiona el CRUD de unidades de eficiencia (u/h, kg/h, etc.)
    """ViewSet para gestionar unidades de eficiencia"""
    
    queryset = UnidadEficiencia.objects.all()
    serializer_class = UnidadEficienciaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'abreviatura']
    ordering_fields = ['nombre']
    filterset_fields = ['empresa']


class MaquinaViewSet(viewsets.ModelViewSet):
    # Gestiona el CRUD de máquinas y acciones como listar disponibles, operando y cambiar estado
    """ViewSet para gestionar máquinas"""
    
    queryset = Maquina.objects.all()
    serializer_class = MaquinaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['codigo', 'nombre', 'marca', 'modelo']
    ordering_fields = ['codigo', 'nombre', 'estado_actual']
    filterset_fields = ['estado_actual', 'tipo', 'empresa', 'activa']
    
    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        """Listar máquinas disponibles"""
        disponibles = self.queryset.filter(estado_actual=Maquina.EstadoChoices.DISPONIBLE, activa=True)
        serializer = self.get_serializer(disponibles, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def operando(self, request):
        """Listar máquinas en operación"""
        operando = self.queryset.filter(estado_actual=Maquina.EstadoChoices.OPERANDO)
        serializer = self.get_serializer(operando, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        """Cambiar el estado de una máquina"""
        maquina = self.get_object()
        nuevo_estado = request.data.get('estado')
        observacion = request.data.get('observacion', '')
        
        if nuevo_estado not in dict(Maquina.EstadoChoices.choices):
            return Response(
                {'error': 'Estado inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        maquina.cambiar_estado(nuevo_estado, request.user, observacion)
        serializer = self.get_serializer(maquina)
        return Response(serializer.data)

"""
ViewSets del modulo de Alertas para FLEX-OP

Este archivo contiene las vistas para gestionar reglas de alerta,
alertas y notificaciones.
"""
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from django.utils import timezone

from .models import ReglaAlerta, Alerta, Notificacion
from .serializers import (
    ReglaAlertaSerializer,
    AlertaSerializer,
    AlertaCreateSerializer,
    ResolverAlertaSerializer,
    NotificacionSerializer
)


class ReglaAlertaViewSet(viewsets.ModelViewSet):
    # Gestiona reglas de alerta
    """
    ViewSet para gestionar reglas de alerta
    
    Las reglas definen condiciones que disparan alertas automaticas.
    
    Endpoints disponibles:
    - GET /reglas-alerta/ - Lista todas las reglas
    - POST /reglas-alerta/ - Crea una nueva regla
    - GET /reglas-alerta/{id}/ - Obtiene una regla especifica
    - PUT /reglas-alerta/{id}/ - Actualiza una regla
    - DELETE /reglas-alerta/{id}/ - Elimina una regla
    - GET /reglas-alerta/activas/ - Lista reglas activas
    - POST /reglas-alerta/{id}/evaluar/ - Evalua una regla manualmente
    - POST /reglas-alerta/evaluar-todas/ - Evalua todas las reglas activas
    """
    
    queryset = ReglaAlerta.objects.all()
    serializer_class = ReglaAlertaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'tipo', 'prioridad']
    filterset_fields = ['tipo', 'prioridad', 'activa', 'empresa']
    
    @action(detail=False, methods=['get'])
    def activas(self, request):
        """Lista solo las reglas que estan activas"""
        activas = self.queryset.filter(activa=True)
        serializer = self.get_serializer(activas, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def evaluar(self, request, pk=None):
        """
        Evalua una regla manualmente y genera alertas si corresponde
        
        Util para probar reglas o forzar la evaluacion.
        """
        regla = self.get_object()
        
        try:
            alertas = regla.evaluar()
            return Response({
                'mensaje': f'Regla evaluada correctamente',
                'alertas_generadas': len(alertas),
                'alertas': AlertaSerializer(alertas, many=True).data
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def evaluar_todas(self, request):
        """
        Evalua todas las reglas activas
        
        Este endpoint es util para probar el sistema de alertas
        o puede ser llamado por una tarea programada.
        """
        reglas_activas = self.queryset.filter(activa=True)
        total_alertas = []
        
        for regla in reglas_activas:
            try:
                alertas = regla.evaluar()
                total_alertas.extend(alertas)
            except Exception as e:
                # Continuar con las demas reglas aunque una falle
                pass
        
        return Response({
            'mensaje': f'Se evaluaron {reglas_activas.count()} reglas',
            'alertas_generadas': len(total_alertas)
        })


class AlertaViewSet(viewsets.ModelViewSet):
    # Gestiona alertas del sistema
    """
    ViewSet para gestionar alertas
    
    Las alertas son generadas automaticamente por las reglas
    o pueden crearse manualmente.
    
    Endpoints disponibles:
    - GET /alertas/ - Lista todas las alertas
    - POST /alertas/ - Crea una alerta manual
    - GET /alertas/{id}/ - Obtiene una alerta especifica
    - PUT /alertas/{id}/ - Actualiza una alerta
    - DELETE /alertas/{id}/ - Elimina una alerta
    - GET /alertas/activas/ - Lista alertas activas
    - GET /alertas/por-prioridad/ - Agrupa por prioridad
    - POST /alertas/{id}/resolver/ - Marca como resuelta
    - POST /alertas/{id}/escalar/ - Escala a nivel superior
    - GET /alertas/estadisticas/ - Estadisticas de alertas
    """
    
    queryset = Alerta.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['titulo', 'descripcion']
    ordering_fields = ['fecha_creacion', 'prioridad', 'estado']
    filterset_fields = ['estado', 'prioridad', 'empresa', 'regla']
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado segun la accion"""
        if self.action == 'create':
            return AlertaCreateSerializer
        return AlertaSerializer
    
    @action(detail=False, methods=['get'])
    def activas(self, request):
        """
        Lista alertas activas que requieren atencion
        
        Ordena por prioridad (criticas primero) y fecha.
        """
        activas = self.queryset.filter(
            estado=Alerta.EstadoChoices.ACTIVA
        ).order_by('-prioridad', '-fecha_creacion')
        
        serializer = self.get_serializer(activas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_prioridad(self, request):
        """
        Agrupa alertas activas por prioridad
        
        Util para ver rapidamente cuantas alertas hay de cada tipo.
        """
        activas = self.queryset.filter(estado=Alerta.EstadoChoices.ACTIVA)
        
        resultado = {
            'CRITICA': activas.filter(prioridad='CRITICA').count(),
            'ALTA': activas.filter(prioridad='ALTA').count(),
            'MEDIA': activas.filter(prioridad='MEDIA').count(),
            'BAJA': activas.filter(prioridad='BAJA').count(),
            'total': activas.count()
        }
        
        return Response(resultado)
    
    @action(detail=True, methods=['post'])
    def resolver(self, request, pk=None):
        """
        Marca una alerta como resuelta
        
        Puede recibir en el body:
        - notas: Notas sobre como se resolvio
        """
        alerta = self.get_object()
        serializer = ResolverAlertaSerializer(data=request.data)
        
        if serializer.is_valid():
            notas = serializer.validated_data.get('notas', '')
            alerta.resolver(request.user, notas)
            
            return Response({
                'mensaje': 'Alerta resuelta correctamente',
                'alerta': AlertaSerializer(alerta).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def escalar(self, request, pk=None):
        """
        Escala una alerta a nivel superior
        
        Notifica a los gerentes y cambia el estado a ESCALADA.
        """
        alerta = self.get_object()
        notas = request.data.get('notas', 'Escalada por supervisor')
        
        alerta.escalar(notas)
        
        return Response({
            'mensaje': 'Alerta escalada correctamente',
            'alerta': AlertaSerializer(alerta).data
        })
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Obtiene estadisticas de alertas
        
        Retorna contadores por estado, prioridad y tipo de regla.
        """
        stats = {
            'por_estado': list(
                self.queryset.values('estado').annotate(total=Count('id'))
            ),
            'por_prioridad': list(
                self.queryset.values('prioridad').annotate(total=Count('id'))
            ),
            'por_regla': list(
                self.queryset.exclude(regla__isnull=True)
                .values('regla__tipo').annotate(total=Count('id'))
            ),
            'total': self.queryset.count(),
            'activas': self.queryset.filter(estado='ACTIVA').count(),
            'resueltas_hoy': self.queryset.filter(
                estado='RESUELTA',
                fecha_resolucion__date=timezone.now().date()
            ).count()
        }
        
        return Response(stats)


class NotificacionViewSet(viewsets.ModelViewSet):
    # Gestiona notificaciones de usuarios
    """
    ViewSet para gestionar notificaciones
    
    Las notificaciones avisan a los usuarios sobre alertas
    y otros eventos importantes.
    
    Endpoints disponibles:
    - GET /notificaciones/ - Lista notificaciones del usuario actual
    - GET /notificaciones/{id}/ - Obtiene una notificacion especifica
    - GET /notificaciones/no-leidas/ - Lista notificaciones sin leer
    - POST /notificaciones/{id}/marcar-leida/ - Marca como leida
    - POST /notificaciones/marcar-todas-leidas/ - Marca todas como leidas
    """
    
    queryset = Notificacion.objects.all()
    serializer_class = NotificacionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['fecha_creacion']
    
    def get_queryset(self):
        """Filtra para mostrar solo notificaciones del usuario actual"""
        return self.queryset.filter(usuario=self.request.user)
    
    @action(detail=False, methods=['get'])
    def no_leidas(self, request):
        """Lista notificaciones que no han sido leidas"""
        no_leidas = self.get_queryset().filter(leida=False)
        serializer = self.get_serializer(no_leidas, many=True)
        return Response({
            'cantidad': no_leidas.count(),
            'notificaciones': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def marcar_leida(self, request, pk=None):
        """Marca una notificacion como leida"""
        notificacion = self.get_object()
        notificacion.marcar_leida()
        return Response({
            'mensaje': 'Notificacion marcada como leida'
        })
    
    @action(detail=False, methods=['post'])
    def marcar_todas_leidas(self, request):
        """Marca todas las notificaciones del usuario como leidas"""
        no_leidas = self.get_queryset().filter(leida=False)
        cantidad = no_leidas.count()
        
        for notificacion in no_leidas:
            notificacion.marcar_leida()
        
        return Response({
            'mensaje': f'Se marcaron {cantidad} notificaciones como leidas'
        })


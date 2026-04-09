"""
ViewSets del modulo de Ordenes de Produccion para FLEX-OP

Este archivo contiene las vistas para gestionar ordenes de produccion
y la cola de despacho. Las ordenes son el corazon de la produccion.
"""
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from .models import OrdenProduccion, ColaDespacho
from .serializers import (
    OrdenProduccionSerializer,
    OrdenProduccionCreateSerializer,
    OrdenProduccionListSerializer,
    ColaDespachoSerializer,
    ActualizarProduccionSerializer
)


class OrdenProduccionViewSet(viewsets.ModelViewSet):
    # Gestiona las ordenes de produccion
    """
    ViewSet para gestionar ordenes de produccion
    
    Las ordenes de produccion representan el trabajo que debe
    realizarse en planta. Incluyen producto, cantidad y fechas.
    
    Endpoints disponibles:
    - GET /ordenes/ - Lista todas las ordenes
    - POST /ordenes/ - Crea una nueva orden
    - GET /ordenes/{id}/ - Obtiene detalle de una orden
    - PUT /ordenes/{id}/ - Actualiza una orden
    - DELETE /ordenes/{id}/ - Elimina una orden
    - POST /ordenes/{id}/iniciar/ - Inicia produccion de la orden
    - POST /ordenes/{id}/registrar_produccion/ - Registra unidades producidas
    - POST /ordenes/{id}/completar/ - Marca la orden como completada
    - POST /ordenes/{id}/cancelar/ - Cancela la orden
    - GET /ordenes/pendientes/ - Lista ordenes pendientes
    - GET /ordenes/en_progreso/ - Lista ordenes en progreso
    """
    
    queryset = OrdenProduccion.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ['estado', 'prioridad', 'maquina_asignada', 'empresa']
    search_fields = ['numero_orden', 'producto__nombre']
    ordering_fields = ['fecha_creacion', 'fecha_entrega_estimada', 'prioridad']
    
    def get_serializer_class(self):
        """Selecciona el serializer segun la accion"""
        if self.action == 'create':
            return OrdenProduccionCreateSerializer
        elif self.action == 'list':
            return OrdenProduccionListSerializer
        return OrdenProduccionSerializer
    
    def get_queryset(self):
        """Filtra por empresa del usuario"""
        empresa = self.request.user.empresa
        return self.queryset.filter(empresa=empresa)
    
    @action(detail=True, methods=['post'])
    def iniciar(self, request, pk=None):
        # Inicia la produccion de una orden
        """
        POST /ordenes/{id}/iniciar/
        
        Cambia el estado de la orden de PENDIENTE a EN_PROGRESO.
        Solo se pueden iniciar ordenes que estan pendientes.
        """
        orden = self.get_object()
        
        if orden.estado != 'PENDIENTE':
            return Response(
                {'error': 'Solo se pueden iniciar ordenes pendientes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        orden.estado = 'EN_PROGRESO'
        orden.save()
        
        return Response({
            'mensaje': f'Orden {orden.numero_orden} iniciada',
            'orden': OrdenProduccionSerializer(orden).data
        })
    
    @action(detail=True, methods=['post'])
    def registrar_produccion(self, request, pk=None):
        # Registra unidades producidas
        """
        POST /ordenes/{id}/registrar_produccion/
        Body: {"cantidad": 100}
        
        Suma la cantidad indicada a la produccion de la orden.
        Si se alcanza la cantidad solicitada, la orden puede completarse.
        """
        orden = self.get_object()
        serializer = ActualizarProduccionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        if orden.estado not in ['PENDIENTE', 'EN_PROGRESO']:
            return Response(
                {'error': 'Solo se puede registrar produccion en ordenes activas'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Si la orden estaba pendiente, la iniciamos automaticamente
        if orden.estado == 'PENDIENTE':
            orden.estado = 'EN_PROGRESO'
        
        cantidad = serializer.validated_data['cantidad']
        orden.cantidad_producida += cantidad
        orden.save()
        
        # Verificar si se completo
        completada = orden.cantidad_producida >= orden.cantidad_solicitada
        
        return Response({
            'mensaje': f'Produccion registrada: {cantidad} unidades',
            'cantidad_total_producida': orden.cantidad_producida,
            'cantidad_solicitada': orden.cantidad_solicitada,
            'orden_completada': completada,
            'orden': OrdenProduccionSerializer(orden).data
        })
    
    @action(detail=True, methods=['post'])
    def completar(self, request, pk=None):
        # Marca la orden como completada
        """
        POST /ordenes/{id}/completar/
        
        Marca la orden como completada y la agrega a la cola de despacho.
        La orden debe tener produccion registrada para completarse.
        """
        orden = self.get_object()
        
        if orden.estado == 'COMPLETADA':
            return Response(
                {'error': 'La orden ya esta completada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if orden.estado == 'CANCELADA':
            return Response(
                {'error': 'No se puede completar una orden cancelada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if orden.cantidad_producida == 0:
            return Response(
                {'error': 'La orden no tiene produccion registrada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        orden.estado = 'COMPLETADA'
        orden.save()
        
        # Agregar a cola de despacho
        ultima_posicion = ColaDespacho.objects.filter(
            orden__empresa=orden.empresa
        ).count()
        
        cola = ColaDespacho.objects.create(
            orden=orden,
            posicion_cola=ultima_posicion + 1
        )
        
        return Response({
            'mensaje': f'Orden {orden.numero_orden} completada y agregada a cola de despacho',
            'posicion_cola': cola.posicion_cola,
            'orden': OrdenProduccionSerializer(orden).data
        })
    
    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        # Cancela una orden
        """
        POST /ordenes/{id}/cancelar/
        Body (opcional): {"motivo": "Razon de la cancelacion"}
        
        Cancela la orden. Las ordenes completadas no se pueden cancelar.
        """
        orden = self.get_object()
        
        if orden.estado == 'COMPLETADA':
            return Response(
                {'error': 'No se puede cancelar una orden completada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if orden.estado == 'CANCELADA':
            return Response(
                {'error': 'La orden ya esta cancelada'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        motivo = request.data.get('motivo', 'Sin motivo especificado')
        orden.estado = 'CANCELADA'
        orden.notas = f"{orden.notas or ''}\n[CANCELADA] {motivo}".strip()
        orden.save()
        
        return Response({
            'mensaje': f'Orden {orden.numero_orden} cancelada',
            'orden': OrdenProduccionSerializer(orden).data
        })
    
    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        # Lista ordenes pendientes
        """
        GET /ordenes/pendientes/
        
        Retorna todas las ordenes con estado PENDIENTE
        ordenadas por prioridad y fecha de entrega.
        """
        ordenes = self.get_queryset().filter(
            estado='PENDIENTE'
        ).order_by('-prioridad', 'fecha_entrega_estimada')
        
        serializer = OrdenProduccionListSerializer(ordenes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def en_progreso(self, request):
        # Lista ordenes en progreso
        """
        GET /ordenes/en_progreso/
        
        Retorna todas las ordenes que estan actualmente
        en produccion, ordenadas por prioridad.
        """
        ordenes = self.get_queryset().filter(
            estado='EN_PROGRESO'
        ).order_by('-prioridad', 'fecha_entrega_estimada')
        
        serializer = OrdenProduccionListSerializer(ordenes, many=True)
        return Response(serializer.data)


class ColaDespachoViewSet(viewsets.ModelViewSet):
    # Gestiona la cola de despacho
    """
    ViewSet para gestionar la cola de despacho
    
    La cola de despacho organiza las ordenes completadas
    que estan listas para ser entregadas al cliente.
    
    Endpoints disponibles:
    - GET /cola-despacho/ - Lista la cola de despacho
    - GET /cola-despacho/{id}/ - Obtiene detalle de un item
    - POST /cola-despacho/{id}/despachar/ - Marca como despachado
    - POST /cola-despacho/reordenar/ - Reordena la cola
    - GET /cola-despacho/pendientes/ - Items pendientes de despacho
    """
    
    queryset = ColaDespacho.objects.all()
    serializer_class = ColaDespachoSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['despachado']
    ordering_fields = ['posicion_cola', 'fecha_ingreso_cola']
    
    # Solo lectura y acciones personalizadas
    http_method_names = ['get', 'head', 'options', 'post']
    
    def get_queryset(self):
        """Filtra por empresa del usuario"""
        empresa = self.request.user.empresa
        return self.queryset.filter(
            orden__empresa=empresa
        ).order_by('posicion_cola')
    
    @action(detail=True, methods=['post'])
    def despachar(self, request, pk=None):
        # Marca un item como despachado
        """
        POST /cola-despacho/{id}/despachar/
        
        Marca el item de la cola como despachado.
        Registra la fecha y hora del despacho.
        """
        item = self.get_object()
        
        if item.despachado:
            return Response(
                {'error': 'Este item ya fue despachado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        item.despachado = True
        item.fecha_despacho = timezone.now()
        item.save()
        
        return Response({
            'mensaje': f'Orden {item.orden.numero_orden} despachada',
            'fecha_despacho': item.fecha_despacho,
            'item': ColaDespachoSerializer(item).data
        })
    
    @action(detail=False, methods=['post'])
    def reordenar(self, request):
        # Reordena la cola de despacho
        """
        POST /cola-despacho/reordenar/
        Body: {"orden": [3, 1, 2]}  (lista de IDs en el nuevo orden)
        
        Reordena los items de la cola segun el orden especificado.
        """
        nuevo_orden = request.data.get('orden', [])
        
        if not nuevo_orden:
            return Response(
                {'error': 'Se requiere una lista de IDs'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        empresa = request.user.empresa
        
        # Verificar que todos los IDs pertenecen a la empresa
        items = ColaDespacho.objects.filter(
            id__in=nuevo_orden,
            orden__empresa=empresa,
            despachado=False
        )
        
        if items.count() != len(nuevo_orden):
            return Response(
                {'error': 'Algunos IDs no son validos o ya fueron despachados'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Actualizar posiciones
        for posicion, item_id in enumerate(nuevo_orden, start=1):
            ColaDespacho.objects.filter(id=item_id).update(posicion_cola=posicion)
        
        return Response({
            'mensaje': 'Cola reordenada exitosamente',
            'nuevo_orden': nuevo_orden
        })
    
    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        # Lista items pendientes de despacho
        """
        GET /cola-despacho/pendientes/
        
        Retorna todos los items que aun no han sido despachados,
        ordenados por posicion en la cola.
        """
        items = self.get_queryset().filter(
            despachado=False
        ).order_by('posicion_cola')
        
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)

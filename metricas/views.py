"""
ViewSets del modulo de Metricas para FLEX-OP

Este archivo contiene las vistas para gestionar registros de produccion,
metricas de eficiencia y objetivos de produccion.
"""
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Avg, Max
from django.utils import timezone
from datetime import timedelta

from .models import RegistroProduccion, MetricaEficiencia, ObjetivoProduccion
from .serializers import (
    RegistroProduccionSerializer,
    RegistroProduccionCreateSerializer,
    MetricaEficienciaSerializer,
    ObjetivoProduccionSerializer
)


class RegistroProduccionViewSet(viewsets.ModelViewSet):
    # Gestiona registros de produccion
    """
    ViewSet para gestionar registros de produccion
    
    Los registros de produccion capturan la cantidad producida
    durante las asignaciones.
    
    Endpoints disponibles:
    - GET /produccion/ - Lista todos los registros
    - POST /produccion/ - Crea un nuevo registro
    - GET /produccion/{id}/ - Obtiene un registro especifico
    - PUT /produccion/{id}/ - Actualiza un registro
    - DELETE /produccion/{id}/ - Elimina un registro
    - GET /produccion/por-asignacion/ - Agrupa por asignacion
    - GET /produccion/por-maquina/ - Agrupa por maquina
    - GET /produccion/resumen-dia/ - Resumen del dia
    """
    
    queryset = RegistroProduccion.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['fecha_hora', 'cantidad']
    filterset_fields = ['asignacion', 'registrado_por']
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado segun la accion"""
        if self.action == 'create':
            return RegistroProduccionCreateSerializer
        return RegistroProduccionSerializer
    
    @action(detail=False, methods=['get'])
    def por_asignacion(self, request):
        """
        Agrupa registros por asignacion
        
        Parametro de query requerido:
        - asignacion_id: ID de la asignacion
        """
        asignacion_id = request.query_params.get('asignacion_id')
        
        if not asignacion_id:
            return Response(
                {'error': 'Se requiere el parametro asignacion_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        registros = self.queryset.filter(asignacion_id=asignacion_id)
        total = registros.aggregate(total=Sum('cantidad'))['total'] or 0
        
        return Response({
            'asignacion_id': asignacion_id,
            'registros': RegistroProduccionSerializer(registros, many=True).data,
            'total_producido': total
        })
    
    @action(detail=False, methods=['get'])
    def por_maquina(self, request):
        """
        Agrupa registros por maquina
        
        Parametros de query:
        - maquina_id: ID de la maquina (requerido)
        - fecha: Fecha especifica (opcional, default hoy)
        """
        maquina_id = request.query_params.get('maquina_id')
        fecha = request.query_params.get('fecha', timezone.now().date())
        
        if not maquina_id:
            return Response(
                {'error': 'Se requiere el parametro maquina_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        registros = self.queryset.filter(
            asignacion__maquina_id=maquina_id,
            fecha_hora__date=fecha
        )
        total = registros.aggregate(total=Sum('cantidad'))['total'] or 0
        
        return Response({
            'maquina_id': maquina_id,
            'fecha': str(fecha),
            'total_producido': total,
            'cantidad_registros': registros.count()
        })
    
    @action(detail=False, methods=['get'])
    def resumen_dia(self, request):
        """
        Obtiene un resumen de produccion del dia
        
        Parametro de query opcional:
        - fecha: Fecha a consultar (default hoy)
        """
        fecha = request.query_params.get('fecha', timezone.now().date())
        
        registros = self.queryset.filter(fecha_hora__date=fecha)
        
        # Agrupar por maquina
        por_maquina = registros.values(
            'asignacion__maquina__codigo',
            'asignacion__maquina__nombre'
        ).annotate(
            total=Sum('cantidad')
        ).order_by('-total')
        
        return Response({
            'fecha': str(fecha),
            'total_produccion': registros.aggregate(total=Sum('cantidad'))['total'] or 0,
            'cantidad_registros': registros.count(),
            'por_maquina': list(por_maquina)
        })


class MetricaEficienciaViewSet(viewsets.ModelViewSet):
    # Gestiona metricas de eficiencia
    """
    ViewSet para gestionar metricas de eficiencia
    
    Las metricas de eficiencia se calculan automaticamente
    al finalizar asignaciones, pero tambien pueden consultarse
    y analizarse.
    
    Endpoints disponibles:
    - GET /metricas/ - Lista todas las metricas
    - GET /metricas/{id}/ - Obtiene una metrica especifica
    - GET /metricas/por-operario/ - Metricas de un operario
    - GET /metricas/por-maquina/ - Metricas de una maquina
    - GET /metricas/por-turno/ - Metricas de un turno
    - GET /metricas/resumen-periodo/ - Resumen de un periodo
    - GET /metricas/ranking-operarios/ - Ranking de eficiencia
    - POST /metricas/calcular/ - Calcula metrica para asignacion
    """
    
    queryset = MetricaEficiencia.objects.all()
    serializer_class = MetricaEficienciaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['fecha', 'eficiencia_calculada']
    filterset_fields = ['operario', 'maquina', 'fecha']
    
    # Deshabilitar creacion manual (se crea automaticamente)
    http_method_names = ['get', 'head', 'options']
    
    @action(detail=False, methods=['get'])
    def por_operario(self, request):
        """
        Obtiene metricas de un operario especifico
        
        Parametros de query:
        - operario_id: ID del operario (requerido)
        - dias: Cantidad de dias hacia atras (default 7)
        """
        operario_id = request.query_params.get('operario_id')
        dias = int(request.query_params.get('dias', 7))
        
        if not operario_id:
            return Response(
                {'error': 'Se requiere el parametro operario_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        fecha_inicio = timezone.now().date() - timedelta(days=dias)
        
        metricas = self.queryset.filter(
            operario_id=operario_id,
            fecha__gte=fecha_inicio
        ).order_by('fecha')
        
        # Calcular promedios
        stats = metricas.aggregate(
            eficiencia_promedio=Avg('eficiencia_calculada'),
            total_produccion=Sum('produccion_real'),
            horas_totales=Sum('horas_trabajadas')
        )
        
        return Response({
            'operario_id': operario_id,
            'periodo_dias': dias,
            'metricas': MetricaEficienciaSerializer(metricas, many=True).data,
            'estadisticas': stats
        })
    
    @action(detail=False, methods=['get'])
    def por_maquina(self, request):
        """
        Obtiene metricas de una maquina especifica
        
        Parametros de query:
        - maquina_id: ID de la maquina (requerido)
        - dias: Cantidad de dias hacia atras (default 7)
        """
        maquina_id = request.query_params.get('maquina_id')
        dias = int(request.query_params.get('dias', 7))
        
        if not maquina_id:
            return Response(
                {'error': 'Se requiere el parametro maquina_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        fecha_inicio = timezone.now().date() - timedelta(days=dias)
        
        metricas = self.queryset.filter(
            maquina_id=maquina_id,
            fecha__gte=fecha_inicio
        ).order_by('fecha')
        
        # Calcular promedios
        stats = metricas.aggregate(
            eficiencia_promedio=Avg('eficiencia_calculada'),
            total_produccion=Sum('produccion_real'),
            horas_totales=Sum('horas_trabajadas')
        )
        
        return Response({
            'maquina_id': maquina_id,
            'periodo_dias': dias,
            'metricas': MetricaEficienciaSerializer(metricas, many=True).data,
            'estadisticas': stats
        })
    
    @action(detail=False, methods=['get'])
    def resumen_periodo(self, request):
        """
        Obtiene un resumen de eficiencia de un periodo
        
        Parametros de query opcionales:
        - fecha_inicio: Fecha inicial (default hace 7 dias)
        - fecha_fin: Fecha final (default hoy)
        """
        fecha_fin = request.query_params.get('fecha_fin', timezone.now().date())
        fecha_inicio = request.query_params.get(
            'fecha_inicio', 
            timezone.now().date() - timedelta(days=7)
        )
        
        metricas = self.queryset.filter(
            fecha__gte=fecha_inicio,
            fecha__lte=fecha_fin
        )
        
        # Resumen por dia
        por_dia = metricas.values('fecha').annotate(
            eficiencia_promedio=Avg('eficiencia_calculada'),
            total_produccion=Sum('produccion_real'),
            cantidad_registros=models.Count('id')
        ).order_by('fecha')
        
        # Estadisticas generales
        stats = metricas.aggregate(
            eficiencia_promedio=Avg('eficiencia_calculada'),
            eficiencia_maxima=Max('eficiencia_calculada'),
            total_produccion=Sum('produccion_real'),
            horas_totales=Sum('horas_trabajadas')
        )
        
        return Response({
            'fecha_inicio': str(fecha_inicio),
            'fecha_fin': str(fecha_fin),
            'por_dia': list(por_dia),
            'estadisticas': stats
        })
    
    @action(detail=False, methods=['get'])
    def ranking_operarios(self, request):
        """
        Obtiene ranking de operarios por eficiencia
        
        Parametros de query opcionales:
        - limite: Cantidad de operarios (default 10)
        - dias: Dias a considerar (default 30)
        """
        limite = int(request.query_params.get('limite', 10))
        dias = int(request.query_params.get('dias', 30))
        
        fecha_inicio = timezone.now().date() - timedelta(days=dias)
        
        ranking = self.queryset.filter(
            fecha__gte=fecha_inicio
        ).values(
            'operario__codigo_empleado',
            'operario__usuario__first_name',
            'operario__usuario__last_name'
        ).annotate(
            eficiencia_promedio=Avg('eficiencia_calculada'),
            total_produccion=Sum('produccion_real'),
            total_registros=models.Count('id')
        ).order_by('-eficiencia_promedio')[:limite]
        
        return Response({
            'periodo_dias': dias,
            'ranking': list(ranking)
        })
    
    @action(detail=False, methods=['post'])
    def calcular(self, request):
        """
        Calcula metrica de eficiencia para una asignacion
        
        Requiere en el body:
        - asignacion_id: ID de la asignacion completada
        """
        from operaciones.models import Asignacion
        
        asignacion_id = request.data.get('asignacion_id')
        
        if not asignacion_id:
            return Response(
                {'error': 'Se requiere asignacion_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            asignacion = Asignacion.objects.get(id=asignacion_id)
            
            if asignacion.estado != 'COMPLETADA':
                return Response(
                    {'error': 'Solo se pueden calcular metricas de asignaciones completadas'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            metrica = MetricaEficiencia.calcular_para_asignacion(asignacion)
            
            if metrica:
                return Response({
                    'mensaje': 'Metrica calculada correctamente',
                    'metrica': MetricaEficienciaSerializer(metrica).data
                })
            else:
                return Response(
                    {'error': 'No se pudo calcular la metrica'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Asignacion.DoesNotExist:
            return Response(
                {'error': 'Asignacion no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )


class ObjetivoProduccionViewSet(viewsets.ModelViewSet):
    # Gestiona objetivos de produccion
    """
    ViewSet para gestionar objetivos de produccion
    
    Los objetivos definen metas de produccion que sirven
    para medir el cumplimiento y generar alertas.
    
    Endpoints disponibles:
    - GET /objetivos/ - Lista todos los objetivos
    - POST /objetivos/ - Crea un nuevo objetivo
    - GET /objetivos/{id}/ - Obtiene un objetivo especifico
    - PUT /objetivos/{id}/ - Actualiza un objetivo
    - DELETE /objetivos/{id}/ - Elimina un objetivo
    - GET /objetivos/activos/ - Lista objetivos activos
    - GET /objetivos/{id}/cumplimiento/ - Calcula cumplimiento
    """
    
    queryset = ObjetivoProduccion.objects.all()
    serializer_class = ObjetivoProduccionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['fecha_inicio', 'cantidad_objetivo']
    filterset_fields = ['tipo', 'empresa', 'activo']
    
    @action(detail=False, methods=['get'])
    def activos(self, request):
        """Lista solo objetivos activos y vigentes"""
        hoy = timezone.now().date()
        activos = self.queryset.filter(
            activo=True,
            fecha_inicio__lte=hoy
        ).filter(
            models.Q(fecha_fin__isnull=True) | models.Q(fecha_fin__gte=hoy)
        )
        serializer = self.get_serializer(activos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def cumplimiento(self, request, pk=None):
        """
        Calcula el cumplimiento de un objetivo
        
        Parametro de query opcional:
        - fecha: Fecha para la cual calcular (default hoy)
        """
        objetivo = self.get_object()
        fecha = request.query_params.get('fecha')
        
        if fecha:
            from datetime import datetime
            fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        
        cumplimiento = objetivo.calcular_cumplimiento(fecha)
        
        return Response({
            'objetivo': ObjetivoProduccionSerializer(objetivo).data,
            'cumplimiento': cumplimiento
        })


# Importar models para usar en consultas
from django.db import models


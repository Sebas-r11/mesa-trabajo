"""
Serializers del modulo de Reportes para FLEX-OP

Este archivo contiene los serializers para el historial de reportes
y los datos de dashboard.
"""
from rest_framework import serializers
from .models import ReporteGenerado


class ReporteGeneradoSerializer(serializers.ModelSerializer):
    # Serializer para reportes generados
    """
    Serializer para convertir reportes generados a JSON
    
    Incluye el tipo y formato en texto legible.
    """
    
    # Campos en formato legible
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    formato_display = serializers.CharField(source='get_formato_display', read_only=True)
    
    # Usuario que genero
    generado_por_nombre = serializers.CharField(
        source='generado_por.get_full_name', 
        read_only=True
    )
    
    class Meta:
        model = ReporteGenerado
        fields = [
            'id', 'tipo', 'tipo_display',
            'formato', 'formato_display',
            'fecha_inicio', 'fecha_fin',
            'archivo', 'empresa',
            'generado_por', 'generado_por_nombre',
            'fecha_generacion', 'parametros'
        ]
        read_only_fields = ['id', 'archivo', 'fecha_generacion']


class DashboardOperarioSerializer(serializers.Serializer):
    # Serializer para datos del dashboard de operario
    """
    Serializer para el dashboard de operarios
    
    Contiene la informacion que ve un operario en su dashboard.
    """
    
    # Asignacion actual
    asignacion_activa = serializers.DictField(allow_null=True)
    
    # Metricas del dia
    eficiencia_hoy = serializers.DecimalField(max_digits=6, decimal_places=2)
    produccion_hoy = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # Objetivo vs real
    objetivo_dia = serializers.DecimalField(max_digits=12, decimal_places=2)
    porcentaje_objetivo = serializers.DecimalField(max_digits=6, decimal_places=2)
    
    # Tareas completadas
    tareas_completadas_hoy = serializers.IntegerField()
    
    # Eficiencia historica
    eficiencia_promedio = serializers.DecimalField(max_digits=5, decimal_places=2)


class DashboardSupervisorSerializer(serializers.Serializer):
    # Serializer para datos del dashboard de supervisor
    """
    Serializer para el dashboard de supervisores
    
    Contiene la informacion que ve un supervisor en su dashboard.
    """
    
    # Estado de maquinas
    maquinas_estado = serializers.ListField(child=serializers.DictField())
    
    # Alertas activas
    alertas_activas = serializers.IntegerField()
    alertas_criticas = serializers.IntegerField()
    
    # Sugerencias pendientes
    sugerencias_pendientes = serializers.IntegerField()
    
    # Eficiencia del turno
    eficiencia_turno = serializers.DecimalField(max_digits=6, decimal_places=2)
    
    # Ranking de operarios del turno
    ranking_operarios = serializers.ListField(child=serializers.DictField())
    
    # Incidencias abiertas
    incidencias_abiertas = serializers.IntegerField()


class DashboardGerenteSerializer(serializers.Serializer):
    # Serializer para datos del dashboard de gerente
    """
    Serializer para el dashboard de gerentes
    
    Contiene los KPIs y metricas gerenciales.
    """
    
    # KPIs principales
    eficiencia_general = serializers.DecimalField(max_digits=6, decimal_places=2)
    oee_aproximado = serializers.DecimalField(max_digits=6, decimal_places=2)
    cumplimiento_objetivos = serializers.DecimalField(max_digits=6, decimal_places=2)
    
    # Produccion
    produccion_total_dia = serializers.DecimalField(max_digits=12, decimal_places=2)
    produccion_total_semana = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # Tendencias (ultimos 7 dias)
    tendencia_eficiencia = serializers.ListField(child=serializers.DictField())
    
    # Comparativa por turnos
    comparativa_turnos = serializers.ListField(child=serializers.DictField())
    
    # Rankings
    top_operarios = serializers.ListField(child=serializers.DictField())
    bottom_operarios = serializers.ListField(child=serializers.DictField())
    ranking_maquinas = serializers.ListField(child=serializers.DictField())
    
    # Incidencias
    estadisticas_incidencias = serializers.DictField()

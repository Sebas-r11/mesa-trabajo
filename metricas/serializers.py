"""
Serializers del modulo de Metricas para FLEX-OP

Este archivo contiene los serializers para convertir modelos de metricas
y produccion a JSON y viceversa.
"""
from rest_framework import serializers
from .models import RegistroProduccion, MetricaEficiencia, ObjetivoProduccion


class RegistroProduccionSerializer(serializers.ModelSerializer):
    # Serializer para registros de produccion
    """
    Serializer para convertir registros de produccion a JSON
    
    Incluye informacion de la asignacion y quien registro
    para tener contexto completo del registro.
    """
    
    # Informacion de la asignacion
    asignacion_info = serializers.SerializerMethodField()
    
    # Usuario que registro
    registrado_por_nombre = serializers.CharField(
        source='registrado_por.get_full_name', 
        read_only=True
    )
    
    class Meta:
        model = RegistroProduccion
        fields = [
            'id', 'asignacion', 'asignacion_info',
            'cantidad', 'fecha_hora', 'observaciones',
            'registrado_por', 'registrado_por_nombre'
        ]
        read_only_fields = ['id', 'fecha_hora']
    
    def get_asignacion_info(self, obj):
        """Retorna informacion basica de la asignacion"""
        return {
            'operario': obj.asignacion.operario.codigo_empleado,
            'maquina': obj.asignacion.maquina.codigo,
            'fecha': str(obj.asignacion.fecha)
        }


class RegistroProduccionCreateSerializer(serializers.ModelSerializer):
    # Serializer simplificado para crear registros
    """
    Serializer para crear nuevos registros de produccion
    
    Solo requiere la asignacion y la cantidad producida.
    """
    
    class Meta:
        model = RegistroProduccion
        fields = ['asignacion', 'cantidad', 'observaciones']
    
    def create(self, validated_data):
        """Asigna automaticamente el usuario que registra"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['registrado_por'] = request.user
        return super().create(validated_data)


class MetricaEficienciaSerializer(serializers.ModelSerializer):
    # Serializer para metricas de eficiencia
    """
    Serializer para convertir metricas de eficiencia a JSON
    
    Incluye informacion del operario y la maquina para
    proporcionar contexto completo de la metrica.
    """
    
    # Informacion del operario
    operario_nombre = serializers.CharField(
        source='operario.usuario.get_full_name', 
        read_only=True
    )
    operario_codigo = serializers.CharField(
        source='operario.codigo_empleado', 
        read_only=True
    )
    
    # Informacion de la maquina
    maquina_nombre = serializers.CharField(source='maquina.nombre', read_only=True)
    maquina_codigo = serializers.CharField(source='maquina.codigo', read_only=True)
    
    # Unidad de medida
    unidad = serializers.CharField(
        source='maquina.unidad_capacidad.abreviatura', 
        read_only=True
    )
    
    class Meta:
        model = MetricaEficiencia
        fields = [
            'id', 'operario', 'operario_nombre', 'operario_codigo',
            'maquina', 'maquina_nombre', 'maquina_codigo',
            'asignacion', 'fecha', 'fecha_calculo',
            'produccion_real', 'produccion_teorica', 'unidad',
            'horas_trabajadas', 'eficiencia_calculada'
        ]
        read_only_fields = ['id', 'fecha_calculo']


class ObjetivoProduccionSerializer(serializers.ModelSerializer):
    # Serializer para objetivos de produccion
    """
    Serializer para convertir objetivos de produccion a JSON
    
    Incluye informacion de la entidad objetivo (maquina, turno u operario)
    y el calculo de cumplimiento actual.
    """
    
    # Tipo en formato legible
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    # Nombres de entidades relacionadas
    maquina_nombre = serializers.CharField(
        source='maquina.nombre', 
        read_only=True,
        default=None
    )
    turno_nombre = serializers.CharField(
        source='turno.nombre', 
        read_only=True,
        default=None
    )
    operario_nombre = serializers.CharField(
        source='operario.usuario.get_full_name', 
        read_only=True,
        default=None
    )
    
    # Cumplimiento actual
    cumplimiento = serializers.SerializerMethodField()
    
    class Meta:
        model = ObjetivoProduccion
        fields = [
            'id', 'tipo', 'tipo_display',
            'maquina', 'maquina_nombre',
            'turno', 'turno_nombre',
            'operario', 'operario_nombre',
            'empresa', 'cantidad_objetivo',
            'fecha_inicio', 'fecha_fin',
            'activo', 'descripcion', 'cumplimiento'
        ]
        read_only_fields = ['id']
    
    def get_cumplimiento(self, obj):
        """Calcula y retorna el cumplimiento actual del objetivo"""
        return obj.calcular_cumplimiento()


class ResumenEficienciaSerializer(serializers.Serializer):
    # Serializer para resumenes de eficiencia
    """
    Serializer para resumenes agregados de eficiencia
    
    Se usa para devolver estadisticas calculadas, no datos de modelo.
    """
    
    fecha = serializers.DateField()
    eficiencia_promedio = serializers.DecimalField(max_digits=6, decimal_places=2)
    total_operarios = serializers.IntegerField()
    total_produccion = serializers.DecimalField(max_digits=12, decimal_places=2)
    mejor_operario = serializers.CharField()
    mejor_eficiencia = serializers.DecimalField(max_digits=6, decimal_places=2)

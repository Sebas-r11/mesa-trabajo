"""
Serializers del modulo de Alertas para FLEX-OP

Este archivo contiene los serializers para convertir modelos de alertas,
reglas y notificaciones a JSON y viceversa.
"""
from rest_framework import serializers
from .models import ReglaAlerta, Alerta, Notificacion


class ReglaAlertaSerializer(serializers.ModelSerializer):
    # Serializer para reglas de alerta
    """
    Serializer para convertir reglas de alerta a JSON
    
    Incluye el tipo y prioridad en formato legible,
    y un contador de alertas generadas por esta regla.
    """
    
    # Campos en formato legible
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    prioridad_display = serializers.CharField(source='get_prioridad_display', read_only=True)
    
    # Nombre de la empresa
    empresa_nombre = serializers.CharField(source='empresa.nombre', read_only=True)
    
    # Contador de alertas generadas
    total_alertas = serializers.IntegerField(source='alertas.count', read_only=True)
    
    class Meta:
        model = ReglaAlerta
        fields = [
            'id', 'nombre', 'descripcion',
            'tipo', 'tipo_display',
            'umbral', 'unidad_umbral',
            'prioridad', 'prioridad_display',
            'empresa', 'empresa_nombre',
            'activa', 'fecha_creacion', 'fecha_actualizacion',
            'total_alertas'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']


class AlertaSerializer(serializers.ModelSerializer):
    # Serializer para alertas
    """
    Serializer para convertir alertas a JSON
    
    Incluye informacion de la regla que la genero,
    y de las entidades relacionadas (operario, maquina, incidencia).
    """
    
    # Campos en formato legible
    prioridad_display = serializers.CharField(source='get_prioridad_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    # Regla que genero la alerta
    regla_nombre = serializers.CharField(source='regla.nombre', read_only=True)
    
    # Entidades relacionadas
    operario_nombre = serializers.CharField(
        source='operario_relacionado.usuario.get_full_name', 
        read_only=True,
        default=None
    )
    maquina_nombre = serializers.CharField(
        source='maquina_relacionada.nombre', 
        read_only=True,
        default=None
    )
    incidencia_titulo = serializers.CharField(
        source='incidencia_relacionada.titulo', 
        read_only=True,
        default=None
    )
    
    # Usuario que resolvio
    resuelta_por_nombre = serializers.CharField(
        source='resuelta_por.get_full_name', 
        read_only=True
    )
    
    class Meta:
        model = Alerta
        fields = [
            'id', 'regla', 'regla_nombre',
            'titulo', 'descripcion',
            'prioridad', 'prioridad_display',
            'estado', 'estado_display',
            'operario_relacionado', 'operario_nombre',
            'maquina_relacionada', 'maquina_nombre',
            'incidencia_relacionada', 'incidencia_titulo',
            'empresa', 'fecha_creacion', 'fecha_resolucion',
            'resuelta_por', 'resuelta_por_nombre',
            'notas_resolucion'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_resolucion']


class AlertaCreateSerializer(serializers.ModelSerializer):
    # Serializer simplificado para crear alertas manuales
    """
    Serializer para crear alertas manualmente
    
    Permite crear alertas sin necesidad de una regla.
    """
    
    class Meta:
        model = Alerta
        fields = [
            'titulo', 'descripcion', 'prioridad',
            'operario_relacionado', 'maquina_relacionada',
            'incidencia_relacionada', 'empresa'
        ]


class ResolverAlertaSerializer(serializers.Serializer):
    # Serializer para resolver alertas
    """
    Serializer para marcar una alerta como resuelta
    """
    
    notas = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Notas sobre como se resolvio la alerta'
    )


class NotificacionSerializer(serializers.ModelSerializer):
    # Serializer para notificaciones
    """
    Serializer para convertir notificaciones a JSON
    
    Incluye informacion de la alerta relacionada si existe.
    """
    
    # Alerta relacionada
    alerta_titulo = serializers.CharField(
        source='alerta.titulo', 
        read_only=True,
        default=None
    )
    
    class Meta:
        model = Notificacion
        fields = [
            'id', 'usuario', 'alerta', 'alerta_titulo',
            'titulo', 'mensaje',
            'leida', 'fecha_lectura', 'fecha_creacion'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_lectura']

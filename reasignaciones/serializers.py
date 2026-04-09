"""
Serializers del modulo de Reasignaciones para FLEX-OP

Este archivo contiene los serializers para convertir sugerencias
de reasignacion a JSON y viceversa.
"""
from rest_framework import serializers
from .models import SugerenciaReasignacion


class SugerenciaReasignacionSerializer(serializers.ModelSerializer):
    # Serializer para sugerencias de reasignacion
    """
    Serializer para convertir sugerencias de reasignacion a JSON
    
    Incluye informacion del operario y las maquinas involucradas
    para proporcionar contexto completo de la sugerencia.
    """
    
    # Campos en formato legible
    razon_display = serializers.CharField(source='get_razon_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    # Informacion del operario
    operario_nombre = serializers.CharField(
        source='operario.usuario.get_full_name', 
        read_only=True
    )
    operario_codigo = serializers.CharField(
        source='operario.codigo_empleado', 
        read_only=True
    )
    operario_eficiencia = serializers.DecimalField(
        source='operario.eficiencia_promedio',
        max_digits=5,
        decimal_places=2,
        read_only=True
    )
    
    # Informacion de la maquina origen
    maquina_origen_nombre = serializers.CharField(
        source='maquina_origen.nombre', 
        read_only=True,
        default=None
    )
    maquina_origen_codigo = serializers.CharField(
        source='maquina_origen.codigo', 
        read_only=True,
        default=None
    )
    
    # Informacion de la maquina destino
    maquina_destino_nombre = serializers.CharField(
        source='maquina_destino.nombre', 
        read_only=True
    )
    maquina_destino_codigo = serializers.CharField(
        source='maquina_destino.codigo', 
        read_only=True
    )
    
    # Usuario que decidio
    decidido_por_nombre = serializers.CharField(
        source='decidido_por.get_full_name', 
        read_only=True
    )
    
    class Meta:
        model = SugerenciaReasignacion
        fields = [
            'id', 
            'operario', 'operario_nombre', 'operario_codigo', 'operario_eficiencia',
            'maquina_origen', 'maquina_origen_nombre', 'maquina_origen_codigo',
            'maquina_destino', 'maquina_destino_nombre', 'maquina_destino_codigo',
            'razon', 'razon_display',
            'descripcion', 'impacto_estimado',
            'estado', 'estado_display',
            'empresa', 'fecha_creacion', 'fecha_decision',
            'decidido_por', 'decidido_por_nombre',
            'notas_decision', 'asignacion_creada'
        ]
        read_only_fields = [
            'id', 'fecha_creacion', 'fecha_decision', 
            'decidido_por', 'asignacion_creada'
        ]


class AceptarSugerenciaSerializer(serializers.Serializer):
    # Serializer para aceptar una sugerencia
    """
    Serializer para aceptar una sugerencia de reasignacion
    """
    
    notas = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Notas sobre por que se acepta la sugerencia'
    )


class RechazarSugerenciaSerializer(serializers.Serializer):
    # Serializer para rechazar una sugerencia
    """
    Serializer para rechazar una sugerencia de reasignacion
    """
    
    notas = serializers.CharField(
        required=True,
        help_text='Razon por la cual se rechaza la sugerencia'
    )

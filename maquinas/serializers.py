"""
Serializers del módulo de Máquinas para FLEX-OP
"""
from rest_framework import serializers
from .models import TipoMaquina, Maquina, UnidadEficiencia, EstadoMaquina


class TipoMaquinaSerializer(serializers.ModelSerializer):
    """Serializer para TipoMaquina"""
    
    total_maquinas = serializers.IntegerField(source='maquinas.count', read_only=True)
    empresa_nombre = serializers.CharField(source='empresa.nombre', read_only=True)
    
    class Meta:
        model = TipoMaquina
        fields = ['id', 'nombre', 'descripcion', 'empresa', 'empresa_nombre', 'total_maquinas']
        read_only_fields = ['id']


class UnidadEficienciaSerializer(serializers.ModelSerializer):
    """Serializer para UnidadEficiencia"""
    
    empresa_nombre = serializers.CharField(source='empresa.nombre', read_only=True)
    
    class Meta:
        model = UnidadEficiencia
        fields = ['id', 'nombre', 'abreviatura', 'descripcion', 'empresa', 'empresa_nombre']
        read_only_fields = ['id']


class MaquinaSerializer(serializers.ModelSerializer):
    """Serializer para Máquina"""
    
    tipo_nombre = serializers.CharField(source='tipo.nombre', read_only=True)
    unidad_nombre = serializers.CharField(source='unidad_capacidad.abreviatura', read_only=True)
    empresa_nombre = serializers.CharField(source='empresa.nombre', read_only=True)
    estado_display = serializers.CharField(source='get_estado_actual_display', read_only=True)
    
    class Meta:
        model = Maquina
        fields = [
            'id', 'codigo', 'nombre', 'tipo', 'tipo_nombre', 'empresa', 'empresa_nombre',
            'marca', 'modelo', 'numero_serie', 'ubicacion',
            'capacidad_teorica', 'unidad_capacidad', 'unidad_nombre',
            'estado_actual', 'estado_display', 'activa',
            'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']

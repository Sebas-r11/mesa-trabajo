"""
Serializer de Empresa para FLEX-OP
"""
from rest_framework import serializers
from .models import Empresa


class EmpresaSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Empresa"""
    
    total_usuarios = serializers.IntegerField(source='usuarios.count', read_only=True)
    total_maquinas = serializers.IntegerField(source='maquinas.count', read_only=True)
    
    class Meta:
        model = Empresa
        fields = [
            'id', 'nombre', 'razon_social', 'ruc', 'direccion',
            'telefono', 'email', 'logo', 'activa',
            'fecha_creacion', 'fecha_actualizacion',
            'total_usuarios', 'total_maquinas'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']

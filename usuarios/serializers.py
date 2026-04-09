"""
Serializers del módulo de Usuarios para FLEX-OP
"""
from rest_framework import serializers
from .models import User, Empresa


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


class UserSerializer(serializers.ModelSerializer):
    """Serializer para el modelo User"""
    
    empresa_nombre = serializers.CharField(source='empresa.nombre', read_only=True)
    rol_display = serializers.CharField(source='get_rol_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'rol', 'rol_display', 'telefono', 'foto_perfil', 
            'activo', 'fecha_ingreso', 'empresa', 'empresa_nombre',
            'es_operario', 'es_supervisor', 'es_gerente', 'es_admin'
        ]
        read_only_fields = ['id', 'fecha_ingreso', 'rol_display', 'empresa_nombre']
    
    def create(self, validated_data):
        """Crear usuario con contraseña hasheada"""
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear nuevos usuarios"""
    
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, label='Confirmar Contraseña', style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password2',
            'first_name', 'last_name', 'rol', 'telefono', 'empresa'
        ]
    
    def validate(self, attrs):
        """Validar que las contraseñas coincidan"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})
        return attrs
    
    def create(self, validated_data):
        """Crear usuario con contraseña hasheada"""
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar usuarios (sin contraseña)"""
    
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 
            'telefono', 'foto_perfil', 'activo'
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer para cambiar contraseña"""
    
    old_password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})
    new_password2 = serializers.CharField(required=True, write_only=True, label='Confirmar Nueva Contraseña', style={'input_type': 'password'})
    
    def validate(self, attrs):
        """Validar que las nuevas contraseñas coincidan"""
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Las nuevas contraseñas no coinciden."})
        return attrs

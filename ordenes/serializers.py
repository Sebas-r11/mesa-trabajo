"""
Serializers del modulo de Ordenes de Produccion para FLEX-OP

Este archivo contiene los serializers para ordenes de produccion y cola de despacho.
Las ordenes representan el trabajo que debe realizarse en planta.
"""
from rest_framework import serializers
from .models import OrdenProduccion, ColaDespacho


class OrdenProduccionSerializer(serializers.ModelSerializer):
    # Serializer para ordenes de produccion
    """
    Serializer para el modelo OrdenProduccion
    
    Las ordenes de produccion representan el trabajo que debe
    realizarse. Incluyen cantidad objetivo, fechas y prioridad.
    """
    
    # Campos de solo lectura calculados
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    cantidad_pendiente = serializers.SerializerMethodField()
    porcentaje_completado = serializers.SerializerMethodField()
    dias_restantes = serializers.SerializerMethodField()
    
    # Relaciones para mostrar nombres
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    maquina_nombre = serializers.CharField(source='maquina_asignada.nombre', read_only=True)
    
    class Meta:
        model = OrdenProduccion
        fields = [
            'id', 'numero_orden', 'empresa', 'producto', 'producto_nombre',
            'cantidad_solicitada', 'cantidad_producida', 'cantidad_pendiente',
            'porcentaje_completado', 'fecha_creacion', 'fecha_entrega_estimada',
            'dias_restantes', 'prioridad', 'estado', 'estado_display',
            'maquina_asignada', 'maquina_nombre', 'notas', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'numero_orden', 'cantidad_producida', 'created_at', 'updated_at']
    
    def get_cantidad_pendiente(self, obj):
        """Calcula la cantidad que falta por producir"""
        pendiente = obj.cantidad_solicitada - obj.cantidad_producida
        return max(0, pendiente)
    
    def get_porcentaje_completado(self, obj):
        """Calcula el porcentaje de avance de la orden"""
        if obj.cantidad_solicitada == 0:
            return 0
        return round((obj.cantidad_producida / obj.cantidad_solicitada) * 100, 2)
    
    def get_dias_restantes(self, obj):
        """Calcula los dias que faltan para la fecha de entrega"""
        from django.utils import timezone
        if not obj.fecha_entrega_estimada:
            return None
        delta = obj.fecha_entrega_estimada - timezone.now().date()
        return delta.days


class OrdenProduccionCreateSerializer(serializers.ModelSerializer):
    # Serializer para crear ordenes
    """
    Serializer simplificado para crear ordenes de produccion
    
    Incluye validaciones para asegurar que los datos son correctos.
    """
    
    class Meta:
        model = OrdenProduccion
        fields = [
            'empresa', 'producto', 'cantidad_solicitada',
            'fecha_entrega_estimada', 'prioridad', 'maquina_asignada', 'notas'
        ]
    
    def validate_cantidad_solicitada(self, value):
        """Valida que la cantidad sea positiva"""
        if value <= 0:
            raise serializers.ValidationError('La cantidad debe ser mayor a cero')
        return value
    
    def validate_fecha_entrega_estimada(self, value):
        """Valida que la fecha de entrega sea futura"""
        from django.utils import timezone
        if value and value < timezone.now().date():
            raise serializers.ValidationError('La fecha de entrega no puede ser en el pasado')
        return value


class OrdenProduccionListSerializer(serializers.ModelSerializer):
    # Serializer resumido para listados
    """
    Serializer resumido para listar ordenes de produccion
    
    Muestra solo la informacion esencial para listados rapidos.
    """
    
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    porcentaje = serializers.SerializerMethodField()
    
    class Meta:
        model = OrdenProduccion
        fields = [
            'id', 'numero_orden', 'producto', 'cantidad_solicitada',
            'cantidad_producida', 'porcentaje', 'fecha_entrega_estimada',
            'prioridad', 'estado', 'estado_display'
        ]
    
    def get_porcentaje(self, obj):
        """Porcentaje de avance"""
        if obj.cantidad_solicitada == 0:
            return 0
        return round((obj.cantidad_producida / obj.cantidad_solicitada) * 100, 1)


class ColaDespachoSerializer(serializers.ModelSerializer):
    # Serializer para cola de despacho
    """
    Serializer para el modelo ColaDespacho
    
    La cola de despacho organiza las ordenes completadas
    que estan listas para ser despachadas.
    """
    
    # Informacion de la orden
    orden_numero = serializers.CharField(source='orden.numero_orden', read_only=True)
    producto_nombre = serializers.CharField(source='orden.producto.nombre', read_only=True)
    cantidad = serializers.IntegerField(source='orden.cantidad_producida', read_only=True)
    
    class Meta:
        model = ColaDespacho
        fields = [
            'id', 'orden', 'orden_numero', 'producto_nombre', 'cantidad',
            'posicion_cola', 'fecha_ingreso_cola', 'despachado', 'fecha_despacho',
            'created_at'
        ]
        read_only_fields = ['id', 'fecha_ingreso_cola', 'created_at']


class ActualizarProduccionSerializer(serializers.Serializer):
    # Serializer para actualizar produccion de una orden
    """
    Serializer para actualizar la cantidad producida de una orden
    """
    
    cantidad = serializers.IntegerField(min_value=1)
    
    def validate_cantidad(self, value):
        """Valida que la cantidad sea positiva"""
        if value <= 0:
            raise serializers.ValidationError('La cantidad debe ser mayor a cero')
        return value

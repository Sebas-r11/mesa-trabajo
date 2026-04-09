"""
Serializers del modulo de Operaciones para FLEX-OP

Este archivo contiene los serializers para convertir modelos a JSON y viceversa.
Los serializers manejan la validacion y transformacion de datos para la API.
"""
from rest_framework import serializers
from .models import Turno, Habilidad, Operario, Asignacion, Evento, Incidencia


class TurnoSerializer(serializers.ModelSerializer):
    # Serializer para el modelo Turno
    """
    Serializer para convertir turnos a JSON
    
    Incluye el nombre de la empresa para facilitar la visualizacion
    sin necesidad de hacer consultas adicionales.
    """
    
    # Campo calculado que muestra el nombre de la empresa
    empresa_nombre = serializers.CharField(source='empresa.nombre', read_only=True)
    
    # Campo calculado para mostrar la duracion del turno
    duracion = serializers.SerializerMethodField()
    
    class Meta:
        model = Turno
        fields = [
            'id', 'nombre', 'hora_inicio', 'hora_fin', 
            'empresa', 'empresa_nombre', 'activo', 'duracion'
        ]
        read_only_fields = ['id']
    
    def get_duracion(self, obj):
        """Calcula y retorna la duracion del turno en horas"""
        return obj.duracion_horas()


class HabilidadSerializer(serializers.ModelSerializer):
    # Serializer para el modelo Habilidad
    """
    Serializer para convertir habilidades a JSON
    
    Incluye los nombres de los tipos de maquina asociados
    para mostrar informacion completa sin consultas adicionales.
    """
    
    # Campos calculados para mostrar informacion relacionada
    tipos_maquina_nombres = serializers.StringRelatedField(
        source='tipos_maquina', 
        many=True, 
        read_only=True
    )
    empresa_nombre = serializers.CharField(source='empresa.nombre', read_only=True)
    
    # Contador de operarios con esta habilidad
    total_operarios = serializers.IntegerField(source='operarios.count', read_only=True)
    
    class Meta:
        model = Habilidad
        fields = [
            'id', 'nombre', 'descripcion', 
            'empresa', 'empresa_nombre', 
            'tipos_maquina', 'tipos_maquina_nombres',
            'total_operarios'
        ]
        read_only_fields = ['id']


class OperarioSerializer(serializers.ModelSerializer):
    # Serializer para el modelo Operario
    """
    Serializer para convertir operarios a JSON
    
    Incluye informacion del usuario asociado y las habilidades
    para proporcionar una vista completa del operario.
    """
    
    # Informacion del usuario asociado
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)
    usuario_username = serializers.CharField(source='usuario.username', read_only=True)
    usuario_email = serializers.CharField(source='usuario.email', read_only=True)
    
    # Habilidades del operario
    habilidades_nombres = serializers.StringRelatedField(
        source='habilidades', 
        many=True, 
        read_only=True
    )
    
    # Informacion del turno
    turno_nombre = serializers.CharField(source='turno_actual.nombre', read_only=True)
    
    class Meta:
        model = Operario
        fields = [
            'id', 'usuario', 'usuario_nombre', 'usuario_username', 'usuario_email',
            'codigo_empleado', 'fecha_contratacion',
            'habilidades', 'habilidades_nombres',
            'turno_actual', 'turno_nombre',
            'disponible', 'activo',
            'eficiencia_promedio', 'total_tareas_completadas'
        ]
        read_only_fields = ['id', 'eficiencia_promedio', 'total_tareas_completadas']


class AsignacionSerializer(serializers.ModelSerializer):
    # Serializer para el modelo Asignacion
    """
    Serializer para convertir asignaciones a JSON
    
    Incluye informacion completa del operario, maquina y turno
    para mostrar toda la informacion relevante de la asignacion.
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
    
    # Informacion del turno
    turno_nombre = serializers.CharField(source='turno.nombre', read_only=True)
    
    # Estado en formato legible
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    # Duracion calculada
    duracion_minutos = serializers.SerializerMethodField()
    
    class Meta:
        model = Asignacion
        fields = [
            'id', 'operario', 'operario_nombre', 'operario_codigo',
            'maquina', 'maquina_nombre', 'maquina_codigo',
            'turno', 'turno_nombre',
            'fecha', 'hora_inicio_real', 'hora_fin_real',
            'estado', 'estado_display',
            'asignado_por', 'observaciones',
            'fecha_creacion', 'fecha_actualizacion',
            'duracion_minutos'
        ]
        read_only_fields = [
            'id', 'hora_inicio_real', 'hora_fin_real', 
            'fecha_creacion', 'fecha_actualizacion'
        ]
    
    def get_duracion_minutos(self, obj):
        """Retorna la duracion de la asignacion en minutos"""
        return obj.duracion_minutos()
    
    def validate(self, data):
        """
        Validacion personalizada para verificar:
        1. Que el operario tenga habilidad para la maquina
        2. Que el operario este disponible
        """
        operario = data.get('operario')
        maquina = data.get('maquina')
        
        if operario and maquina:
            if not operario.puede_operar(maquina):
                raise serializers.ValidationError({
                    'operario': f"El operario no tiene habilidad para operar {maquina.tipo.nombre}"
                })
        
        return data


class AsignacionCreateSerializer(serializers.ModelSerializer):
    # Serializer simplificado para crear asignaciones
    """
    Serializer para crear nuevas asignaciones
    
    Version simplificada que solo requiere los campos necesarios
    para crear una asignacion.
    """
    
    class Meta:
        model = Asignacion
        fields = [
            'operario', 'maquina', 'turno', 'fecha', 
            'observaciones'
        ]
    
    def validate(self, data):
        """Valida que el operario pueda operar la maquina"""
        operario = data.get('operario')
        maquina = data.get('maquina')
        
        if operario and maquina:
            if not operario.puede_operar(maquina):
                raise serializers.ValidationError({
                    'operario': f"El operario no tiene habilidad para operar {maquina.tipo.nombre}"
                })
        
        return data
    
    def create(self, validated_data):
        """Crea la asignacion con el usuario actual como asignador"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['asignado_por'] = request.user
        return super().create(validated_data)


class EventoSerializer(serializers.ModelSerializer):
    # Serializer para el modelo Evento
    """
    Serializer para convertir eventos a JSON
    
    Los eventos registran las acciones que ocurren durante una asignacion
    como inicios, pausas, finalizaciones e incidencias.
    """
    
    # Tipo en formato legible
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    # Informacion del usuario que registro
    registrado_por_nombre = serializers.CharField(
        source='registrado_por.get_full_name', 
        read_only=True
    )
    
    class Meta:
        model = Evento
        fields = [
            'id', 'asignacion', 'tipo', 'tipo_display',
            'fecha_hora', 'observaciones', 'datos_json',
            'registrado_por', 'registrado_por_nombre'
        ]
        read_only_fields = ['id', 'fecha_hora']


class IncidenciaSerializer(serializers.ModelSerializer):
    # Serializer para el modelo Incidencia
    """
    Serializer para convertir incidencias a JSON
    
    Las incidencias representan problemas que afectan la produccion
    y deben ser resueltos.
    """
    
    # Campos en formato legible
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    prioridad_display = serializers.CharField(source='get_prioridad_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    # Informacion de la maquina
    maquina_nombre = serializers.CharField(source='maquina.nombre', read_only=True)
    maquina_codigo = serializers.CharField(source='maquina.codigo', read_only=True)
    
    # Usuarios involucrados
    reportado_por_nombre = serializers.CharField(
        source='reportado_por.get_full_name', 
        read_only=True
    )
    resuelto_por_nombre = serializers.CharField(
        source='resuelto_por.get_full_name', 
        read_only=True
    )
    
    # Tiempo abierta
    tiempo_abierta = serializers.SerializerMethodField()
    
    class Meta:
        model = Incidencia
        fields = [
            'id', 'asignacion', 
            'maquina', 'maquina_nombre', 'maquina_codigo',
            'tipo', 'tipo_display',
            'prioridad', 'prioridad_display',
            'estado', 'estado_display',
            'titulo', 'descripcion',
            'fecha_reporte', 'fecha_resolucion',
            'reportado_por', 'reportado_por_nombre',
            'resuelto_por', 'resuelto_por_nombre',
            'solucion', 'tiempo_abierta'
        ]
        read_only_fields = ['id', 'fecha_reporte', 'fecha_resolucion']
    
    def get_tiempo_abierta(self, obj):
        """Retorna el tiempo que lleva abierta en minutos"""
        return obj.tiempo_abierta_minutos()


class IncidenciaCreateSerializer(serializers.ModelSerializer):
    # Serializer simplificado para crear incidencias
    """
    Serializer para reportar nuevas incidencias
    
    Solo requiere los campos necesarios para crear una incidencia.
    """
    
    class Meta:
        model = Incidencia
        fields = [
            'asignacion', 'maquina', 'tipo', 'prioridad',
            'titulo', 'descripcion'
        ]
    
    def create(self, validated_data):
        """Crea la incidencia con el usuario actual como reportador"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['reportado_por'] = request.user
        return super().create(validated_data)


class ResolverIncidenciaSerializer(serializers.Serializer):
    # Serializer para resolver una incidencia
    """
    Serializer para marcar una incidencia como resuelta
    
    Recibe la solucion aplicada para documentar como se resolvio.
    """
    
    solucion = serializers.CharField(
        required=True,
        help_text='Descripcion de como se resolvio la incidencia'
    )


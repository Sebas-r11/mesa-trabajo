"""
Modelos del módulo de Máquinas para FLEX-OP

Este módulo contiene los modelos relacionados con máquinas y equipos:
- TipoMaquina: Categorías de máquinas (Llenadora, Tractor, etc.)
- UnidadEficiencia: Unidades de medida (u/h, kg/h, ha/h)
- Maquina: Equipos productivos con estado y capacidad
- EstadoMaquina: Historial de cambios de estado
"""
from django.db import models
from django.utils import timezone


class TipoMaquina(models.Model):
    # Categoría o tipo de máquina industrial
    """
    Categoría o clasificación de máquinas industriales
    
    Agrupa máquinas por su función y características operativas:
    - Permite estandarizar configuraciones para máquinas del mismo tipo
    - Define qué habilidades son necesarias para operarlas
    - Facilita reportes y análisis por categoría de equipo
    
    Ejemplos de tipos:
    - Llenadora de líquidos
    - Etiquetadora automática
    - Empaquetadora de cajas
    - Cosechadora agrícola
    - Mezcladora industrial
    """
    
    # Nombre del tipo de máquina
    nombre = models.CharField(max_length=100, unique=True)
    
    # Descripción detallada del tipo y su uso
    descripcion = models.TextField(
        blank=True,
        help_text='Explicación del tipo de máquina y sus características'
    )
    
    # Empresa propietaria de este tipo
    empresa = models.ForeignKey(
        'usuarios.Empresa',
        on_delete=models.CASCADE,
        related_name='tipos_maquina'
    )
    
    class Meta:
        """Configuración del modelo en la base de datos"""
        db_table = 'tipos_maquina'
        verbose_name = 'Tipo de Máquina'
        verbose_name_plural = 'Tipos de Máquina'
        ordering = ['nombre']  # Orden alfabético
    
    def __str__(self):
        """Representación en texto: nombre del tipo"""
        return self.nombre


class UnidadEficiencia(models.Model):
    # Unidad de medida para capacidad y producción de máquinas
    """
    Unidad de medida para capacidad y producción de máquinas
    
    Permite estandarizar cómo se mide la producción de diferentes tipos de máquinas:
    - Llenadora: botellas/hora
    - Etiquetadora: unidades/hora
    - Cosechadora: hectáreas/hora
    - Empaquetadora: cajas/hora
    - Mezcladora: kilogramos/hora
    
    Cada máquina tiene una capacidad teórica en su unidad de medida,
    y la eficiencia se calcula comparando producción real vs teórica.
    """
    
    # Nombre descriptivo de la unidad
    # Ejemplos: "Unidades por Hora", "Kilogramos por Hora", "Hectáreas por Hora"
    nombre = models.CharField(max_length=100)
    
    # Abreviatura o símbolo de la unidad
    # Ejemplos: "u/h", "kg/h", "ha/h", "cajas/h"
    abreviatura = models.CharField(
        max_length=20,
        help_text='Símbolo corto de la unidad (ej: u/h, kg/h)'
    )
    
    # Descripción opcional con contexto de uso
    descripcion = models.TextField(
        blank=True,
        help_text='Explicación de cuándo usar esta unidad'
    )
    
    # Empresa propietaria de esta unidad
    empresa = models.ForeignKey(
        'usuarios.Empresa',
        on_delete=models.CASCADE,
        related_name='unidades_eficiencia'
    )
    
    class Meta:
        """Configuración del modelo en la base de datos"""
        db_table = 'unidades_eficiencia'
        verbose_name = 'Unidad de Eficiencia'
        verbose_name_plural = 'Unidades de Eficiencia'
        # Evitar unidades duplicadas por empresa
        unique_together = ['nombre', 'empresa']
        ordering = ['nombre']  # Orden alfabético
    
    def __str__(self):
        """Representación en texto: nombre (abreviatura)"""
        return f"{self.nombre} ({self.abreviatura})"


class Maquina(models.Model):
    # Representa una máquina productiva con estado y capacidad
    """
    Máquina o equipo productivo
    
    Almacena información de cada equipo de producción incluyendo:
    - Identificación y ubicación
    - Especificaciones técnicas (marca, modelo, serie)
    - Capacidad de producción teórica
    - Estado actual de operación
    - Control de actividad
    """
    
    class EstadoChoices(models.TextChoices):
        """
        Estados posibles de una máquina
        
        El estado determina si la máquina puede recibir asignaciones:
        - DISPONIBLE: Lista para ser asignada a un operario
        - OPERANDO: Actualmente en producción
        - MANTENIMIENTO: En mantenimiento preventivo o correctivo
        - PARADA: Detenida temporalmente (falla, falta de insumos, etc.)
        - FUERA_SERVICIO: Fuera de operación permanente
        """
        DISPONIBLE = 'DISPONIBLE', 'Disponible'
        OPERANDO = 'OPERANDO', 'Operando'
        MANTENIMIENTO = 'MANTENIMIENTO', 'En Mantenimiento'
        PARADA = 'PARADA', 'Parada'
        FUERA_SERVICIO = 'FUERA_SERVICIO', 'Fuera de Servicio'
    
    # Identificación única de la máquina
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200)
    
    # Relación con el tipo de máquina (Llenadora, Tractor, etc.)
    # PROTECT evita eliminar un tipo si hay máquinas asociadas
    tipo = models.ForeignKey(
        'TipoMaquina', 
        on_delete=models.PROTECT, 
        related_name='maquinas'
    )
    
    # Empresa propietaria de la máquina
    empresa = models.ForeignKey(
        'usuarios.Empresa', 
        on_delete=models.CASCADE, 
        related_name='maquinas'
    )
    
    # Especificaciones técnicas (opcionales)
    marca = models.CharField(max_length=100, blank=True)
    modelo = models.CharField(max_length=100, blank=True)
    numero_serie = models.CharField(max_length=100, blank=True)
    ubicacion = models.CharField(max_length=200, blank=True)
    
    # Capacidad de producción teórica
    # Por ejemplo: 300 unidades/hora, 5 hectáreas/hora, etc.
    capacidad_teorica = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Producción teórica por hora'
    )
    
    # Unidad de medida para la capacidad
    # PROTECT evita eliminar una unidad si está en uso
    unidad_capacidad = models.ForeignKey(
        'UnidadEficiencia',
        on_delete=models.PROTECT,
        related_name='maquinas'
    )
    
    # Estado actual de la máquina
    estado_actual = models.CharField(
        max_length=20,
        choices=EstadoChoices.choices,
        default=EstadoChoices.DISPONIBLE
    )
    
    # Control de actividad
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Configuración del modelo en la base de datos"""
        db_table = 'maquinas'
        verbose_name = 'Máquina'
        verbose_name_plural = 'Máquinas'
        ordering = ['codigo']
        
        # Índices para mejorar el rendimiento de consultas frecuentes
        indexes = [
            models.Index(fields=['estado_actual']),  # Consultas por estado
            models.Index(fields=['empresa', 'activa']),  # Consultas por empresa
        ]
    
    def __str__(self):
        """Representación en texto: código - nombre"""
        return f"{self.codigo} - {self.nombre}"
    
    def cambiar_estado(self, nuevo_estado, usuario=None, observacion=''):
        """
        Cambia el estado de la máquina y registra el cambio en el historial
        
        Args:
            nuevo_estado: Uno de los valores de EstadoChoices
            usuario: Usuario que realiza el cambio (opcional)
            observacion: Motivo o descripción del cambio (opcional)
            
        Returns:
            True si el cambio fue exitoso
            
        Ejemplo:
            maquina.cambiar_estado('MANTENIMIENTO', user, 'Mantenimiento preventivo mensual')
        """
        # Guardar el estado anterior para referencia
        estado_anterior = self.estado_actual
        
        # Actualizar al nuevo estado
        self.estado_actual = nuevo_estado
        self.save()
        
        # Crear registro en el historial de cambios
        EstadoMaquina.objects.create(
            maquina=self,
            estado=nuevo_estado,
            usuario=usuario,
            observacion=observacion
        )
        
        return True


class EstadoMaquina(models.Model):
    # Historial de cambios de estado de una máquina
    """
    Registro histórico de cambios de estado de máquinas
    
    Cada vez que una máquina cambia de estado (disponible → operando,
    operando → mantenimiento, etc.) se crea un registro en esta tabla.
    
    Esto permite:
    - Rastrear historial completo de estados de cada máquina
    - Calcular tiempo de operación efectiva vs paradas
    - Identificar patrones de fallas o mantenimiento
    - Auditar quién cambió el estado y cuándo
    - Generar reportes de disponibilidad de equipos
    
    Estados posibles (definidos en Maquina.EstadoChoices):
    - DISPONIBLE: Lista para operar, sin operario asignado
    - OPERANDO: En producción activa
    - MANTENIMIENTO: En servicio técnico programado o correctivo
    - PARADA: Detenida temporalmente por causas operativas
    - FUERA_SERVICIO: No disponible por tiempo indefinido
    """
    
    # Relación con la máquina cuyo estado cambió
    maquina = models.ForeignKey(
        'Maquina',
        on_delete=models.CASCADE,  # Si se elimina la máquina, se elimina su historial
        related_name='historial_estados'  # Acceso: maquina.historial_estados.all()
    )
    
    # Estado al que cambió la máquina
    # Se guarda como texto (choices) para mantener historial aunque cambien las opciones
    estado = models.CharField(max_length=20)
    
    # Fecha y hora exacta del cambio de estado
    fecha_hora = models.DateTimeField(
        default=timezone.now,
        help_text='Momento exacto del cambio de estado'
    )
    
    # Usuario que realizó el cambio (puede ser supervisor o gerente)
    usuario = models.ForeignKey(
        'usuarios.User',
        on_delete=models.SET_NULL,  # Si se elimina el usuario, mantener el registro
        null=True,
        blank=True
    )
    
    # Notas o comentarios sobre el cambio
    # Ejemplos: "Mantenimiento preventivo programado", "Parada por falta de materia prima"
    observacion = models.TextField(
        blank=True,
        help_text='Motivo o comentarios sobre el cambio de estado'
    )
    
    class Meta:
        """Configuración del modelo en la base de datos"""
        db_table = 'estados_maquina'
        verbose_name = 'Estado de Máquina'
        verbose_name_plural = 'Estados de Máquina'
        
        # Ordenar por fecha más reciente primero
        ordering = ['-fecha_hora']
        
        # Índices para optimizar consultas comunes
        indexes = [
            models.Index(fields=['maquina', 'fecha_hora']),  # Historial de una máquina
        ]
    
    def __str__(self):
        """Representación en texto: máquina - estado (fecha)"""
        return f"{self.maquina} - {self.estado} ({self.fecha_hora.strftime('%d/%m/%Y %H:%M')})"
    
    def duracion(self):
        """
        Calcula cuánto tiempo duró este estado antes del siguiente cambio
        
        Útil para análisis de tiempos:
        - ¿Cuánto tiempo operó sin parar?
        - ¿Cuánto duró el mantenimiento?
        - ¿Cuánto tiempo estuvo parada?
        
        Returns:
            timedelta: Duración del estado, o None si es el estado actual (sin fin)
            
        Ejemplo:
            estado = EstadoMaquina.objects.get(id=123)
            duracion = estado.duracion()
            if duracion:
                horas = duracion.total_seconds() / 3600
                print(f"Duró {horas:.1f} horas en {estado.estado}")
        """
        # Buscar el siguiente cambio de estado de esta máquina
        siguiente = EstadoMaquina.objects.filter(
            maquina=self.maquina,
            fecha_hora__gt=self.fecha_hora  # Mayor que (después de) este cambio
        ).order_by('fecha_hora').first()
        
        # Si existe un estado siguiente, calcular diferencia
        if siguiente:
            return siguiente.fecha_hora - self.fecha_hora
        
        # Si no hay siguiente estado, este es el estado actual (sin duración definida)
        return None

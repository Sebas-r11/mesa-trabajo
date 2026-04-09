"""
Modelos del módulo de Operaciones para FLEX-OP

Este módulo contiene los modelos relacionados con operaciones, personal y turnos:
- Turno: Turnos de trabajo (mañana, tarde, noche)
- Habilidad: Competencias técnicas de operarios
- Operario: Perfil extendido de operarios con habilidades y métricas
"""
from django.db import models


class Turno(models.Model):
    # Turno de trabajo para organizar operarios
    """
    Turno de trabajo para organización de operarios
    
    Los turnos permiten:
    - Organizar el personal en diferentes horarios
    - Planificar asignaciones de máquinas según disponibilidad
    - Calcular eficiencia por turno
    - Generar reportes de producción por periodo
    
    Ejemplos comunes:
    - Turno Mañana: 06:00 - 14:00
    - Turno Tarde: 14:00 - 22:00
    - Turno Noche: 22:00 - 06:00
    """
    
    # Nombre descriptivo del turno
    # Ejemplos: "Turno Mañana", "Turno A", "Primer Turno"
    nombre = models.CharField(max_length=100)
    
    # Horarios del turno
    hora_inicio = models.TimeField(help_text='Hora de inicio del turno (ej: 06:00)')
    hora_fin = models.TimeField(help_text='Hora de fin del turno (ej: 14:00)')
    
    # Empresa propietaria del turno
    empresa = models.ForeignKey(
        'usuarios.Empresa',
        on_delete=models.CASCADE,
        related_name='turnos'
    )
    
    # Estado de vigencia
    activo = models.BooleanField(
        default=True,
        help_text='Si está inactivo, no se puede asignar a operarios'
    )
    
    class Meta:
        """Configuración del modelo en la base de datos"""
        db_table = 'turnos'
        verbose_name = 'Turno'
        verbose_name_plural = 'Turnos'
        ordering = ['hora_inicio']  # Ordenar por hora de inicio
    
    def __str__(self):
        """Representación en texto: nombre (hora_inicio - hora_fin)"""
        return f"{self.nombre} ({self.hora_inicio.strftime('%H:%M')} - {self.hora_fin.strftime('%H:%M')})"
    
    def duracion_horas(self):
        """
        Calcula la duración del turno en horas
        
        Maneja correctamente turnos que cruzan medianoche (ej: 22:00 - 06:00)
        
        Returns:
            float: Duración del turno en horas (ej: 8.0, 8.5)
            
        Ejemplo:
            turno_manana = Turno(hora_inicio=time(6,0), hora_fin=time(14,0))
            print(turno_manana.duracion_horas())  # 8.0
        """
        from datetime import datetime, timedelta
        
        # Crear objetos datetime para hacer la resta
        inicio = datetime.combine(datetime.today(), self.hora_inicio)
        fin = datetime.combine(datetime.today(), self.hora_fin)
        
        # Si el turno cruza medianoche, agregar un día a la hora de fin
        if fin < inicio:
            fin += timedelta(days=1)
        
        # Calcular diferencia y convertir a horas
        duracion = fin - inicio
        return duracion.total_seconds() / 3600


class Habilidad(models.Model):
    # Competencia técnica que puede tener un operario
    """
    Habilidad técnica requerida para operar máquinas
    
    Las habilidades permiten:
    - Definir qué operarios pueden manejar qué tipos de máquinas
    - Garantizar seguridad al asignar solo personal capacitado
    - Rastrear certificaciones y competencias del personal
    
    Relaciones:
    - ManyToMany con TipoMaquina: una habilidad puede aplicar a varios tipos de máquinas
    - ManyToMany con Operario: un operario puede tener varias habilidades
    """
    
    # Nombre de la habilidad
    # Ejemplos: "Operador de Llenadora", "Certificado en Empaquetado", "Manejo de Montacargas"
    nombre = models.CharField(max_length=100)
    
    # Descripción detallada de la competencia
    descripcion = models.TextField(blank=True)
    
    # Empresa propietaria de esta habilidad
    empresa = models.ForeignKey(
        'usuarios.Empresa',
        on_delete=models.CASCADE,
        related_name='habilidades'
    )
    
    # Relación muchos a muchos con tipos de máquinas
    # Una habilidad puede ser requerida por varios tipos de máquinas
    # Un tipo de máquina puede requerir varias habilidades
    tipos_maquina = models.ManyToManyField(
        'maquinas.TipoMaquina',
        related_name='habilidades_requeridas',  # Acceso inverso: tipo.habilidades_requeridas.all()
        blank=True,
        help_text='Tipos de máquinas que requieren esta habilidad'
    )
    
    class Meta:
        """Configuración del modelo en la base de datos"""
        db_table = 'habilidades'
        verbose_name = 'Habilidad'
        verbose_name_plural = 'Habilidades'
        # Evitar habilidades duplicadas por empresa
        unique_together = ['nombre', 'empresa']
        ordering = ['nombre']  # Orden alfabético
    
    def __str__(self):
        """Representación en texto: nombre de la habilidad"""
        return self.nombre


class Operario(models.Model):
    # Perfil de operario con habilidades, turno y métricas
    """
    Perfil extendido de operarios con sus habilidades y métricas
    
    Almacena información adicional de los operarios más allá del usuario base:
    - Código de empleado para identificación interna
    - Habilidades para operar diferentes tipos de máquinas
    - Turno de trabajo asignado
    - Métricas históricas de desempeño
    """
    
    # Relación uno a uno con el usuario
    # Limita a solo usuarios con rol OPERARIO
    usuario = models.OneToOneField(
        'usuarios.User',
        on_delete=models.CASCADE,
        related_name='perfil_operario',  # Acceso: user.perfil_operario
        limit_choices_to={'rol': 'OPERARIO'}  # Solo permite usuarios operarios
    )
    
    # Información laboral
    codigo_empleado = models.CharField(max_length=50, unique=True)
    fecha_contratacion = models.DateField()
    
    # Relación muchos a muchos con habilidades
    # Un operario puede tener varias habilidades
    # Una habilidad puede ser poseída por varios operarios
    habilidades = models.ManyToManyField(
        'Habilidad',
        related_name='operarios',  # Acceso inverso: habilidad.operarios.all()
        blank=True
    )
    
    # Turno de trabajo actual del operario
    turno_actual = models.ForeignKey(
        'Turno',
        on_delete=models.SET_NULL,  # Si se elimina el turno, se pone en null
        null=True,
        blank=True,
        related_name='operarios_asignados'
    )
    
    # Estado de disponibilidad
    disponible = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)
    
    # Métricas acumuladas históricas
    # Estos valores se calculan automáticamente desde las métricas de eficiencia
    eficiencia_promedio = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text='Eficiencia promedio histórica (%)'
    )
    total_tareas_completadas = models.IntegerField(default=0)
    
    class Meta:
        """Configuración del modelo en la base de datos"""
        db_table = 'operarios'
        verbose_name = 'Operario'
        verbose_name_plural = 'Operarios'
        ordering = ['codigo_empleado']
    
    def __str__(self):
        """Representación en texto: código - nombre completo"""
        return f"{self.codigo_empleado} - {self.usuario.get_full_name()}"
    
    def puede_operar(self, maquina):
        """
        Verifica si el operario tiene las habilidades necesarias para operar una máquina
        
        Lógica:
        1. Si el tipo de máquina no requiere habilidades específicas, cualquiera puede operar
        2. Si requiere habilidades, verifica que el operario tenga al menos una de ellas
        
        Args:
            maquina: Instancia del modelo Maquina a verificar
            
        Returns:
            True si puede operar la máquina, False si no
            
        Ejemplo:
            if operario.puede_operar(maquina_llenadora):
                asignar_operario_a_maquina(operario, maquina_llenadora)
        """
        # Obtener habilidades requeridas por el tipo de máquina
        habilidades_requeridas = maquina.tipo.habilidades_requeridas.all()
        
        # Obtener habilidades que posee el operario
        habilidades_operario = self.habilidades.all()
        
        # Si el tipo de máquina no requiere habilidades específicas, todos pueden operar
        if not habilidades_requeridas.exists():
            return True
        
        # Verificar si el operario tiene al menos una habilidad requerida
        # Busca intersección entre habilidades requeridas y habilidades del operario
        return habilidades_requeridas.filter(id__in=habilidades_operario).exists()
    
    def actualizar_eficiencia_promedio(self):
        """
        Recalcula la eficiencia promedio basada en todas las métricas históricas
        
        Este método se llama después de crear nuevas métricas de eficiencia
        para mantener actualizado el promedio histórico del operario.
        
        No retorna nada, actualiza el campo eficiencia_promedio directamente.
        """
        # Importación diferida para evitar imports circulares
        from metricas.models import MetricaEficiencia
        
        # Obtener todas las métricas de este operario
        metricas = MetricaEficiencia.objects.filter(operario=self)
        
        if metricas.exists():
            # Calcular promedio usando aggregate de Django
            promedio = metricas.aggregate(
                models.Avg('eficiencia_calculada')
            )['eficiencia_calculada__avg']
            
            # Actualizar el campo con el promedio o 0 si es None
            self.eficiencia_promedio = promedio or 0
            self.save()


class Asignacion(models.Model):
    # Representa la asignacion de un operario a una maquina en un turno especifico
    """
    Asignacion de un operario a una maquina en un turno especifico
    
    Las asignaciones son el nucleo operativo del sistema porque:
    - Vinculan operarios con maquinas en fechas y turnos especificos
    - Controlan que un operario no tenga multiples asignaciones simultaneas
    - Registran tiempos reales de inicio y fin de operaciones
    - Permiten calcular eficiencia y generar metricas
    
    Estados de una asignacion:
    - PENDIENTE: Creada pero no iniciada (operario aun no comienza)
    - ACTIVA: Operario trabajando activamente en la maquina
    - COMPLETADA: Tarea finalizada normalmente
    - CANCELADA: Asignacion cancelada antes de completarse
    """
    
    class EstadoChoices(models.TextChoices):
        """Estados posibles de una asignacion"""
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        ACTIVA = 'ACTIVA', 'Activa'
        COMPLETADA = 'COMPLETADA', 'Completada'
        CANCELADA = 'CANCELADA', 'Cancelada'
    
    # Relacion con el operario asignado
    operario = models.ForeignKey(
        'Operario',
        on_delete=models.PROTECT,  # No eliminar operarios con asignaciones
        related_name='asignaciones'
    )
    
    # Relacion con la maquina asignada
    maquina = models.ForeignKey(
        'maquinas.Maquina',
        on_delete=models.PROTECT,  # No eliminar maquinas con asignaciones
        related_name='asignaciones'
    )
    
    # Relacion con el turno de trabajo
    turno = models.ForeignKey(
        'Turno',
        on_delete=models.PROTECT,
        related_name='asignaciones'
    )
    
    # Fecha de la asignacion (sin hora, solo dia)
    fecha = models.DateField(
        help_text='Fecha para la cual se crea esta asignacion'
    )
    
    # Tiempos reales de operacion (se llenan cuando inicia/termina)
    hora_inicio_real = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Momento exacto en que el operario inicio la tarea'
    )
    hora_fin_real = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Momento exacto en que el operario termino la tarea'
    )
    
    # Estado actual de la asignacion
    estado = models.CharField(
        max_length=20,
        choices=EstadoChoices.choices,
        default=EstadoChoices.PENDIENTE
    )
    
    # Usuario que creo la asignacion (supervisor o gerente)
    asignado_por = models.ForeignKey(
        'usuarios.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='asignaciones_creadas'
    )
    
    # Notas o comentarios sobre la asignacion
    observaciones = models.TextField(blank=True)
    
    # Campos de auditoria
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Configuracion del modelo en la base de datos"""
        db_table = 'asignaciones'
        verbose_name = 'Asignacion'
        verbose_name_plural = 'Asignaciones'
        ordering = ['-fecha', '-fecha_creacion']
        
        # Indices para optimizar consultas frecuentes
        indexes = [
            models.Index(fields=['fecha', 'estado']),
            models.Index(fields=['operario', 'fecha']),
            models.Index(fields=['maquina', 'fecha']),
        ]
    
    def __str__(self):
        """Representacion en texto: operario hacia maquina (fecha)"""
        return f"{self.operario} -> {self.maquina} ({self.fecha})"
    
    def clean(self):
        """
        Validaciones personalizadas antes de guardar
        
        Verifica:
        1. Que el operario tenga habilidad para operar la maquina
        2. Que el operario no tenga otra asignacion activa el mismo dia
        """
        from django.core.exceptions import ValidationError
        
        # Validar habilidad del operario para la maquina
        if self.operario and self.maquina:
            if not self.operario.puede_operar(self.maquina):
                raise ValidationError(
                    f"El operario {self.operario} no tiene habilidad para operar {self.maquina.tipo.nombre}"
                )
        
        # Validar que no haya otra asignacion activa para el mismo operario
        if self.estado == self.EstadoChoices.ACTIVA:
            asignaciones_activas = Asignacion.objects.filter(
                operario=self.operario,
                estado=self.EstadoChoices.ACTIVA,
                fecha=self.fecha
            ).exclude(id=self.id)
            
            if asignaciones_activas.exists():
                raise ValidationError(
                    f"El operario {self.operario} ya tiene una asignacion activa para esta fecha"
                )
    
    def iniciar(self):
        """
        Inicia la asignacion marcandola como activa
        
        Acciones que realiza:
        1. Cambia el estado de PENDIENTE a ACTIVA
        2. Registra la hora real de inicio
        3. Cambia el estado de la maquina a OPERANDO
        4. Crea un evento de tipo INICIO
        
        Raises:
            ValidationError: Si la asignacion no esta en estado PENDIENTE
            
        Returns:
            True si se inicio correctamente
        """
        from django.core.exceptions import ValidationError
        from django.utils import timezone
        
        if self.estado != self.EstadoChoices.PENDIENTE:
            raise ValidationError("Solo se pueden iniciar asignaciones pendientes")
        
        # Actualizar estado y hora de inicio
        self.estado = self.EstadoChoices.ACTIVA
        self.hora_inicio_real = timezone.now()
        
        # Cambiar estado de la maquina a operando
        self.maquina.cambiar_estado(
            'OPERANDO',
            usuario=self.operario.usuario,
            observacion=f"Iniciado por asignacion #{self.id}"
        )
        
        # Marcar operario como no disponible
        self.operario.disponible = False
        self.operario.save()
        
        self.save()
        
        # Crear evento de inicio
        Evento.objects.create(
            asignacion=self,
            tipo=Evento.TipoEventoChoices.INICIO,
            registrado_por=self.operario.usuario,
            observaciones=f"Inicio de tarea en {self.maquina}"
        )
        
        return True
    
    def finalizar(self):
        """
        Finaliza la asignacion marcandola como completada
        
        Acciones que realiza:
        1. Cambia el estado de ACTIVA a COMPLETADA
        2. Registra la hora real de finalizacion
        3. Cambia el estado de la maquina a DISPONIBLE
        4. Incrementa el contador de tareas completadas del operario
        5. Crea un evento de tipo FIN
        
        Raises:
            ValidationError: Si la asignacion no esta en estado ACTIVA
            
        Returns:
            True si se finalizo correctamente
        """
        from django.core.exceptions import ValidationError
        from django.utils import timezone
        
        if self.estado != self.EstadoChoices.ACTIVA:
            raise ValidationError("Solo se pueden finalizar asignaciones activas")
        
        # Actualizar estado y hora de fin
        self.estado = self.EstadoChoices.COMPLETADA
        self.hora_fin_real = timezone.now()
        
        # Cambiar estado de la maquina a disponible
        self.maquina.cambiar_estado(
            'DISPONIBLE',
            usuario=self.operario.usuario,
            observacion=f"Finalizado por asignacion #{self.id}"
        )
        
        # Actualizar metricas del operario
        self.operario.disponible = True
        self.operario.total_tareas_completadas += 1
        self.operario.save()
        
        self.save()
        
        # Crear evento de fin
        Evento.objects.create(
            asignacion=self,
            tipo=Evento.TipoEventoChoices.FIN,
            registrado_por=self.operario.usuario,
            observaciones=f"Fin de tarea en {self.maquina}"
        )
        
        return True
    
    def duracion_minutos(self):
        """
        Calcula la duracion de la asignacion en minutos
        
        Returns:
            int: Minutos de duracion, o None si no ha finalizado
        """
        if self.hora_inicio_real and self.hora_fin_real:
            duracion = self.hora_fin_real - self.hora_inicio_real
            return int(duracion.total_seconds() / 60)
        return None


class Evento(models.Model):
    # Registra eventos operacionales como inicio, fin, pausas e incidencias
    """
    Registro de eventos operacionales durante una asignacion
    
    Los eventos permiten:
    - Rastrear el historial completo de cada asignacion
    - Calcular tiempos efectivos de trabajo vs pausas
    - Identificar incidencias y su impacto en la produccion
    - Generar reportes detallados de actividades
    
    Tipos de eventos:
    - INICIO: Cuando el operario comienza a trabajar
    - FIN: Cuando el operario termina la tarea
    - PAUSA: Cuando se detiene temporalmente (descanso, etc)
    - REANUDACION: Cuando se retoma despues de una pausa
    - CAMBIO_MAQUINA: Cuando se reasigna a otra maquina
    - INCIDENCIA: Cuando ocurre un problema
    """
    
    class TipoEventoChoices(models.TextChoices):
        """Tipos de eventos operacionales"""
        INICIO = 'INICIO', 'Inicio de Tarea'
        FIN = 'FIN', 'Fin de Tarea'
        PAUSA = 'PAUSA', 'Pausa'
        REANUDACION = 'REANUDACION', 'Reanudacion'
        CAMBIO_MAQUINA = 'CAMBIO_MAQUINA', 'Cambio de Maquina'
        INCIDENCIA = 'INCIDENCIA', 'Incidencia Reportada'
    
    # Relacion con la asignacion donde ocurrio el evento
    asignacion = models.ForeignKey(
        'Asignacion',
        on_delete=models.CASCADE,
        related_name='eventos'
    )
    
    # Tipo de evento
    tipo = models.CharField(
        max_length=20,
        choices=TipoEventoChoices.choices
    )
    
    # Momento en que ocurrio el evento
    fecha_hora = models.DateTimeField(auto_now_add=True)
    
    # Notas o comentarios del evento
    observaciones = models.TextField(blank=True)
    
    # Datos adicionales en formato JSON (flexible para diferentes tipos de eventos)
    datos_json = models.JSONField(
        null=True,
        blank=True,
        help_text='Datos adicionales en formato JSON'
    )
    
    # Usuario que registro el evento
    registrado_por = models.ForeignKey(
        'usuarios.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='eventos_registrados'
    )
    
    class Meta:
        """Configuracion del modelo en la base de datos"""
        db_table = 'eventos'
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['-fecha_hora']
        
        indexes = [
            models.Index(fields=['asignacion', 'tipo']),
            models.Index(fields=['fecha_hora']),
        ]
    
    def __str__(self):
        """Representacion en texto: tipo - asignacion (hora)"""
        return f"{self.get_tipo_display()} - {self.asignacion} ({self.fecha_hora.strftime('%H:%M')})"


class Incidencia(models.Model):
    # Registra problemas o incidencias que afectan la produccion
    """
    Registro de incidencias o problemas durante la operacion
    
    Las incidencias permiten:
    - Documentar problemas que afectan la produccion
    - Calcular tiempos de parada no planificada
    - Generar estadisticas de tipos de problemas
    - Escalar automaticamente segun prioridad y tiempo sin resolver
    
    Tipos de incidencias:
    - FALLA_MAQUINA: Problemas mecanicos o tecnicos del equipo
    - FALTA_MATERIAL: No hay insumos para continuar
    - PROBLEMA_CALIDAD: Producto no cumple especificaciones
    - OTRO: Cualquier otra situacion no categorizada
    """
    
    class TipoChoices(models.TextChoices):
        """Tipos de incidencias"""
        FALLA_MAQUINA = 'FALLA_MAQUINA', 'Falla de Maquina'
        FALTA_MATERIAL = 'FALTA_MATERIAL', 'Falta de Material'
        PROBLEMA_CALIDAD = 'PROBLEMA_CALIDAD', 'Problema de Calidad'
        OTRO = 'OTRO', 'Otro'
    
    class PrioridadChoices(models.TextChoices):
        """Niveles de prioridad"""
        BAJA = 'BAJA', 'Baja'
        MEDIA = 'MEDIA', 'Media'
        ALTA = 'ALTA', 'Alta'
        CRITICA = 'CRITICA', 'Critica'
    
    class EstadoChoices(models.TextChoices):
        """Estados de la incidencia"""
        ABIERTA = 'ABIERTA', 'Abierta'
        EN_PROCESO = 'EN_PROCESO', 'En Proceso'
        RESUELTA = 'RESUELTA', 'Resuelta'
        ESCALADA = 'ESCALADA', 'Escalada'
    
    # Relacion con la asignacion donde ocurrio (opcional)
    asignacion = models.ForeignKey(
        'Asignacion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incidencias'
    )
    
    # Relacion con la maquina afectada
    maquina = models.ForeignKey(
        'maquinas.Maquina',
        on_delete=models.CASCADE,
        related_name='incidencias'
    )
    
    # Clasificacion de la incidencia
    tipo = models.CharField(
        max_length=20,
        choices=TipoChoices.choices
    )
    
    prioridad = models.CharField(
        max_length=20,
        choices=PrioridadChoices.choices,
        default=PrioridadChoices.MEDIA
    )
    
    estado = models.CharField(
        max_length=20,
        choices=EstadoChoices.choices,
        default=EstadoChoices.ABIERTA
    )
    
    # Descripcion del problema
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    
    # Tiempos de la incidencia
    fecha_reporte = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    
    # Usuarios involucrados
    reportado_por = models.ForeignKey(
        'usuarios.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='incidencias_reportadas'
    )
    
    resuelto_por = models.ForeignKey(
        'usuarios.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incidencias_resueltas'
    )
    
    # Solucion aplicada (cuando se resuelve)
    solucion = models.TextField(blank=True)
    
    class Meta:
        """Configuracion del modelo en la base de datos"""
        db_table = 'incidencias'
        verbose_name = 'Incidencia'
        verbose_name_plural = 'Incidencias'
        ordering = ['-fecha_reporte']
        
        indexes = [
            models.Index(fields=['estado', 'prioridad']),
            models.Index(fields=['maquina', 'fecha_reporte']),
        ]
    
    def __str__(self):
        """Representacion en texto: titulo (estado)"""
        return f"{self.titulo} ({self.get_estado_display()})"
    
    def resolver(self, usuario, solucion):
        """
        Marca la incidencia como resuelta
        
        Args:
            usuario: Usuario que resuelve la incidencia
            solucion: Descripcion de como se resolvio el problema
        """
        from django.utils import timezone
        
        self.estado = self.EstadoChoices.RESUELTA
        self.resuelto_por = usuario
        self.solucion = solucion
        self.fecha_resolucion = timezone.now()
        self.save()
    
    def tiempo_abierta_minutos(self):
        """
        Calcula cuanto tiempo lleva abierta la incidencia
        
        Returns:
            int: Minutos desde que se reporto hasta ahora o hasta que se resolvio
        """
        from django.utils import timezone
        
        fin = self.fecha_resolucion or timezone.now()
        duracion = fin - self.fecha_reporte
        return int(duracion.total_seconds() / 60)

"""
Modelos del modulo de Metricas para FLEX-OP

Este modulo contiene los modelos relacionados con eficiencia y produccion:
- RegistroProduccion: Registra unidades producidas por asignacion
- MetricaEficiencia: Almacena calculos de eficiencia por operario/maquina
- ObjetivoProduccion: Define metas de produccion por maquina o turno
"""
from django.db import models
from django.utils import timezone
from decimal import Decimal


class RegistroProduccion(models.Model):
    # Registro de unidades producidas durante una asignacion
    """
    Registro de produccion realizada durante una asignacion
    
    Permite registrar la cantidad producida en una asignacion especifica:
    - Puede haber multiples registros por asignacion (parciales)
    - Se suma al total de produccion de la asignacion
    - Sirve como base para calcular eficiencia
    
    La eficiencia se calcula como:
    Eficiencia = (Produccion Real / Produccion Teorica) * 100
    
    Donde Produccion Teorica = Capacidad de Maquina * Horas Trabajadas
    """
    
    # Relacion con la asignacion donde se produjo
    asignacion = models.ForeignKey(
        'operaciones.Asignacion',
        on_delete=models.CASCADE,
        related_name='registros_produccion'
    )
    
    # Cantidad producida (en la unidad de la maquina)
    cantidad = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text='Cantidad producida en la unidad de la maquina'
    )
    
    # Momento del registro
    fecha_hora = models.DateTimeField(default=timezone.now)
    
    # Notas sobre este registro de produccion
    observaciones = models.TextField(blank=True)
    
    # Usuario que registro la produccion
    registrado_por = models.ForeignKey(
        'usuarios.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='registros_produccion'
    )
    
    class Meta:
        """Configuracion del modelo en la base de datos"""
        db_table = 'registros_produccion'
        verbose_name = 'Registro de Produccion'
        verbose_name_plural = 'Registros de Produccion'
        ordering = ['-fecha_hora']
        
        indexes = [
            models.Index(fields=['asignacion', 'fecha_hora']),
        ]
    
    def __str__(self):
        """Representacion en texto: cantidad - asignacion"""
        return f"{self.cantidad} - {self.asignacion}"


class MetricaEficiencia(models.Model):
    # Calculo de eficiencia de un operario en una asignacion
    """
    Metrica de eficiencia calculada para una asignacion
    
    Almacena el calculo de eficiencia de un operario en una maquina:
    - Se genera automaticamente al finalizar una asignacion
    - Tambien puede generarse periodicamente para asignaciones en curso
    
    Formula de eficiencia:
    Eficiencia = (Produccion Real / Produccion Teorica) * 100
    
    Donde:
    - Produccion Real = Suma de registros de produccion de la asignacion
    - Produccion Teorica = Capacidad de Maquina por Hora * Horas Trabajadas
    
    La eficiencia puede ser mayor a 100 si se supera la capacidad teorica
    """
    
    # Relacion con operario evaluado
    operario = models.ForeignKey(
        'operaciones.Operario',
        on_delete=models.CASCADE,
        related_name='metricas_eficiencia'
    )
    
    # Relacion con maquina usada
    maquina = models.ForeignKey(
        'maquinas.Maquina',
        on_delete=models.CASCADE,
        related_name='metricas_eficiencia'
    )
    
    # Relacion con la asignacion (opcional, para metricas historicas)
    asignacion = models.ForeignKey(
        'operaciones.Asignacion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='metricas_eficiencia'
    )
    
    # Fecha y hora del calculo
    fecha = models.DateField()
    fecha_calculo = models.DateTimeField(auto_now_add=True)
    
    # Valores usados en el calculo
    produccion_real = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text='Total producido'
    )
    
    produccion_teorica = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text='Produccion esperada segun capacidad de maquina'
    )
    
    horas_trabajadas = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text='Horas efectivas de trabajo'
    )
    
    # Resultado del calculo
    eficiencia_calculada = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text='Porcentaje de eficiencia (100 = 100%)'
    )
    
    class Meta:
        """Configuracion del modelo en la base de datos"""
        db_table = 'metricas_eficiencia'
        verbose_name = 'Metrica de Eficiencia'
        verbose_name_plural = 'Metricas de Eficiencia'
        ordering = ['-fecha', '-fecha_calculo']
        
        indexes = [
            models.Index(fields=['operario', 'fecha']),
            models.Index(fields=['maquina', 'fecha']),
        ]
    
    def __str__(self):
        """Representacion en texto: operario - maquina: eficiencia%"""
        return f"{self.operario} - {self.maquina}: {self.eficiencia_calculada}%"
    
    @classmethod
    def calcular_para_asignacion(cls, asignacion):
        """
        Calcula la eficiencia de una asignacion completada
        
        Este metodo es el corazon del sistema de metricas. Toma una asignacion
        finalizada y calcula que tan eficiente fue el operario.
        
        Args:
            asignacion: Instancia de Asignacion (debe estar completada)
            
        Returns:
            MetricaEficiencia: Nueva instancia con el calculo realizado
        """
        # Verificar que la asignacion tenga tiempos registrados
        if not asignacion.hora_inicio_real or not asignacion.hora_fin_real:
            return None
        
        # Calcular horas trabajadas
        duracion = asignacion.hora_fin_real - asignacion.hora_inicio_real
        horas = Decimal(str(duracion.total_seconds() / 3600))
        
        # Obtener produccion real (suma de todos los registros)
        produccion_real = asignacion.registros_produccion.aggregate(
            total=models.Sum('cantidad')
        )['total'] or Decimal('0')
        
        # Calcular produccion teorica
        capacidad_por_hora = asignacion.maquina.capacidad_teorica
        produccion_teorica = capacidad_por_hora * horas
        
        # Calcular eficiencia (evitar division por cero)
        if produccion_teorica > 0:
            eficiencia = (produccion_real / produccion_teorica) * 100
        else:
            eficiencia = Decimal('0')
        
        # Crear y guardar la metrica
        metrica = cls.objects.create(
            operario=asignacion.operario,
            maquina=asignacion.maquina,
            asignacion=asignacion,
            fecha=asignacion.fecha,
            produccion_real=produccion_real,
            produccion_teorica=produccion_teorica,
            horas_trabajadas=horas,
            eficiencia_calculada=eficiencia
        )
        
        # Actualizar eficiencia promedio del operario
        asignacion.operario.actualizar_eficiencia_promedio()
        
        return metrica


class ObjetivoProduccion(models.Model):
    # Meta de produccion para una maquina o turno especifico
    """
    Objetivo de produccion para medir cumplimiento
    
    Permite definir metas especificas de produccion:
    - Por maquina: cuanto debe producir una maquina al dia
    - Por turno: cuanto debe producir todo un turno
    
    Los objetivos se usan para:
    - Comparar produccion real vs meta en dashboards
    - Generar alertas cuando no se alcanza el objetivo
    - Calcular porcentaje de cumplimiento
    """
    
    class TipoObjetivoChoices(models.TextChoices):
        """Tipos de objetivo"""
        POR_MAQUINA = 'POR_MAQUINA', 'Por Maquina'
        POR_TURNO = 'POR_TURNO', 'Por Turno'
        POR_OPERARIO = 'POR_OPERARIO', 'Por Operario'
    
    # Tipo de objetivo
    tipo = models.CharField(
        max_length=20,
        choices=TipoObjetivoChoices.choices
    )
    
    # Relaciones opcionales segun el tipo de objetivo
    maquina = models.ForeignKey(
        'maquinas.Maquina',
        on_delete=models.CASCADE,
        related_name='objetivos',
        null=True,
        blank=True
    )
    
    turno = models.ForeignKey(
        'operaciones.Turno',
        on_delete=models.CASCADE,
        related_name='objetivos',
        null=True,
        blank=True
    )
    
    operario = models.ForeignKey(
        'operaciones.Operario',
        on_delete=models.CASCADE,
        related_name='objetivos',
        null=True,
        blank=True
    )
    
    # Empresa propietaria del objetivo
    empresa = models.ForeignKey(
        'usuarios.Empresa',
        on_delete=models.CASCADE,
        related_name='objetivos_produccion'
    )
    
    # Meta de produccion
    cantidad_objetivo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text='Cantidad a producir como meta'
    )
    
    # Periodo de vigencia
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    
    # Estado
    activo = models.BooleanField(default=True)
    
    # Descripcion del objetivo
    descripcion = models.TextField(blank=True)
    
    class Meta:
        """Configuracion del modelo en la base de datos"""
        db_table = 'objetivos_produccion'
        verbose_name = 'Objetivo de Produccion'
        verbose_name_plural = 'Objetivos de Produccion'
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        """Representacion en texto segun tipo de objetivo"""
        if self.tipo == self.TipoObjetivoChoices.POR_MAQUINA:
            return f"Objetivo {self.maquina}: {self.cantidad_objetivo}"
        elif self.tipo == self.TipoObjetivoChoices.POR_TURNO:
            return f"Objetivo {self.turno}: {self.cantidad_objetivo}"
        else:
            return f"Objetivo {self.operario}: {self.cantidad_objetivo}"
    
    def calcular_cumplimiento(self, fecha=None):
        """
        Calcula el porcentaje de cumplimiento del objetivo
        
        Args:
            fecha: Fecha para la cual calcular (por defecto hoy)
            
        Returns:
            dict: Diccionario con produccion real, objetivo y porcentaje
        """
        from django.db.models import Sum
        
        fecha = fecha or timezone.now().date()
        
        # Obtener produccion real segun tipo de objetivo
        if self.tipo == self.TipoObjetivoChoices.POR_MAQUINA:
            produccion = RegistroProduccion.objects.filter(
                asignacion__maquina=self.maquina,
                fecha_hora__date=fecha
            ).aggregate(total=Sum('cantidad'))['total'] or 0
        
        elif self.tipo == self.TipoObjetivoChoices.POR_TURNO:
            produccion = RegistroProduccion.objects.filter(
                asignacion__turno=self.turno,
                fecha_hora__date=fecha
            ).aggregate(total=Sum('cantidad'))['total'] or 0
        
        else:  # POR_OPERARIO
            produccion = RegistroProduccion.objects.filter(
                asignacion__operario=self.operario,
                fecha_hora__date=fecha
            ).aggregate(total=Sum('cantidad'))['total'] or 0
        
        # Calcular porcentaje
        if self.cantidad_objetivo > 0:
            porcentaje = (Decimal(str(produccion)) / self.cantidad_objetivo) * 100
        else:
            porcentaje = Decimal('0')
        
        return {
            'produccion_real': produccion,
            'objetivo': self.cantidad_objetivo,
            'porcentaje_cumplimiento': round(porcentaje, 2)
        }


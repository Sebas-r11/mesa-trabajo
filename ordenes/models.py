"""
Modelos del modulo de Ordenes para FLEX-OP

Este modulo contiene los modelos relacionados con ordenes de produccion y despacho:
- OrdenProduccion: Orden de produccion con producto, cantidad y fecha limite
- ColaDespacho: Cola priorizada de ordenes listas para despachar
"""
from django.db import models
from django.utils import timezone


class OrdenProduccion(models.Model):
    # Orden de produccion con producto, cantidad y fecha limite
    """
    Orden de produccion para planificar y seguir trabajo
    
    Una orden de produccion representa un pedido que debe cumplirse:
    - Define que producto producir y en que cantidad
    - Establece una fecha limite para completar
    - Puede asignarse a una maquina especifica
    - Permite seguir el avance de produccion
    
    Estados de una orden:
    - PENDIENTE: Creada pero no iniciada
    - EN_PROCESO: Se esta trabajando en ella
    - LISTA: Produccion completada, lista para despacho
    - DESPACHADA: Ya fue enviada al cliente
    - CANCELADA: Orden cancelada
    """
    
    class EstadoChoices(models.TextChoices):
        """Estados de la orden de produccion"""
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        EN_PROCESO = 'EN_PROCESO', 'En Proceso'
        LISTA = 'LISTA', 'Lista para Despacho'
        DESPACHADA = 'DESPACHADA', 'Despachada'
        CANCELADA = 'CANCELADA', 'Cancelada'
    
    class PrioridadChoices(models.TextChoices):
        """Prioridad de la orden"""
        BAJA = 'BAJA', 'Baja'
        NORMAL = 'NORMAL', 'Normal'
        ALTA = 'ALTA', 'Alta'
        URGENTE = 'URGENTE', 'Urgente'
    
    # Numero de orden unico
    numero_orden = models.CharField(max_length=50, unique=True)
    
    # Informacion del producto
    producto = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    
    # Cantidad requerida y unidad
    cantidad_requerida = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    unidad = models.CharField(max_length=50, default='unidades')
    
    # Cantidad ya producida (se actualiza automaticamente)
    cantidad_producida = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    
    # Fechas importantes
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_limite = models.DateTimeField(
        help_text='Fecha y hora limite para completar la orden'
    )
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_completada = models.DateTimeField(null=True, blank=True)
    fecha_despachada = models.DateTimeField(null=True, blank=True)
    
    # Estado y prioridad
    estado = models.CharField(
        max_length=20,
        choices=EstadoChoices.choices,
        default=EstadoChoices.PENDIENTE
    )
    
    prioridad = models.CharField(
        max_length=20,
        choices=PrioridadChoices.choices,
        default=PrioridadChoices.NORMAL
    )
    
    # Maquina asignada (opcional)
    maquina = models.ForeignKey(
        'maquinas.Maquina',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordenes_produccion'
    )
    
    # Empresa
    empresa = models.ForeignKey(
        'usuarios.Empresa',
        on_delete=models.CASCADE,
        related_name='ordenes_produccion'
    )
    
    # Usuario que creo la orden
    creada_por = models.ForeignKey(
        'usuarios.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='ordenes_creadas'
    )
    
    # Notas adicionales
    notas = models.TextField(blank=True)
    
    class Meta:
        """Configuracion del modelo en la base de datos"""
        db_table = 'ordenes_produccion'
        verbose_name = 'Orden de Produccion'
        verbose_name_plural = 'Ordenes de Produccion'
        ordering = ['-prioridad', 'fecha_limite', '-fecha_creacion']
        
        indexes = [
            models.Index(fields=['estado', 'prioridad']),
            models.Index(fields=['empresa', 'estado']),
            models.Index(fields=['fecha_limite']),
        ]
    
    def __str__(self):
        """Representacion en texto: numero de orden - producto"""
        return f"{self.numero_orden} - {self.producto}"
    
    def porcentaje_avance(self):
        """
        Calcula el porcentaje de avance de la orden
        
        Returns:
            float: Porcentaje de avance (0-100)
        """
        if self.cantidad_requerida > 0:
            return float((self.cantidad_producida / self.cantidad_requerida) * 100)
        return 0
    
    def esta_atrasada(self):
        """
        Verifica si la orden esta atrasada
        
        Returns:
            bool: True si la fecha limite ya paso y no esta completada
        """
        if self.estado in [self.EstadoChoices.LISTA, self.EstadoChoices.DESPACHADA]:
            return False
        return timezone.now() > self.fecha_limite
    
    def iniciar(self):
        """
        Marca la orden como en proceso
        """
        if self.estado == self.EstadoChoices.PENDIENTE:
            self.estado = self.EstadoChoices.EN_PROCESO
            self.fecha_inicio = timezone.now()
            self.save()
    
    def completar(self):
        """
        Marca la orden como lista para despacho
        
        Tambien la agrega a la cola de despacho automaticamente
        """
        if self.estado == self.EstadoChoices.EN_PROCESO:
            self.estado = self.EstadoChoices.LISTA
            self.fecha_completada = timezone.now()
            self.save()
            
            # Agregar a cola de despacho
            ColaDespacho.objects.create(
                orden=self,
                empresa=self.empresa
            )
    
    def despachar(self, usuario):
        """
        Marca la orden como despachada
        
        Args:
            usuario: Usuario que realiza el despacho
        """
        if self.estado == self.EstadoChoices.LISTA:
            self.estado = self.EstadoChoices.DESPACHADA
            self.fecha_despachada = timezone.now()
            self.save()
            
            # Actualizar cola de despacho
            try:
                cola = self.posicion_cola.get()
                cola.despachar(usuario)
            except ColaDespacho.DoesNotExist:
                pass
    
    def registrar_produccion(self, cantidad):
        """
        Registra produccion hacia esta orden
        
        Args:
            cantidad: Cantidad producida a agregar
        """
        self.cantidad_producida += cantidad
        
        # Si alcanzo o supero la cantidad requerida, marcar como lista
        if self.cantidad_producida >= self.cantidad_requerida:
            self.completar()
        else:
            self.save()


class ColaDespacho(models.Model):
    # Posicion de una orden en la cola de despacho
    """
    Cola de despacho para ordenes listas
    
    Cuando una orden se completa, entra en la cola de despacho:
    - La cola esta ordenada por prioridad y fecha limite
    - El operador de logistica toma la primera de la cola
    - Al despachar, se registra quien y cuando
    
    La cola permite:
    - Organizar el trabajo de despacho
    - Priorizar ordenes urgentes
    - Generar alertas si ordenes llevan mucho tiempo esperando
    """
    
    class EstadoChoices(models.TextChoices):
        """Estados en la cola"""
        EN_COLA = 'EN_COLA', 'En Cola'
        DESPACHADA = 'DESPACHADA', 'Despachada'
    
    # Orden en la cola
    orden = models.ForeignKey(
        'OrdenProduccion',
        on_delete=models.CASCADE,
        related_name='posicion_cola'
    )
    
    # Empresa
    empresa = models.ForeignKey(
        'usuarios.Empresa',
        on_delete=models.CASCADE,
        related_name='cola_despacho'
    )
    
    # Estado en la cola
    estado = models.CharField(
        max_length=20,
        choices=EstadoChoices.choices,
        default=EstadoChoices.EN_COLA
    )
    
    # Posicion manual (para reordenar si es necesario)
    posicion_manual = models.IntegerField(
        default=0,
        help_text='Posicion manual para reordenar la cola'
    )
    
    # Tiempos
    fecha_entrada = models.DateTimeField(auto_now_add=True)
    fecha_despacho = models.DateTimeField(null=True, blank=True)
    
    # Usuario que despacho
    despachado_por = models.ForeignKey(
        'usuarios.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='despachos_realizados'
    )
    
    # Notas del despacho
    notas = models.TextField(blank=True)
    
    class Meta:
        """Configuracion del modelo en la base de datos"""
        db_table = 'cola_despacho'
        verbose_name = 'Cola de Despacho'
        verbose_name_plural = 'Cola de Despacho'
        # Ordenar por prioridad de la orden, luego por fecha limite, luego por posicion manual
        ordering = ['-orden__prioridad', 'orden__fecha_limite', 'posicion_manual', 'fecha_entrada']
    
    def __str__(self):
        """Representacion en texto: orden - estado"""
        return f"{self.orden} - {self.get_estado_display()}"
    
    def tiempo_en_cola_minutos(self):
        """
        Calcula cuanto tiempo lleva en cola
        
        Returns:
            int: Minutos en cola
        """
        fin = self.fecha_despacho or timezone.now()
        return int((fin - self.fecha_entrada).total_seconds() / 60)
    
    def despachar(self, usuario, notas=''):
        """
        Marca como despachada
        
        Args:
            usuario: Usuario que despacha
            notas: Notas del despacho
        """
        self.estado = self.EstadoChoices.DESPACHADA
        self.fecha_despacho = timezone.now()
        self.despachado_por = usuario
        self.notas = notas
        self.save()
    
    @classmethod
    def siguiente_a_despachar(cls, empresa):
        """
        Obtiene la siguiente orden a despachar
        
        Args:
            empresa: Empresa para la cual buscar
            
        Returns:
            ColaDespacho: Siguiente item en cola, o None si esta vacia
        """
        return cls.objects.filter(
            empresa=empresa,
            estado=cls.EstadoChoices.EN_COLA
        ).first()
    
    @classmethod
    def ordenes_pendientes_count(cls, empresa):
        """
        Cuenta ordenes pendientes de despacho
        
        Args:
            empresa: Empresa para la cual contar
            
        Returns:
            int: Cantidad de ordenes en cola
        """
        return cls.objects.filter(
            empresa=empresa,
            estado=cls.EstadoChoices.EN_COLA
        ).count()


"""
Modelos del modulo de Alertas para FLEX-OP

Este modulo contiene los modelos relacionados con alertas y reglas:
- ReglaAlerta: Define condiciones que disparan alertas automaticas
- Alerta: Alertas generadas por el sistema segun las reglas
- Notificacion: Registro de notificaciones enviadas a usuarios
"""
from django.db import models
from django.utils import timezone


class ReglaAlerta(models.Model):
    # Define una condicion que dispara una alerta automatica
    """
    Regla que define cuando generar una alerta automatica
    
    Las reglas permiten configurar alertas sin programar:
    - Definen una condicion a evaluar (eficiencia baja, maquina parada, etc)
    - Especifican un umbral que dispara la alerta
    - Determinan la prioridad de las alertas generadas
    
    Tipos de reglas disponibles:
    - EFICIENCIA_BAJA: Cuando eficiencia cae bajo un porcentaje
    - MAQUINA_PARADA: Cuando una maquina lleva tiempo sin operar
    - INCIDENCIA_SIN_RESOLVER: Cuando una incidencia lleva tiempo abierta
    - OBJETIVO_NO_ALCANZADO: Cuando no se cumple la meta de produccion
    
    Las reglas se evaluan periodicamente por una tarea programada
    """
    
    class TipoReglaChoices(models.TextChoices):
        """Tipos de reglas disponibles"""
        EFICIENCIA_BAJA = 'EFICIENCIA_BAJA', 'Eficiencia Baja'
        MAQUINA_PARADA = 'MAQUINA_PARADA', 'Maquina Parada'
        INCIDENCIA_SIN_RESOLVER = 'INCIDENCIA_SIN_RESOLVER', 'Incidencia Sin Resolver'
        OBJETIVO_NO_ALCANZADO = 'OBJETIVO_NO_ALCANZADO', 'Objetivo No Alcanzado'
    
    class PrioridadChoices(models.TextChoices):
        """Prioridad de las alertas generadas"""
        BAJA = 'BAJA', 'Baja'
        MEDIA = 'MEDIA', 'Media'
        ALTA = 'ALTA', 'Alta'
        CRITICA = 'CRITICA', 'Critica'
    
    # Identificacion de la regla
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    
    # Tipo de regla
    tipo = models.CharField(
        max_length=30,
        choices=TipoReglaChoices.choices
    )
    
    # Umbral que dispara la alerta
    # Por ejemplo: 70 para eficiencia < 70%, 30 para parada > 30 minutos
    umbral = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Valor umbral que dispara la alerta'
    )
    
    # Unidad del umbral para claridad
    unidad_umbral = models.CharField(
        max_length=50,
        blank=True,
        help_text='Unidad del umbral (porcentaje, minutos, etc)'
    )
    
    # Prioridad de las alertas generadas por esta regla
    prioridad = models.CharField(
        max_length=20,
        choices=PrioridadChoices.choices,
        default=PrioridadChoices.MEDIA
    )
    
    # Empresa propietaria de la regla
    empresa = models.ForeignKey(
        'usuarios.Empresa',
        on_delete=models.CASCADE,
        related_name='reglas_alerta'
    )
    
    # Estado de la regla
    activa = models.BooleanField(default=True)
    
    # Audioria
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Configuracion del modelo en la base de datos"""
        db_table = 'reglas_alerta'
        verbose_name = 'Regla de Alerta'
        verbose_name_plural = 'Reglas de Alerta'
        ordering = ['nombre']
    
    def __str__(self):
        """Representacion en texto: nombre (tipo)"""
        return f"{self.nombre} ({self.get_tipo_display()})"
    
    def evaluar(self):
        """
        Evalua la regla y genera alertas si se cumple la condicion
        
        Este metodo es llamado por la tarea programada que revisa las reglas.
        Segun el tipo de regla, evalua diferentes condiciones.
        
        Returns:
            list: Lista de alertas generadas (puede estar vacia)
        """
        alertas_generadas = []
        
        if self.tipo == self.TipoReglaChoices.EFICIENCIA_BAJA:
            alertas_generadas = self._evaluar_eficiencia_baja()
        
        elif self.tipo == self.TipoReglaChoices.MAQUINA_PARADA:
            alertas_generadas = self._evaluar_maquina_parada()
        
        elif self.tipo == self.TipoReglaChoices.INCIDENCIA_SIN_RESOLVER:
            alertas_generadas = self._evaluar_incidencia_sin_resolver()
        
        elif self.tipo == self.TipoReglaChoices.OBJETIVO_NO_ALCANZADO:
            alertas_generadas = self._evaluar_objetivo_no_alcanzado()
        
        return alertas_generadas
    
    def _evaluar_eficiencia_baja(self):
        """Evalua si hay operarios con eficiencia bajo el umbral"""
        from operaciones.models import Operario
        
        alertas = []
        operarios = Operario.objects.filter(
            usuario__empresa=self.empresa,
            activo=True,
            eficiencia_promedio__lt=self.umbral
        )
        
        for operario in operarios:
            # Verificar si ya existe alerta activa para este operario
            alerta_existente = Alerta.objects.filter(
                regla=self,
                operario_relacionado=operario,
                estado=Alerta.EstadoChoices.ACTIVA
            ).exists()
            
            if not alerta_existente:
                alerta = Alerta.objects.create(
                    regla=self,
                    titulo=f"Eficiencia baja: {operario}",
                    descripcion=f"El operario {operario} tiene eficiencia de {operario.eficiencia_promedio}%, bajo el umbral de {self.umbral}%",
                    prioridad=self.prioridad,
                    operario_relacionado=operario,
                    empresa=self.empresa
                )
                alertas.append(alerta)
        
        return alertas
    
    def _evaluar_maquina_parada(self):
        """Evalua si hay maquinas paradas por mas tiempo del umbral"""
        from maquinas.models import Maquina
        
        alertas = []
        maquinas_paradas = Maquina.objects.filter(
            empresa=self.empresa,
            estado_actual='PARADA',
            activa=True
        )
        
        for maquina in maquinas_paradas:
            # Obtener ultimo cambio de estado
            ultimo_estado = maquina.historial_estados.first()
            if ultimo_estado:
                minutos_parada = (timezone.now() - ultimo_estado.fecha_hora).total_seconds() / 60
                
                if minutos_parada >= float(self.umbral):
                    # Verificar si ya existe alerta activa
                    alerta_existente = Alerta.objects.filter(
                        regla=self,
                        maquina_relacionada=maquina,
                        estado=Alerta.EstadoChoices.ACTIVA
                    ).exists()
                    
                    if not alerta_existente:
                        alerta = Alerta.objects.create(
                            regla=self,
                            titulo=f"Maquina parada: {maquina}",
                            descripcion=f"La maquina {maquina} lleva {int(minutos_parada)} minutos parada",
                            prioridad=self.prioridad,
                            maquina_relacionada=maquina,
                            empresa=self.empresa
                        )
                        alertas.append(alerta)
        
        return alertas
    
    def _evaluar_incidencia_sin_resolver(self):
        """Evalua si hay incidencias abiertas por mas tiempo del umbral"""
        from operaciones.models import Incidencia
        
        alertas = []
        incidencias_abiertas = Incidencia.objects.filter(
            maquina__empresa=self.empresa,
            estado__in=['ABIERTA', 'EN_PROCESO']
        )
        
        for incidencia in incidencias_abiertas:
            minutos_abierta = incidencia.tiempo_abierta_minutos()
            
            if minutos_abierta >= float(self.umbral):
                # Verificar si ya existe alerta activa
                alerta_existente = Alerta.objects.filter(
                    regla=self,
                    incidencia_relacionada=incidencia,
                    estado=Alerta.EstadoChoices.ACTIVA
                ).exists()
                
                if not alerta_existente:
                    alerta = Alerta.objects.create(
                        regla=self,
                        titulo=f"Incidencia sin resolver: {incidencia.titulo}",
                        descripcion=f"La incidencia '{incidencia.titulo}' lleva {minutos_abierta} minutos sin resolver",
                        prioridad=self.prioridad,
                        incidencia_relacionada=incidencia,
                        empresa=self.empresa
                    )
                    alertas.append(alerta)
        
        return alertas
    
    def _evaluar_objetivo_no_alcanzado(self):
        """Evalua si hay objetivos que no se estan cumpliendo"""
        from metricas.models import ObjetivoProduccion
        
        alertas = []
        objetivos = ObjetivoProduccion.objects.filter(
            empresa=self.empresa,
            activo=True
        )
        
        for objetivo in objetivos:
            cumplimiento = objetivo.calcular_cumplimiento()
            
            if cumplimiento['porcentaje_cumplimiento'] < float(self.umbral):
                # Verificar si ya existe alerta activa para este objetivo hoy
                alerta_existente = Alerta.objects.filter(
                    regla=self,
                    estado=Alerta.EstadoChoices.ACTIVA,
                    fecha_creacion__date=timezone.now().date()
                ).exists()
                
                if not alerta_existente:
                    alerta = Alerta.objects.create(
                        regla=self,
                        titulo=f"Objetivo no alcanzado: {objetivo}",
                        descripcion=f"El objetivo tiene {cumplimiento['porcentaje_cumplimiento']}% de cumplimiento, bajo el {self.umbral}% esperado",
                        prioridad=self.prioridad,
                        empresa=self.empresa
                    )
                    alertas.append(alerta)
        
        return alertas


class Alerta(models.Model):
    # Alerta generada por el sistema segun una regla
    """
    Alerta generada automaticamente por el sistema
    
    Las alertas notifican situaciones que requieren atencion:
    - Se generan automaticamente cuando se cumplen las reglas
    - Tienen diferentes prioridades segun la urgencia
    - Pueden ser resueltas o escaladas por supervisores
    
    Estados de una alerta:
    - ACTIVA: Requiere atencion
    - RESUELTA: Ya fue atendida
    - ESCALADA: Se notifico a nivel superior
    - DESCARTADA: Se ignoro por no ser relevante
    """
    
    class EstadoChoices(models.TextChoices):
        """Estados posibles de una alerta"""
        ACTIVA = 'ACTIVA', 'Activa'
        RESUELTA = 'RESUELTA', 'Resuelta'
        ESCALADA = 'ESCALADA', 'Escalada'
        DESCARTADA = 'DESCARTADA', 'Descartada'
    
    class PrioridadChoices(models.TextChoices):
        """Prioridad de la alerta"""
        BAJA = 'BAJA', 'Baja'
        MEDIA = 'MEDIA', 'Media'
        ALTA = 'ALTA', 'Alta'
        CRITICA = 'CRITICA', 'Critica'
    
    # Regla que genero la alerta (puede ser null si se creo manualmente)
    regla = models.ForeignKey(
        'ReglaAlerta',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alertas'
    )
    
    # Informacion de la alerta
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    
    prioridad = models.CharField(
        max_length=20,
        choices=PrioridadChoices.choices,
        default=PrioridadChoices.MEDIA
    )
    
    estado = models.CharField(
        max_length=20,
        choices=EstadoChoices.choices,
        default=EstadoChoices.ACTIVA
    )
    
    # Relaciones opcionales con entidades relacionadas
    operario_relacionado = models.ForeignKey(
        'operaciones.Operario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alertas'
    )
    
    maquina_relacionada = models.ForeignKey(
        'maquinas.Maquina',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alertas'
    )
    
    incidencia_relacionada = models.ForeignKey(
        'operaciones.Incidencia',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alertas'
    )
    
    # Empresa
    empresa = models.ForeignKey(
        'usuarios.Empresa',
        on_delete=models.CASCADE,
        related_name='alertas'
    )
    
    # Tiempos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    
    # Usuario que resolvio la alerta
    resuelta_por = models.ForeignKey(
        'usuarios.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alertas_resueltas'
    )
    
    # Notas de resolucion
    notas_resolucion = models.TextField(blank=True)
    
    class Meta:
        """Configuracion del modelo en la base de datos"""
        db_table = 'alertas'
        verbose_name = 'Alerta'
        verbose_name_plural = 'Alertas'
        ordering = ['-fecha_creacion']
        
        indexes = [
            models.Index(fields=['estado', 'prioridad']),
            models.Index(fields=['empresa', 'estado']),
        ]
    
    def __str__(self):
        """Representacion en texto: titulo (estado)"""
        return f"{self.titulo} ({self.get_estado_display()})"
    
    def resolver(self, usuario, notas=''):
        """
        Marca la alerta como resuelta
        
        Args:
            usuario: Usuario que resuelve la alerta
            notas: Notas opcionales sobre la resolucion
        """
        self.estado = self.EstadoChoices.RESUELTA
        self.resuelta_por = usuario
        self.notas_resolucion = notas
        self.fecha_resolucion = timezone.now()
        self.save()
    
    def escalar(self, notas=''):
        """
        Escala la alerta a nivel superior
        
        Args:
            notas: Notas sobre por que se escala
        """
        self.estado = self.EstadoChoices.ESCALADA
        self.notas_resolucion = notas
        self.save()
        
        # Crear notificacion para gerentes
        from usuarios.models import User
        gerentes = User.objects.filter(
            empresa=self.empresa,
            rol=User.RolChoices.GERENTE,
            activo=True
        )
        
        for gerente in gerentes:
            Notificacion.objects.create(
                usuario=gerente,
                alerta=self,
                titulo=f"Alerta escalada: {self.titulo}",
                mensaje=f"La alerta '{self.titulo}' ha sido escalada y requiere su atencion"
            )


class Notificacion(models.Model):
    # Notificacion enviada a un usuario sobre una alerta
    """
    Notificacion enviada a un usuario
    
    Las notificaciones permiten:
    - Avisar a usuarios sobre alertas importantes
    - Mantener un registro de comunicaciones
    - Rastrear si el usuario vio la notificacion
    """
    
    # Usuario destinatario
    usuario = models.ForeignKey(
        'usuarios.User',
        on_delete=models.CASCADE,
        related_name='notificaciones'
    )
    
    # Alerta relacionada (opcional)
    alerta = models.ForeignKey(
        'Alerta',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notificaciones'
    )
    
    # Contenido de la notificacion
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    
    # Estado de lectura
    leida = models.BooleanField(default=False)
    fecha_lectura = models.DateTimeField(null=True, blank=True)
    
    # Auditoria
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        """Configuracion del modelo en la base de datos"""
        db_table = 'notificaciones'
        verbose_name = 'Notificacion'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        """Representacion en texto: titulo para usuario"""
        return f"{self.titulo} para {self.usuario}"
    
    def marcar_leida(self):
        """Marca la notificacion como leida"""
        self.leida = True
        self.fecha_lectura = timezone.now()
        self.save()


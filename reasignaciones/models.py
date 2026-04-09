"""
Modelos del modulo de Reasignaciones para FLEX-OP

Este modulo contiene los modelos relacionados con sugerencias de reasignacion:
- SugerenciaReasignacion: Propuesta de mover un operario a otra maquina
"""
from django.db import models
from django.utils import timezone


class SugerenciaReasignacion(models.Model):
    # Sugerencia automatica de reasignar un operario a otra maquina
    """
    Sugerencia de reasignacion generada por el sistema
    
    El sistema detecta oportunidades de mejora y sugiere reasignaciones:
    - Maquina parada con operario disponible que puede operarla
    - Operario con baja eficiencia en una maquina pero alta en otra
    - Operario ocioso mientras hay maquinas sin operar
    
    Los supervisores pueden:
    - Aceptar la sugerencia (se aplica la reasignacion)
    - Rechazar la sugerencia (se descarta)
    - Ignorarla (se mantiene como pendiente)
    
    Tipos de razones para reasignacion:
    - MAQUINA_DISPONIBLE: Hay una maquina disponible que necesita operario
    - OPTIMIZAR_EFICIENCIA: El operario seria mas eficiente en otra maquina
    - CUBRIR_AUSENCIA: Cubrir la ausencia de otro operario
    - BALANCEAR_CARGA: Equilibrar la carga de trabajo entre maquinas
    """
    
    class RazonChoices(models.TextChoices):
        """Razones para la sugerencia de reasignacion"""
        MAQUINA_DISPONIBLE = 'MAQUINA_DISPONIBLE', 'Maquina Disponible'
        OPTIMIZAR_EFICIENCIA = 'OPTIMIZAR_EFICIENCIA', 'Optimizar Eficiencia'
        CUBRIR_AUSENCIA = 'CUBRIR_AUSENCIA', 'Cubrir Ausencia'
        BALANCEAR_CARGA = 'BALANCEAR_CARGA', 'Balancear Carga'
    
    class EstadoChoices(models.TextChoices):
        """Estados de la sugerencia"""
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        ACEPTADA = 'ACEPTADA', 'Aceptada'
        RECHAZADA = 'RECHAZADA', 'Rechazada'
        EXPIRADA = 'EXPIRADA', 'Expirada'
    
    # Operario que se sugiere reasignar
    operario = models.ForeignKey(
        'operaciones.Operario',
        on_delete=models.CASCADE,
        related_name='sugerencias_reasignacion'
    )
    
    # Maquina de origen (donde esta actualmente, puede ser null si esta libre)
    maquina_origen = models.ForeignKey(
        'maquinas.Maquina',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sugerencias_salida'
    )
    
    # Maquina de destino (donde se sugiere asignarlo)
    maquina_destino = models.ForeignKey(
        'maquinas.Maquina',
        on_delete=models.CASCADE,
        related_name='sugerencias_entrada'
    )
    
    # Razon de la sugerencia
    razon = models.CharField(
        max_length=30,
        choices=RazonChoices.choices
    )
    
    # Descripcion detallada de por que se sugiere
    descripcion = models.TextField()
    
    # Impacto estimado en produccion (porcentaje de mejora esperado)
    impacto_estimado = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text='Porcentaje de mejora estimado en produccion'
    )
    
    # Estado de la sugerencia
    estado = models.CharField(
        max_length=20,
        choices=EstadoChoices.choices,
        default=EstadoChoices.PENDIENTE
    )
    
    # Empresa
    empresa = models.ForeignKey(
        'usuarios.Empresa',
        on_delete=models.CASCADE,
        related_name='sugerencias_reasignacion'
    )
    
    # Tiempos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_decision = models.DateTimeField(null=True, blank=True)
    
    # Usuario que tomo la decision
    decidido_por = models.ForeignKey(
        'usuarios.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sugerencias_decididas'
    )
    
    # Notas sobre la decision
    notas_decision = models.TextField(blank=True)
    
    # Asignacion creada si se acepto la sugerencia
    asignacion_creada = models.ForeignKey(
        'operaciones.Asignacion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sugerencia_origen'
    )
    
    class Meta:
        """Configuracion del modelo en la base de datos"""
        db_table = 'sugerencias_reasignacion'
        verbose_name = 'Sugerencia de Reasignacion'
        verbose_name_plural = 'Sugerencias de Reasignacion'
        ordering = ['-fecha_creacion']
        
        indexes = [
            models.Index(fields=['estado', 'empresa']),
            models.Index(fields=['operario', 'estado']),
        ]
    
    def __str__(self):
        """Representacion en texto: operario de maquina_origen a maquina_destino"""
        origen = self.maquina_origen.codigo if self.maquina_origen else "Libre"
        return f"{self.operario}: {origen} -> {self.maquina_destino.codigo}"
    
    def aceptar(self, usuario, notas=''):
        """
        Acepta la sugerencia y crea la asignacion correspondiente
        
        Args:
            usuario: Usuario que acepta la sugerencia
            notas: Notas opcionales
            
        Returns:
            Asignacion: La nueva asignacion creada
        """
        from operaciones.models import Asignacion, Turno
        
        # Actualizar estado
        self.estado = self.EstadoChoices.ACEPTADA
        self.decidido_por = usuario
        self.fecha_decision = timezone.now()
        self.notas_decision = notas
        
        # Obtener turno actual del operario o el primero activo
        turno = self.operario.turno_actual
        if not turno:
            turno = Turno.objects.filter(
                empresa=self.empresa,
                activo=True
            ).first()
        
        # Crear la nueva asignacion
        asignacion = Asignacion.objects.create(
            operario=self.operario,
            maquina=self.maquina_destino,
            turno=turno,
            fecha=timezone.now().date(),
            asignado_por=usuario,
            observaciones=f"Creada por sugerencia de reasignacion #{self.id}: {notas}"
        )
        
        self.asignacion_creada = asignacion
        self.save()
        
        return asignacion
    
    def rechazar(self, usuario, notas=''):
        """
        Rechaza la sugerencia
        
        Args:
            usuario: Usuario que rechaza
            notas: Razon del rechazo
        """
        self.estado = self.EstadoChoices.RECHAZADA
        self.decidido_por = usuario
        self.fecha_decision = timezone.now()
        self.notas_decision = notas
        self.save()
    
    @classmethod
    def generar_sugerencias(cls, empresa):
        """
        Genera sugerencias de reasignacion para una empresa
        
        Analiza la situacion actual y genera sugerencias:
        1. Busca maquinas disponibles sin operario
        2. Busca operarios disponibles con habilidades
        3. Calcula impacto estimado basado en eficiencia historica
        
        Args:
            empresa: Empresa para la cual generar sugerencias
            
        Returns:
            list: Lista de sugerencias generadas
        """
        from operaciones.models import Operario
        from maquinas.models import Maquina
        
        sugerencias = []
        
        # Buscar maquinas disponibles que no tienen operario asignado hoy
        maquinas_disponibles = Maquina.objects.filter(
            empresa=empresa,
            estado_actual='DISPONIBLE',
            activa=True
        )
        
        # Buscar operarios disponibles
        operarios_disponibles = Operario.objects.filter(
            usuario__empresa=empresa,
            disponible=True,
            activo=True
        )
        
        for maquina in maquinas_disponibles:
            # Buscar operarios que pueden operar esta maquina
            for operario in operarios_disponibles:
                if operario.puede_operar(maquina):
                    # Verificar si ya existe sugerencia pendiente similar
                    existe = cls.objects.filter(
                        operario=operario,
                        maquina_destino=maquina,
                        estado=cls.EstadoChoices.PENDIENTE
                    ).exists()
                    
                    if not existe:
                        # Calcular impacto estimado basado en eficiencia historica
                        impacto = operario.eficiencia_promedio if operario.eficiencia_promedio else 80
                        
                        sugerencia = cls.objects.create(
                            operario=operario,
                            maquina_origen=None,  # Operario libre
                            maquina_destino=maquina,
                            razon=cls.RazonChoices.MAQUINA_DISPONIBLE,
                            descripcion=f"El operario {operario} esta disponible y puede operar la maquina {maquina} que esta sin asignar",
                            impacto_estimado=impacto,
                            empresa=empresa
                        )
                        sugerencias.append(sugerencia)
                        
                        # Solo una sugerencia por maquina
                        break
        
        return sugerencias


# FLEX-OP - Modelos de Django
## Diseño Completo de la Base de Datos

---

## Tabla de Contenidos
1. [Modelos de Autenticación y Usuarios](#1-modelos-de-autenticación-y-usuarios)
2. [Modelos de Configuración](#2-modelos-de-configuración)
3. [Modelos Operacionales](#3-modelos-operacionales)
4. [Modelos de Métricas y Eficiencia](#4-modelos-de-métricas-y-eficiencia)
5. [Modelos de Alertas y Reglas](#5-modelos-de-alertas-y-reglas)
6. [Modelos de Reasignación](#6-modelos-de-reasignación)
7. [Modelos de Órdenes y Despacho](#7-modelos-de-órdenes-y-despacho)
8. [Modelos IoT (Preparados)](#8-modelos-iot-preparados)
9. [Diagrama de Relaciones](#9-diagrama-de-relaciones)

---

## 1. Modelos de Autenticación y Usuarios

### 1.1 Usuario (User)
**Archivo**: `core/models/user.py`

```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Usuario extendido con roles del sistema"""
    
    class RolChoices(models.TextChoices):
        OPERARIO = 'OPERARIO', 'Operario'
        SUPERVISOR = 'SUPERVISOR', 'Supervisor'
        GERENTE = 'GERENTE', 'Gerente'
        ADMIN = 'ADMIN', 'Administrador'
    
    rol = models.CharField(
        max_length=20,
        choices=RolChoices.choices,
        default=RolChoices.OPERARIO,
        verbose_name='Rol'
    )
    telefono = models.CharField(max_length=20, blank=True, null=True)
    foto_perfil = models.ImageField(upload_to='perfiles/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_ingreso = models.DateField(auto_now_add=True)
    
    # Relación con empresa (preparado para multitenancy)
    empresa = models.ForeignKey(
        'Empresa',
        on_delete=models.CASCADE,
        related_name='usuarios',
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['username']
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_rol_display()})"
    
    @property
    def es_operario(self):
        return self.rol == self.RolChoices.OPERARIO
    
    @property
    def es_supervisor(self):
        return self.rol == self.RolChoices.SUPERVISOR
    
    @property
    def es_gerente(self):
        return self.rol == self.RolChoices.GERENTE
    
    @property
    def es_admin(self):
        return self.rol == self.RolChoices.ADMIN
```

### 1.2 Empresa
**Archivo**: `core/models/empresa.py`

```python
from django.db import models

class Empresa(models.Model):
    """Cliente/Empresa que usa el sistema"""
    
    nombre = models.CharField(max_length=200, unique=True)
    razon_social = models.CharField(max_length=200)
    ruc = models.CharField(max_length=20, unique=True)
    direccion = models.TextField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField()
    
    # Configuración
    logo = models.ImageField(upload_to='empresas/', blank=True, null=True)
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'empresas'
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
```

---

## 2. Modelos de Configuración

### 2.1 TipoMaquina
**Archivo**: `core/models/tipo_maquina.py`

```python
from django.db import models

class TipoMaquina(models.Model):
    """Categoría de máquinas (ej: Llenadora, Tractor, Torno CNC)"""
    
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    empresa = models.ForeignKey('Empresa', on_delete=models.CASCADE, related_name='tipos_maquina')
    
    class Meta:
        db_table = 'tipos_maquina'
        verbose_name = 'Tipo de Máquina'
        verbose_name_plural = 'Tipos de Máquina'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
```

### 2.2 Maquina
**Archivo**: `core/models/maquina.py`

```python
from django.db import models

class Maquina(models.Model):
    """Máquina o equipo productivo"""
    
    class EstadoChoices(models.TextChoices):
        DISPONIBLE = 'DISPONIBLE', 'Disponible'
        OPERANDO = 'OPERANDO', 'Operando'
        MANTENIMIENTO = 'MANTENIMIENTO', 'En Mantenimiento'
        PARADA = 'PARADA', 'Parada'
        FUERA_SERVICIO = 'FUERA_SERVICIO', 'Fuera de Servicio'
    
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200)
    tipo = models.ForeignKey('TipoMaquina', on_delete=models.PROTECT, related_name='maquinas')
    empresa = models.ForeignKey('Empresa', on_delete=models.CASCADE, related_name='maquinas')
    
    # Especificaciones
    marca = models.CharField(max_length=100, blank=True)
    modelo = models.CharField(max_length=100, blank=True)
    numero_serie = models.CharField(max_length=100, blank=True)
    ubicacion = models.CharField(max_length=200, blank=True)
    
    # Capacidad teórica
    capacidad_teorica = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Producción teórica por hora'
    )
    unidad_capacidad = models.ForeignKey(
        'UnidadEficiencia',
        on_delete=models.PROTECT,
        related_name='maquinas'
    )
    
    # Estado
    estado_actual = models.CharField(
        max_length=20,
        choices=EstadoChoices.choices,
        default=EstadoChoices.DISPONIBLE
    )
    
    # Control
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    # Preparado para IoT
    tiene_sensor = models.BooleanField(default=False)
    sensor_iot = models.ForeignKey(
        'SensorIoT',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='maquina_asociada'
    )
    
    class Meta:
        db_table = 'maquinas'
        verbose_name = 'Máquina'
        verbose_name_plural = 'Máquinas'
        ordering = ['codigo']
        indexes = [
            models.Index(fields=['estado_actual']),
            models.Index(fields=['empresa', 'activa']),
        ]
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    def cambiar_estado(self, nuevo_estado, usuario=None, observacion=''):
        """Cambia el estado de la máquina y registra el cambio"""
        from .estado_maquina import EstadoMaquina
        
        estado_anterior = self.estado_actual
        self.estado_actual = nuevo_estado
        self.save()
        
        # Registrar cambio de estado
        EstadoMaquina.objects.create(
            maquina=self,
            estado=nuevo_estado,
            usuario=usuario,
            observacion=observacion
        )
        
        return True
```

### 2.3 UnidadEficiencia
**Archivo**: `core/models/unidad_eficiencia.py`

```python
from django.db import models

class UnidadEficiencia(models.Model):
    """Unidades de medida de eficiencia (hectáreas/hora, unidades/hora, etc.)"""
    
    nombre = models.CharField(max_length=100)
    abreviatura = models.CharField(max_length=20)
    descripcion = models.TextField(blank=True)
    empresa = models.ForeignKey('Empresa', on_delete=models.CASCADE, related_name='unidades_eficiencia')
    
    class Meta:
        db_table = 'unidades_eficiencia'
        verbose_name = 'Unidad de Eficiencia'
        verbose_name_plural = 'Unidades de Eficiencia'
        unique_together = ['nombre', 'empresa']
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.abreviatura})"
```

### 2.4 Habilidad
**Archivo**: `core/models/habilidad.py`

```python
from django.db import models

class Habilidad(models.Model):
    """Habilidades que pueden tener los operarios"""
    
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    empresa = models.ForeignKey('Empresa', on_delete=models.CASCADE, related_name='habilidades')
    
    # Asociación con tipos de máquina
    tipos_maquina = models.ManyToManyField(
        'TipoMaquina',
        related_name='habilidades_requeridas',
        blank=True
    )
    
    class Meta:
        db_table = 'habilidades'
        verbose_name = 'Habilidad'
        verbose_name_plural = 'Habilidades'
        unique_together = ['nombre', 'empresa']
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
```

### 2.5 Operario (Perfil Extendido)
**Archivo**: `core/models/operario.py`

```python
from django.db import models

class Operario(models.Model):
    """Perfil extendido de operarios con sus habilidades y métricas"""
    
    usuario = models.OneToOneField(
        'User',
        on_delete=models.CASCADE,
        related_name='perfil_operario',
        limit_choices_to={'rol': 'OPERARIO'}
    )
    
    # Información laboral
    codigo_empleado = models.CharField(max_length=50, unique=True)
    fecha_contratacion = models.DateField()
    
    # Habilidades
    habilidades = models.ManyToManyField(
        'Habilidad',
        related_name='operarios',
        blank=True
    )
    
    # Turnos
    turno_actual = models.ForeignKey(
        'Turno',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='operarios_asignados'
    )
    
    # Estado
    disponible = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)
    
    # Métricas acumuladas
    eficiencia_promedio = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text='Eficiencia promedio histórica (%)'
    )
    total_tareas_completadas = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'operarios'
        verbose_name = 'Operario'
        verbose_name_plural = 'Operarios'
        ordering = ['codigo_empleado']
    
    def __str__(self):
        return f"{self.codigo_empleado} - {self.usuario.get_full_name()}"
    
    def puede_operar(self, maquina):
        """Verifica si el operario tiene habilidad para operar una máquina"""
        habilidades_requeridas = maquina.tipo.habilidades_requeridas.all()
        habilidades_operario = self.habilidades.all()
        
        # Si el tipo de máquina no requiere habilidades específicas, cualquiera puede
        if not habilidades_requeridas.exists():
            return True
        
        # Verificar si tiene al menos una habilidad requerida
        return habilidades_requeridas.filter(id__in=habilidades_operario).exists()
    
    def actualizar_eficiencia_promedio(self):
        """Recalcula la eficiencia promedio basada en métricas históricas"""
        from .metrica_eficiencia import MetricaEficiencia
        
        metricas = MetricaEficiencia.objects.filter(operario=self)
        if metricas.exists():
            promedio = metricas.aggregate(models.Avg('eficiencia_calculada'))['eficiencia_calculada__avg']
            self.eficiencia_promedio = promedio or 0
            self.save()
```

### 2.6 Turno
**Archivo**: `core/models/turno.py`

```python
from django.db import models

class Turno(models.Model):
    """Turnos de trabajo"""
    
    nombre = models.CharField(max_length=100)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    empresa = models.ForeignKey('Empresa', on_delete=models.CASCADE, related_name='turnos')
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'turnos'
        verbose_name = 'Turno'
        verbose_name_plural = 'Turnos'
        ordering = ['hora_inicio']
    
    def __str__(self):
        return f"{self.nombre} ({self.hora_inicio.strftime('%H:%M')} - {self.hora_fin.strftime('%H:%M')})"
```

---

## 3. Modelos Operacionales

### 3.1 Asignacion
**Archivo**: `core/models/asignacion.py`

```python
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class Asignacion(models.Model):
    """Asignación de un operario a una máquina en un turno específico"""
    
    class EstadoChoices(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        ACTIVA = 'ACTIVA', 'Activa'
        COMPLETADA = 'COMPLETADA', 'Completada'
        CANCELADA = 'CANCELADA', 'Cancelada'
    
    operario = models.ForeignKey(
        'Operario',
        on_delete=models.PROTECT,
        related_name='asignaciones'
    )
    maquina = models.ForeignKey(
        'Maquina',
        on_delete=models.PROTECT,
        related_name='asignaciones'
    )
    turno = models.ForeignKey(
        'Turno',
        on_delete=models.PROTECT,
        related_name='asignaciones'
    )
    
    # Fechas
    fecha = models.DateField(default=timezone.now)
    hora_inicio_real = models.DateTimeField(null=True, blank=True)
    hora_fin_real = models.DateTimeField(null=True, blank=True)
    
    # Estado
    estado = models.CharField(
        max_length=20,
        choices=EstadoChoices.choices,
        default=EstadoChoices.PENDIENTE
    )
    
    # Control
    asignado_por = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='asignaciones_creadas'
    )
    observaciones = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'asignaciones'
        verbose_name = 'Asignación'
        verbose_name_plural = 'Asignaciones'
        ordering = ['-fecha', '-fecha_creacion']
        indexes = [
            models.Index(fields=['fecha', 'estado']),
            models.Index(fields=['operario', 'fecha']),
            models.Index(fields=['maquina', 'fecha']),
        ]
    
    def __str__(self):
        return f"{self.operario} → {self.maquina} ({self.fecha})"
    
    def clean(self):
        """Validaciones personalizadas"""
        # Validar que el operario tenga habilidad para la máquina
        if self.operario and self.maquina:
            if not self.operario.puede_operar(self.maquina):
                raise ValidationError(
                    f"El operario {self.operario} no tiene habilidad para operar {self.maquina.tipo.nombre}"
                )
        
        # Validar que no haya otra asignación activa para el mismo operario
        if self.estado == self.EstadoChoices.ACTIVA:
            asignaciones_activas = Asignacion.objects.filter(
                operario=self.operario,
                estado=self.EstadoChoices.ACTIVA,
                fecha=self.fecha
            ).exclude(id=self.id)
            
            if asignaciones_activas.exists():
                raise ValidationError(
                    f"El operario {self.operario} ya tiene una asignación activa"
                )
    
    def iniciar(self):
        """Marca la asignación como activa"""
        if self.estado != self.EstadoChoices.PENDIENTE:
            raise ValidationError("Solo se pueden iniciar asignaciones pendientes")
        
        self.estado = self.EstadoChoices.ACTIVA
        self.hora_inicio_real = timezone.now()
        self.maquina.cambiar_estado(
            'OPERANDO',
            usuario=self.operario.usuario,
            observacion=f"Iniciado por asignación #{self.id}"
        )
        self.save()
    
    def finalizar(self):
        """Marca la asignación como completada"""
        if self.estado != self.EstadoChoices.ACTIVA:
            raise ValidationError("Solo se pueden finalizar asignaciones activas")
        
        self.estado = self.EstadoChoices.COMPLETADA
        self.hora_fin_real = timezone.now()
        self.operario.total_tareas_completadas += 1
        self.operario.save()
        self.save()
```

### 3.2 Evento
**Archivo**: `core/models/evento.py`

```python
from django.db import models
from django.utils import timezone

class Evento(models.Model):
    """Eventos operacionales (inicio, fin, pausa, reanudación)"""
    
    class TipoEventoChoices(models.TextChoices):
        INICIO = 'INICIO', 'Inicio de Tarea'
        FIN = 'FIN', 'Fin de Tarea'
        PAUSA = 'PAUSA', 'Pausa'
        REANUDACION = 'REANUDACION', 'Reanudación'
        CAMBIO_MAQUINA = 'CAMBIO_MAQUINA', 'Cambio de Máquina'
        INCIDENCIA = 'INCIDENCIA', 'Incidencia Reportada'
    
    asignacion = models.ForeignKey(
        'Asignacion',
        on_delete=models.CASCADE,
        related_name='eventos'
    )
    tipo = models.CharField(
        max_length=20,
        choices=TipoEventoChoices.choices
    )
    fecha_hora = models.DateTimeField(default=timezone.now)
    
    # Datos adicionales
    observaciones = models.TextField(blank=True)
    datos_json = models.JSONField(
        null=True,
        blank=True,
        help_text='Datos adicionales en formato JSON'
    )
    
    # Control
    registrado_por = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='eventos_registrados'
    )
    
    class Meta:
        db_table = 'eventos'
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['-fecha_hora']
        indexes = [
            models.Index(fields=['asignacion', 'tipo']),
            models.Index(fields=['fecha_hora']),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.asignacion} ({self.fecha_hora.strftime('%H:%M')})"
```

### 3.3 Incidencia
**Archivo**: `core/models/incidencia.py`

```python
from django.db import models
from django.utils import timezone

class Incidencia(models.Model):
    """Problemas o incidencias reportadas durante la operación"""
    
    class TipoChoices(models.TextChoices):
        FALLA_MAQUINA = 'FALLA_MAQUINA', 'Falla de Máquina'
        FALTA_MATERIAL = 'FALTA_MATERIAL', 'Falta de Material'
        PROBLEMA_CALIDAD = 'PROBLEMA_CALIDAD', 'Problema de Calidad'
        OTRO = 'OTRO', 'Otro'
    
    class PrioridadChoices(models.TextChoices):
        BAJA = 'BAJA', 'Baja'
        MEDIA = 'MEDIA', 'Media'
        ALTA = 'ALTA', 'Alta'
        CRITICA = 'CRITICA', 'Crítica'
    
    class EstadoChoices(models.TextChoices):
        REPORTADA = 'REPORTADA', 'Reportada'
        EN_ATENCION = 'EN_ATENCION', 'En Atención'
        RESUELTA = 'RESUELTA', 'Resuelta'
        CERRADA = 'CERRADA', 'Cerrada'
    
    asignacion = models.ForeignKey(
        'Asignacion',
        on_delete=models.CASCADE,
        related_name='incidencias'
    )
    maquina = models.ForeignKey(
        'Maquina',
        on_delete=models.PROTECT,
        related_name='incidencias'
    )
    
    # Detalles
    tipo = models.CharField(max_length=20, choices=TipoChoices.choices)
    prioridad = models.CharField(
        max_length=10,
        choices=PrioridadChoices.choices,
        default=PrioridadChoices.MEDIA
    )
    descripcion = models.TextField()
    
    # Estado
    estado = models.CharField(
        max_length=20,
        choices=EstadoChoices.choices,
        default=EstadoChoices.REPORTADA
    )
    
    # Fechas
    fecha_reporte = models.DateTimeField(default=timezone.now)
    fecha_atencion = models.DateTimeField(null=True, blank=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    
    # Personas involucradas
    reportado_por = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='incidencias_reportadas'
    )
    atendido_por = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incidencias_atendidas'
    )
    
    # Resolución
    solucion = models.TextField(blank=True)
    
    class Meta:
        db_table = 'incidencias'
        verbose_name = 'Incidencia'
        verbose_name_plural = 'Incidencias'
        ordering = ['-fecha_reporte']
        indexes = [
            models.Index(fields=['estado', 'prioridad']),
            models.Index(fields=['maquina', 'fecha_reporte']),
        ]
    
    def __str__(self):
        return f"Incidencia #{self.id} - {self.get_tipo_display()} ({self.maquina})"
    
    def tiempo_sin_atender(self):
        """Calcula minutos desde el reporte sin atención"""
        if self.estado == self.EstadoChoices.REPORTADA:
            return (timezone.now() - self.fecha_reporte).total_seconds() / 60
        return 0
    
    def tiempo_resolucion(self):
        """Calcula minutos totales de resolución"""
        if self.fecha_resolucion:
            return (self.fecha_resolucion - self.fecha_reporte).total_seconds() / 60
        return None
```

### 3.4 EstadoMaquina (Historial)
**Archivo**: `core/models/estado_maquina.py`

```python
from django.db import models
from django.utils import timezone

class EstadoMaquina(models.Model):
    """Historial de cambios de estado de las máquinas"""
    
    maquina = models.ForeignKey(
        'Maquina',
        on_delete=models.CASCADE,
        related_name='historial_estados'
    )
    estado = models.CharField(max_length=20)
    fecha_hora = models.DateTimeField(default=timezone.now)
    usuario = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    observacion = models.TextField(blank=True)
    
    class Meta:
        db_table = 'estados_maquina'
        verbose_name = 'Estado de Máquina'
        verbose_name_plural = 'Estados de Máquina'
        ordering = ['-fecha_hora']
        indexes = [
            models.Index(fields=['maquina', 'fecha_hora']),
        ]
    
    def __str__(self):
        return f"{self.maquina} - {self.estado} ({self.fecha_hora.strftime('%d/%m/%Y %H:%M')})"
```

---

## 4. Modelos de Métricas y Eficiencia

### 4.1 RegistroProduccion
**Archivo**: `core/models/registro_produccion.py`

```python
from django.db import models
from django.utils import timezone

class RegistroProduccion(models.Model):
    """Registro de producción (manual o automático)"""
    
    asignacion = models.ForeignKey(
        'Asignacion',
        on_delete=models.CASCADE,
        related_name='registros_produccion'
    )
    
    # Datos de producción
    cantidad_producida = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Cantidad producida en la unidad correspondiente'
    )
    unidad = models.ForeignKey(
        'UnidadEficiencia',
        on_delete=models.PROTECT
    )
    
    # Tiempo
    fecha_hora = models.DateTimeField(default=timezone.now)
    duracion_minutos = models.IntegerField(
        help_text='Duración en minutos de este registro'
    )
    
    # Origen del dato
    es_automatico = models.BooleanField(
        default=False,
        help_text='True si viene de sensor IoT, False si es manual'
    )
    registrado_por = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Observaciones
    observaciones = models.TextField(blank=True)
    
    class Meta:
        db_table = 'registros_produccion'
        verbose_name = 'Registro de Producción'
        verbose_name_plural = 'Registros de Producción'
        ordering = ['-fecha_hora']
        indexes = [
            models.Index(fields=['asignacion', 'fecha_hora']),
        ]
    
    def __str__(self):
        return f"{self.cantidad_producida} {self.unidad.abreviatura} - {self.asignacion}"
```

### 4.2 MetricaEficiencia
**Archivo**: `core/models/metrica_eficiencia.py`

```python
from django.db import models
from django.utils import timezone

class MetricaEficiencia(models.Model):
    """Métricas de eficiencia calculadas"""
    
    # Relaciones
    asignacion = models.ForeignKey(
        'Asignacion',
        on_delete=models.CASCADE,
        related_name='metricas'
    )
    operario = models.ForeignKey(
        'Operario',
        on_delete=models.CASCADE,
        related_name='metricas'
    )
    maquina = models.ForeignKey(
        'Maquina',
        on_delete=models.CASCADE,
        related_name='metricas'
    )
    turno = models.ForeignKey(
        'Turno',
        on_delete=models.CASCADE,
        related_name='metricas'
    )
    
    # Datos de cálculo
    fecha = models.DateField()
    produccion_real = models.DecimalField(max_digits=10, decimal_places=2)
    produccion_teorica = models.DecimalField(max_digits=10, decimal_places=2)
    eficiencia_calculada = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text='Eficiencia en porcentaje'
    )
    
    # Tiempos
    tiempo_operando_minutos = models.IntegerField()
    tiempo_parada_minutos = models.IntegerField(default=0)
    tiempo_total_minutos = models.IntegerField()
    
    # Factores de ajuste (opcional)
    factor_ajuste = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.00,
        help_text='Factor de corrección por dificultad (ej: terreno difícil)'
    )
    
    # Control
    fecha_calculo = models.DateTimeField(default=timezone.now)
    observaciones = models.TextField(blank=True)
    
    class Meta:
        db_table = 'metricas_eficiencia'
        verbose_name = 'Métrica de Eficiencia'
        verbose_name_plural = 'Métricas de Eficiencia'
        ordering = ['-fecha', '-fecha_calculo']
        indexes = [
            models.Index(fields=['fecha', 'operario']),
            models.Index(fields=['fecha', 'maquina']),
            models.Index(fields=['fecha', 'turno']),
        ]
    
    def __str__(self):
        return f"Eficiencia {self.eficiencia_calculada}% - {self.operario} ({self.fecha})"
    
    @staticmethod
    def calcular_eficiencia(produccion_real, produccion_teorica, factor_ajuste=1.0):
        """Calcula el porcentaje de eficiencia"""
        if produccion_teorica == 0:
            return 0
        return round((produccion_real / produccion_teorica) * factor_ajuste * 100, 2)
```

### 4.3 ObjetivoProduccion
**Archivo**: `core/models/objetivo_produccion.py`

```python
from django.db import models

class ObjetivoProduccion(models.Model):
    """Objetivos de producción por máquina, operario o turno"""
    
    class TipoObjetivoChoices(models.TextChoices):
        MAQUINA = 'MAQUINA', 'Por Máquina'
        OPERARIO = 'OPERARIO', 'Por Operario'
        TURNO = 'TURNO', 'Por Turno'
        GLOBAL = 'GLOBAL', 'Global'
    
    tipo = models.CharField(max_length=20, choices=TipoObjetivoChoices.choices)
    
    # Relaciones opcionales
    maquina = models.ForeignKey(
        'Maquina',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='objetivos'
    )
    operario = models.ForeignKey(
        'Operario',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='objetivos'
    )
    turno = models.ForeignKey(
        'Turno',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='objetivos'
    )
    
    # Objetivo
    objetivo_cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    unidad = models.ForeignKey('UnidadEficiencia', on_delete=models.PROTECT)
    
    # Periodo
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'objetivos_produccion'
        verbose_name = 'Objetivo de Producción'
        verbose_name_plural = 'Objetivos de Producción'
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"Objetivo {self.objetivo_cantidad} {self.unidad.abreviatura} ({self.get_tipo_display()})"
```

---

## 5. Modelos de Alertas y Reglas

### 5.1 ReglaAlerta
**Archivo**: `core/models/regla_alerta.py`

```python
from django.db import models

class ReglaAlerta(models.Model):
    """Reglas configurables para generar alertas automáticas"""
    
    class TipoCondicionChoices(models.TextChoices):
        EFICIENCIA_BAJA = 'EFICIENCIA_BAJA', 'Eficiencia Baja'
        MAQUINA_PARADA = 'MAQUINA_PARADA', 'Máquina Parada'
        INCIDENCIA_SIN_ATENDER = 'INCIDENCIA_SIN_ATENDER', 'Incidencia sin Atender'
        TIEMPO_EXCEDIDO = 'TIEMPO_EXCEDIDO', 'Tiempo Excedido'
        PRODUCCION_BAJA = 'PRODUCCION_BAJA', 'Producción Baja'
    
    class PrioridadChoices(models.TextChoices):
        BAJA = 'BAJA', 'Baja'
        MEDIA = 'MEDIA', 'Media'
        ALTA = 'ALTA', 'Alta'
        CRITICA = 'CRITICA', 'Crítica'
    
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    empresa = models.ForeignKey('Empresa', on_delete=models.CASCADE, related_name='reglas_alerta')
    
    # Condición
    tipo_condicion = models.CharField(max_length=30, choices=TipoCondicionChoices.choices)
    parametros = models.JSONField(
        help_text='Parámetros de la regla en JSON (ej: {"umbral": 70, "duracion_minutos": 15})'
    )
    
    # Acción
    prioridad = models.CharField(
        max_length=10,
        choices=PrioridadChoices.choices,
        default=PrioridadChoices.MEDIA
    )
    mensaje_plantilla = models.TextField(
        help_text='Plantilla del mensaje de alerta. Usa {variable} para datos dinámicos'
    )
    
    # Destinatarios
    notificar_supervisor = models.BooleanField(default=True)
    notificar_gerente = models.BooleanField(default=False)
    usuarios_adicionales = models.ManyToManyField(
        'User',
        related_name='reglas_alerta_suscritas',
        blank=True
    )
    
    # Escalamiento
    escalar_si_no_resuelve = models.BooleanField(default=False)
    tiempo_escalamiento_minutos = models.IntegerField(
        null=True,
        blank=True,
        help_text='Minutos antes de escalar'
    )
    
    # Control
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'reglas_alerta'
        verbose_name = 'Regla de Alerta'
        verbose_name_plural = 'Reglas de Alerta'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_condicion_display()})"
```

### 5.2 Alerta
**Archivo**: `core/models/alerta.py`

```python
from django.db import models
from django.utils import timezone

class Alerta(models.Model):
    """Alertas generadas por el sistema"""
    
    class EstadoChoices(models.TextChoices):
        ACTIVA = 'ACTIVA', 'Activa'
        EN_ATENCION = 'EN_ATENCION', 'En Atención'
        RESUELTA = 'RESUELTA', 'Resuelta'
        ESCALADA = 'ESCALADA', 'Escalada'
        CERRADA = 'CERRADA', 'Cerrada'
    
    regla = models.ForeignKey(
        'ReglaAlerta',
        on_delete=models.CASCADE,
        related_name='alertas_generadas'
    )
    
    # Contexto
    asignacion = models.ForeignKey(
        'Asignacion',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='alertas'
    )
    maquina = models.ForeignKey(
        'Maquina',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='alertas'
    )
    incidencia = models.ForeignKey(
        'Incidencia',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='alertas'
    )
    
    # Detalles
    prioridad = models.CharField(max_length=10)
    mensaje = models.TextField()
    datos_contexto = models.JSONField(
        null=True,
        blank=True,
        help_text='Datos adicionales de contexto'
    )
    
    # Estado
    estado = models.CharField(
        max_length=20,
        choices=EstadoChoices.choices,
        default=EstadoChoices.ACTIVA
    )
    
    # Fechas
    fecha_generacion = models.DateTimeField(default=timezone.now)
    fecha_atencion = models.DateTimeField(null=True, blank=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    
    # Gestión
    atendida_por = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alertas_atendidas'
    )
    observaciones_resolucion = models.TextField(blank=True)
    
    # Escalamiento
    fue_escalada = models.BooleanField(default=False)
    fecha_escalamiento = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'alertas'
        verbose_name = 'Alerta'
        verbose_name_plural = 'Alertas'
        ordering = ['-fecha_generacion', '-prioridad']
        indexes = [
            models.Index(fields=['estado', 'prioridad']),
            models.Index(fields=['fecha_generacion']),
        ]
    
    def __str__(self):
        return f"Alerta #{self.id} - {self.regla.nombre} ({self.get_estado_display()})"
    
    def tiempo_sin_atender(self):
        """Calcula minutos desde generación sin atención"""
        if self.estado == self.EstadoChoices.ACTIVA:
            return (timezone.now() - self.fecha_generacion).total_seconds() / 60
        return 0
```

### 5.3 Notificacion
**Archivo**: `core/models/notificacion.py`

```python
from django.db import models
from django.utils import timezone

class Notificacion(models.Model):
    """Log de notificaciones enviadas"""
    
    class CanalChoices(models.TextChoices):
        PLATAFORMA = 'PLATAFORMA', 'En Plataforma'
        EMAIL = 'EMAIL', 'Email'
        TELEGRAM = 'TELEGRAM', 'Telegram'
        WHATSAPP = 'WHATSAPP', 'WhatsApp'
    
    class EstadoChoices(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        ENVIADA = 'ENVIADA', 'Enviada'
        ERROR = 'ERROR', 'Error'
    
    # Relación con alerta
    alerta = models.ForeignKey(
        'Alerta',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notificaciones'
    )
    
    # Destinatario
    usuario = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='notificaciones_recibidas'
    )
    
    # Contenido
    canal = models.CharField(max_length=20, choices=CanalChoices.choices)
    asunto = models.CharField(max_length=200)
    mensaje = models.TextField()
    
    # Estado
    estado = models.CharField(
        max_length=20,
        choices=EstadoChoices.choices,
        default=EstadoChoices.PENDIENTE
    )
    leida = models.BooleanField(default=False)
    
    # Fechas
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    fecha_lectura = models.DateTimeField(null=True, blank=True)
    
    # Control de errores
    intentos_envio = models.IntegerField(default=0)
    mensaje_error = models.TextField(blank=True)
    
    class Meta:
        db_table = 'notificaciones'
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['usuario', 'leida']),
            models.Index(fields=['estado', 'canal']),
        ]
    
    def __str__(self):
        return f"Notificación para {self.usuario.username} ({self.get_canal_display()})"
```

---

## 6. Modelos de Reasignación

### 6.1 SugerenciaReasignacion
**Archivo**: `core/models/sugerencia_reasignacion.py`

```python
from django.db import models
from django.utils import timezone

class SugerenciaReasignacion(models.Model):
    """Sugerencias automáticas de reasignación de operarios"""
    
    class EstadoChoices(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        ACEPTADA = 'ACEPTADA', 'Aceptada'
        RECHAZADA = 'RECHAZADA', 'Rechazada'
        EXPIRADA = 'EXPIRADA', 'Expirada'
    
    class MotivoChoices(models.TextChoices):
        MAQUINA_PARADA = 'MAQUINA_PARADA', 'Máquina Parada'
        BAJO_RENDIMIENTO = 'BAJO_RENDIMIENTO', 'Bajo Rendimiento'
        OPTIMIZACION = 'OPTIMIZACION', 'Optimización'
        INCIDENCIA = 'INCIDENCIA', 'Por Incidencia'
    
    # Operario y máquinas involucradas
    operario = models.ForeignKey(
        'Operario',
        on_delete=models.CASCADE,
        related_name='sugerencias_reasignacion'
    )
    maquina_origen = models.ForeignKey(
        'Maquina',
        on_delete=models.CASCADE,
        related_name='sugerencias_desde',
        null=True,
        blank=True
    )
    maquina_destino = models.ForeignKey(
        'Maquina',
        on_delete=models.CASCADE,
        related_name='sugerencias_hacia'
    )
    
    # Asignación actual afectada
    asignacion_actual = models.ForeignKey(
        'Asignacion',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sugerencias_reasignacion'
    )
    
    # Detalles de la sugerencia
    motivo = models.CharField(max_length=30, choices=MotivoChoices.choices)
    descripcion = models.TextField()
    justificacion = models.TextField(
        help_text='Razón técnica de la sugerencia'
    )
    
    # Impacto estimado
    impacto_eficiencia = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text='Mejora estimada de eficiencia (%)',
        null=True,
        blank=True
    )
    prioridad = models.CharField(max_length=10, default='MEDIA')
    
    # Estado
    estado = models.CharField(
        max_length=20,
        choices=EstadoChoices.choices,
        default=EstadoChoices.PENDIENTE
    )
    
    # Fechas
    fecha_generacion = models.DateTimeField(default=timezone.now)
    fecha_decision = models.DateTimeField(null=True, blank=True)
    fecha_expiracion = models.DateTimeField(
        help_text='La sugerencia expira automáticamente después de este tiempo'
    )
    
    # Decisión
    decidido_por = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='decisiones_reasignacion'
    )
    observaciones_decision = models.TextField(blank=True)
    
    # Nueva asignación creada (si fue aceptada)
    nueva_asignacion = models.ForeignKey(
        'Asignacion',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='generada_por_sugerencia'
    )
    
    class Meta:
        db_table = 'sugerencias_reasignacion'
        verbose_name = 'Sugerencia de Reasignación'
        verbose_name_plural = 'Sugerencias de Reasignación'
        ordering = ['-fecha_generacion', '-prioridad']
        indexes = [
            models.Index(fields=['estado', 'fecha_generacion']),
            models.Index(fields=['operario', 'estado']),
        ]
    
    def __str__(self):
        return f"Sugerencia: {self.operario} → {self.maquina_destino} ({self.get_motivo_display()})"
    
    def aceptar(self, usuario):
        """Acepta la sugerencia y crea la nueva asignación"""
        from .asignacion import Asignacion
        
        if self.estado != self.EstadoChoices.PENDIENTE:
            raise ValueError("Solo se pueden aceptar sugerencias pendientes")
        
        # Finalizar asignación actual si existe
        if self.asignacion_actual and self.asignacion_actual.estado == 'ACTIVA':
            self.asignacion_actual.finalizar()
        
        # Crear nueva asignación
        nueva_asig = Asignacion.objects.create(
            operario=self.operario,
            maquina=self.maquina_destino,
            turno=self.operario.turno_actual,
            fecha=timezone.now().date(),
            asignado_por=usuario,
            observaciones=f"Reasignación automática por sugerencia #{self.id}"
        )
        nueva_asig.iniciar()
        
        # Actualizar sugerencia
        self.estado = self.EstadoChoices.ACEPTADA
        self.fecha_decision = timezone.now()
        self.decidido_por = usuario
        self.nueva_asignacion = nueva_asig
        self.save()
        
        return nueva_asig
    
    def rechazar(self, usuario, motivo=''):
        """Rechaza la sugerencia"""
        if self.estado != self.EstadoChoices.PENDIENTE:
            raise ValueError("Solo se pueden rechazar sugerencias pendientes")
        
        self.estado = self.EstadoChoices.RECHAZADA
        self.fecha_decision = timezone.now()
        self.decidido_por = usuario
        self.observaciones_decision = motivo
        self.save()
```

---

## 7. Modelos de Órdenes y Despacho

### 7.1 OrdenProduccion
**Archivo**: `core/models/orden_produccion.py`

```python
from django.db import models
from django.utils import timezone

class OrdenProduccion(models.Model):
    """Orden de producción o trabajo"""
    
    class EstadoChoices(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        EN_PROCESO = 'EN_PROCESO', 'En Proceso'
        LISTA = 'LISTA', 'Lista para Despacho'
        DESPACHADA = 'DESPACHADA', 'Despachada'
        CANCELADA = 'CANCELADA', 'Cancelada'
    
    class PrioridadChoices(models.TextChoices):
        BAJA = 'BAJA', 'Baja'
        NORMAL = 'NORMAL', 'Normal'
        ALTA = 'ALTA', 'Alta'
        URGENTE = 'URGENTE', 'Urgente'
    
    # Identificación
    numero_orden = models.CharField(max_length=50, unique=True)
    empresa = models.ForeignKey('Empresa', on_delete=models.CASCADE, related_name='ordenes')
    
    # Detalles
    descripcion = models.TextField()
    producto = models.CharField(max_length=200)
    cantidad_solicitada = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad_producida = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unidad = models.ForeignKey('UnidadEficiencia', on_delete=models.PROTECT)
    
    # Fechas
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_limite = models.DateField()
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_finalizacion = models.DateTimeField(null=True, blank=True)
    fecha_despacho = models.DateTimeField(null=True, blank=True)
    
    # Estado y prioridad
    estado = models.CharField(
        max_length=20,
        choices=EstadoChoices.choices,
        default=EstadoChoices.PENDIENTE
    )
    prioridad = models.CharField(
        max_length=10,
        choices=PrioridadChoices.choices,
        default=PrioridadChoices.NORMAL
    )
    
    # Máquina asignada
    maquina_asignada = models.ForeignKey(
        'Maquina',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ordenes'
    )
    
    # Control
    creado_por = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='ordenes_creadas'
    )
    observaciones = models.TextField(blank=True)
    
    class Meta:
        db_table = 'ordenes_produccion'
        verbose_name = 'Orden de Producción'
        verbose_name_plural = 'Órdenes de Producción'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['estado', 'prioridad']),
            models.Index(fields=['fecha_limite']),
            models.Index(fields=['numero_orden']),
        ]
    
    def __str__(self):
        return f"Orden {self.numero_orden} - {self.producto}"
    
    @property
    def porcentaje_completado(self):
        """Calcula el porcentaje de completado"""
        if self.cantidad_solicitada == 0:
            return 0
        return round((self.cantidad_producida / self.cantidad_solicitada) * 100, 2)
    
    @property
    def dias_restantes(self):
        """Calcula días restantes hasta la fecha límite"""
        if self.estado in ['DESPACHADA', 'CANCELADA']:
            return 0
        delta = self.fecha_limite - timezone.now().date()
        return delta.days
    
    def marcar_lista(self):
        """Marca la orden como lista y la pone en cola de despacho"""
        from .cola_despacho import ColaDespacho
        
        if self.estado != self.EstadoChoices.EN_PROCESO:
            raise ValueError("Solo se pueden marcar como listas órdenes en proceso")
        
        self.estado = self.EstadoChoices.LISTA
        self.fecha_finalizacion = timezone.now()
        self.save()
        
        # Agregar a cola de despacho
        ColaDespacho.objects.create(
            orden=self,
            prioridad_calculada=self._calcular_prioridad_despacho()
        )
    
    def _calcular_prioridad_despacho(self):
        """Calcula prioridad numérica para cola de despacho"""
        prioridades = {
            'URGENTE': 1,
            'ALTA': 2,
            'NORMAL': 3,
            'BAJA': 4
        }
        return prioridades.get(self.prioridad, 3)
```

### 7.2 ColaDespacho
**Archivo**: `core/models/cola_despacho.py`

```python
from django.db import models
from django.utils import timezone

class ColaDespacho(models.Model):
    """Cola priorizada de órdenes listas para despacho"""
    
    orden = models.OneToOneField(
        'OrdenProduccion',
        on_delete=models.CASCADE,
        related_name='en_cola_despacho'
    )
    
    # Priorización
    prioridad_calculada = models.IntegerField(
        help_text='Menor número = mayor prioridad'
    )
    fecha_ingreso_cola = models.DateTimeField(default=timezone.now)
    
    # Estado
    despachada = models.BooleanField(default=False)
    fecha_despacho = models.DateTimeField(null=True, blank=True)
    despachada_por = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'cola_despacho'
        verbose_name = 'Cola de Despacho'
        verbose_name_plural = 'Cola de Despacho'
        ordering = ['prioridad_calculada', 'fecha_ingreso_cola']
        indexes = [
            models.Index(fields=['despachada', 'prioridad_calculada']),
        ]
    
    def __str__(self):
        return f"Cola: {self.orden.numero_orden} (Prioridad {self.prioridad_calculada})"
    
    @property
    def tiempo_en_cola_minutos(self):
        """Calcula tiempo en cola en minutos"""
        if self.despachada:
            return (self.fecha_despacho - self.fecha_ingreso_cola).total_seconds() / 60
        return (timezone.now() - self.fecha_ingreso_cola).total_seconds() / 60
    
    def despachar(self, usuario):
        """Marca la orden como despachada"""
        self.orden.estado = 'DESPACHADA'
        self.orden.fecha_despacho = timezone.now()
        self.orden.save()
        
        self.despachada = True
        self.fecha_despacho = timezone.now()
        self.despachada_por = usuario
        self.save()
```

---

## 8. Modelos IoT (Preparados)

### 8.1 SensorIoT
**Archivo**: `core/models/sensor_iot.py`

```python
from django.db import models
from django.utils import timezone

class SensorIoT(models.Model):
    """Sensores IoT conectados (preparado para futuro)"""
    
    class TipoSensorChoices(models.TextChoices):
        GPS = 'GPS', 'GPS'
        CONTADOR = 'CONTADOR', 'Contador de Pulsos'
        VIBRACIÓN = 'VIBRACIÓN', 'Sensor de Vibración'
        CONSUMO = 'CONSUMO', 'Medidor de Consumo'
        TEMPERATURA = 'TEMPERATURA', 'Sensor de Temperatura'
        OTRO = 'OTRO', 'Otro'
    
    codigo = models.CharField(max_length=100, unique=True)
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=20, choices=TipoSensorChoices.choices)
    
    # Configuración MQTT (para futuro)
    topic_mqtt = models.CharField(max_length=200, blank=True)
    configuracion_json = models.JSONField(
        null=True,
        blank=True,
        help_text='Configuración específica del sensor'
    )
    
    # Estado
    activo = models.BooleanField(default=False)
    ultima_lectura = models.DateTimeField(null=True, blank=True)
    
    # Control
    fecha_instalacion = models.DateField(null=True, blank=True)
    observaciones = models.TextField(blank=True)
    
    class Meta:
        db_table = 'sensores_iot'
        verbose_name = 'Sensor IoT'
        verbose_name_plural = 'Sensores IoT'
        ordering = ['codigo']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre} ({'Activo' if self.activo else 'Inactivo'})"
```

### 8.2 DatoSensorIoT
**Archivo**: `core/models/dato_sensor_iot.py`

```python
from django.db import models
from django.utils import timezone

class DatoSensorIoT(models.Model):
    """Datos recibidos de sensores IoT (preparado para futuro)"""
    
    sensor = models.ForeignKey(
        'SensorIoT',
        on_delete=models.CASCADE,
        related_name='datos'
    )
    
    # Datos
    fecha_hora = models.DateTimeField(default=timezone.now)
    valor = models.DecimalField(max_digits=15, decimal_places=5)
    unidad = models.CharField(max_length=50)
    
    # Datos adicionales en JSON
    datos_adicionales = models.JSONField(
        null=True,
        blank=True,
        help_text='Datos extra del sensor (ej: coordenadas GPS, temperatura, etc.)'
    )
    
    class Meta:
        db_table = 'datos_sensores_iot'
        verbose_name = 'Dato de Sensor IoT'
        verbose_name_plural = 'Datos de Sensores IoT'
        ordering = ['-fecha_hora']
        indexes = [
            models.Index(fields=['sensor', 'fecha_hora']),
        ]
    
    def __str__(self):
        return f"{self.sensor.codigo} - {self.valor} {self.unidad} ({self.fecha_hora.strftime('%d/%m/%Y %H:%M')})"
```

---

## 9. Diagrama de Relaciones

```
┌─────────────────┐
│    Empresa      │
└────────┬────────┘
         │
         ├──────────────┐
         │              │
┌────────▼────────┐ ┌──▼──────────────┐
│     User        │ │   Maquina       │
│   (Usuario)     │ │                 │
└────────┬────────┘ └──┬──────────────┘
         │             │
         │             │
┌────────▼────────┐    │
│    Operario     │    │
│  (perfil ext.)  │    │
└────────┬────────┘    │
         │             │
         │             │
┌────────▼─────────────▼─────┐
│       Asignacion           │
│  (operario → máquina)      │
└────────┬───────────────────┘
         │
         ├─────────┬──────────┬──────────┐
         │         │          │          │
┌────────▼───┐ ┌──▼─────┐ ┌──▼────────┐ │
│   Evento   │ │ Incid. │ │  Registro  │ │
│            │ │        │ │ Producción │ │
└────────────┘ └────┬───┘ └──┬─────────┘ │
                    │        │           │
                    │        │           │
               ┌────▼────────▼───────────▼────┐
               │     MetricaEficiencia         │
               └───────────────────────────────┘
                            │
                            │
               ┌────────────▼────────────┐
               │    ReglaAlerta          │
               │  (motor de reglas)      │
               └────────────┬────────────┘
                            │
                            │
               ┌────────────▼────────────┐
               │       Alerta            │
               │  (alertas generadas)    │
               └────────────┬────────────┘
                            │
                            │
               ┌────────────▼────────────┐
               │  SugerenciaReasignacion │
               │  (reasignaciones auto)  │
               └─────────────────────────┘

┌─────────────────────────────────────────┐
│       OrdenProduccion                   │
└────────────┬────────────────────────────┘
             │
             │
┌────────────▼────────────────────────────┐
│        ColaDespacho                     │
│    (órdenes listas priorizadas)         │
└─────────────────────────────────────────┘
```

---

## Notas Finales

### Convenciones Utilizadas
- **Nombres en español**: Campos y modelos en español por ser proyecto educativo
- **db_table explícitas**: Nombres de tabla en plural y snake_case
- **Índices estratégicos**: En campos de búsqueda frecuente
- **JSONField**: Para flexibilidad en configuraciones
- **Soft delete**: No usado, pero se puede agregar campo `eliminado` si se requiere

### Campos Comunes
- `fecha_creacion`: DateTime de creación (auto_now_add=True)
- `fecha_actualizacion`: DateTime de última modificación (auto_now=True)
- `activo/activa`: Boolean para activar/desactivar registros
- `empresa`: ForeignKey para preparar multitenancy

### Próximos Pasos
1. Crear proyecto Django
2. Implementar estos modelos en archivos separados
3. Crear y aplicar migraciones
4. Poblar con datos de prueba
5. Implementar serializers de DRF

---

**Fecha de creación**: 5 de marzo de 2026  
**Proyecto**: FLEX-OP  
**Total de modelos**: 25

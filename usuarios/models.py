"""
Modelos del módulo de Usuarios para FLEX-OP

Este módulo contiene los modelos relacionados con usuarios y empresas:
- User: Usuario extendido con roles
- Empresa: Cliente/empresa que usa el sistema
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Empresa(models.Model):
    # Representa una empresa cliente del sistema
    """
    Empresa cliente del sistema FLEX-OP
    
    Cada empresa es un cliente independiente que:
    - Gestiona sus propios usuarios (operarios, supervisores, gerentes)
    - Administra su parque de máquinas
    - Tiene sus propios datos y métricas aislados de otras empresas
    
    Este modelo permite que FLEX-OP sea multi-tenant (múltiples clientes
    en una sola instalación del sistema).
    """
    
    # Información básica de la empresa
    nombre = models.CharField(max_length=200, unique=True)
    razon_social = models.CharField(max_length=200)
    
    # RUC: Registro Único de Contribuyentes (identificación tributaria en Perú)
    # En otros países puede ser: RFC (México), CUIT (Argentina), NIT (Colombia), etc.
    ruc = models.CharField(max_length=20, unique=True)
    
    # Información de contacto
    direccion = models.TextField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField()
    
    # Imagen corporativa
    logo = models.ImageField(
        upload_to='empresas/',  # Archivos se guardan en media/empresas/
        blank=True,
        null=True
    )
    
    # Estado de la cuenta
    activa = models.BooleanField(
        default=True,
        help_text='Si está inactiva, los usuarios no podrán acceder al sistema'
    )
    
    # Auditoría: campos automáticos de creación y modificación
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        """Configuración del modelo en la base de datos"""
        db_table = 'empresas'
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['nombre']  # Ordenar alfabéticamente por nombre
    
    def __str__(self):
        """Representación en texto: nombre de la empresa"""
        return self.nombre


class User(AbstractUser):
    # Usuario del sistema con roles y vinculación a empresa
    """
    Usuario extendido con roles del sistema
    
    Hereda de AbstractUser que ya incluye:
    - username, password, email
    - first_name, last_name
    - is_staff, is_active, is_superuser
    - date_joined, last_login
    
    Agrega campos específicos para FLEX-OP:
    - rol: Define el nivel de acceso del usuario
    - empresa: Relación para soportar múltiples empresas (multitenancy)
    - campos adicionales: teléfono, foto, etc.
    """
    
    class RolChoices(models.TextChoices):
        """
        Definición de roles disponibles en el sistema
        
        Cada rol tiene diferentes permisos y acceso a funcionalidades:
        - OPERARIO: Usuario de piso que opera máquinas y registra producción
        - SUPERVISOR: Supervisa operarios y puede reasignar tareas
        - GERENTE: Visualiza KPIs y toma decisiones estratégicas
        - ADMIN: Administrador con acceso completo al sistema
        """
        OPERARIO = 'OPERARIO', 'Operario'
        SUPERVISOR = 'SUPERVISOR', 'Supervisor'
        GERENTE = 'GERENTE', 'Gerente'
        ADMIN = 'ADMIN', 'Administrador'
    
    # Campo de rol con valor por defecto OPERARIO
    rol = models.CharField(
        max_length=20,
        choices=RolChoices.choices,
        default=RolChoices.OPERARIO,
        verbose_name='Rol'
    )
    
    # Campos adicionales de contacto e información
    telefono = models.CharField(max_length=20, blank=True, null=True)
    foto_perfil = models.ImageField(
        upload_to='perfiles/',  # Las fotos se guardan en media/perfiles/
        blank=True, 
        null=True
    )
    
    # Control de estado del usuario
    activo = models.BooleanField(default=True)
    fecha_ingreso = models.DateField(auto_now_add=True)
    
    # Relación con empresa (preparado para multitenancy)
    # Si se elimina la empresa, se eliminan todos sus usuarios (CASCADE)
    empresa = models.ForeignKey(
        'Empresa',
        on_delete=models.CASCADE,
        related_name='usuarios',  # Acceso inverso: empresa.usuarios.all()
        null=True,
        blank=True
    )
    
    class Meta:
        """Configuración del modelo en la base de datos"""
        db_table = 'usuarios'  # Nombre de la tabla en la BD
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['username']  # Orden por defecto al listar
    
    def __str__(self):
        """
        Representación en texto del usuario
        Retorna nombre completo o username si no hay nombre
        """
        return f"{self.get_full_name() or self.username} ({self.get_rol_display()})"
    
    # Propiedades de conveniencia para verificar roles
    # Permiten escribir: if user.es_operario: en lugar de if user.rol == 'OPERARIO':
    
    @property
    def es_operario(self):
        """Verifica si el usuario es operario"""
        return self.rol == self.RolChoices.OPERARIO
    
    @property
    def es_supervisor(self):
        """Verifica si el usuario es supervisor"""
        return self.rol == self.RolChoices.SUPERVISOR
    
    @property
    def es_gerente(self):
        """Verifica si el usuario es gerente"""
        return self.rol == self.RolChoices.GERENTE
    
    @property
    def es_admin(self):
        """Verifica si el usuario es administrador"""
        return self.rol == self.RolChoices.ADMIN

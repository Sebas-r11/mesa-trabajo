"""
Configuración del Admin para el módulo de Máquinas
"""
from django.contrib import admin
from .models import TipoMaquina, UnidadEficiencia, Maquina, EstadoMaquina


@admin.register(TipoMaquina)
class TipoMaquinaAdmin(admin.ModelAdmin):
    """Admin para TipoMaquina"""
    
    list_display = ['nombre', 'empresa', 'descripcion']
    list_filter = ['empresa']
    search_fields = ['nombre', 'descripcion']


@admin.register(UnidadEficiencia)
class UnidadEficienciaAdmin(admin.ModelAdmin):
    """Admin para UnidadEficiencia"""
    
    list_display = ['nombre', 'abreviatura', 'empresa']
    list_filter = ['empresa']
    search_fields = ['nombre', 'abreviatura']


@admin.register(Maquina)
class MaquinaAdmin(admin.ModelAdmin):
    """Admin para Máquina"""
    
    list_display = ['codigo', 'nombre', 'tipo', 'empresa', 'estado_actual', 'activa']
    list_filter = ['estado_actual', 'tipo', 'empresa', 'activa']
    search_fields = ['codigo', 'nombre', 'marca', 'modelo']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    fieldsets = [
        ('Identificación', {
            'fields': ('codigo', 'nombre', 'tipo', 'empresa')
        }),
        ('Especificaciones', {
            'fields': ('marca', 'modelo', 'numero_serie', 'ubicacion')
        }),
        ('Capacidad', {
            'fields': ('capacidad_teorica', 'unidad_capacidad')
        }),
        ('Estado', {
            'fields': ('estado_actual', 'activa')
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    ]


@admin.register(EstadoMaquina)
class EstadoMaquinaAdmin(admin.ModelAdmin):
    """Admin para EstadoMaquina"""
    
    list_display = ['maquina', 'estado', 'fecha_hora', 'usuario']
    list_filter = ['estado', 'fecha_hora']
    search_fields = ['maquina__codigo', 'maquina__nombre']
    readonly_fields = ['fecha_hora']
    date_hierarchy = 'fecha_hora'


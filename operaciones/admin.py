"""
Configuración del Admin para el módulo de Operaciones
"""
from django.contrib import admin
from .models import Turno, Habilidad, Operario


@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    """Admin para Turno"""
    
    list_display = ['nombre', 'hora_inicio', 'hora_fin', 'empresa', 'activo']
    list_filter = ['empresa', 'activo']
    search_fields = ['nombre']


@admin.register(Habilidad)
class HabilidadAdmin(admin.ModelAdmin):
    """Admin para Habilidad"""
    
    list_display = ['nombre', 'empresa', 'descripcion']
    list_filter = ['empresa']
    search_fields = ['nombre', 'descripcion']
    filter_horizontal = ['tipos_maquina']


@admin.register(Operario)
class OperarioAdmin(admin.ModelAdmin):
    """Admin para Operario"""
    
    list_display = ['codigo_empleado', 'usuario', 'turno_actual', 'disponible', 'activo', 'eficiencia_promedio']
    list_filter = ['disponible', 'activo', 'turno_actual']
    search_fields = ['codigo_empleado', 'usuario__username', 'usuario__first_name', 'usuario__last_name']
    readonly_fields = ['eficiencia_promedio', 'total_tareas_completadas']
    filter_horizontal = ['habilidades']
    
    fieldsets = [
        ('Usuario', {
            'fields': ('usuario', 'codigo_empleado', 'fecha_contratacion')
        }),
        ('Habilidades y Turno', {
            'fields': ('habilidades', 'turno_actual')
        }),
        ('Estado', {
            'fields': ('disponible', 'activo')
        }),
        ('Métricas', {
            'fields': ('eficiencia_promedio', 'total_tareas_completadas'),
            'classes': ('collapse',)
        }),
    ]


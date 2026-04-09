"""
Configuración del Admin para el módulo de Usuarios
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Empresa


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin personalizado para User"""
    
    list_display = ['username', 'email', 'first_name', 'last_name', 'rol', 'empresa', 'activo']
    list_filter = ['rol', 'activo', 'empresa']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información FLEX-OP', {
            'fields': ('rol', 'telefono', 'foto_perfil', 'activo', 'empresa')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Información FLEX-OP', {
            'fields': ('rol', 'telefono', 'empresa')
        }),
    )


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    """Admin para Empresa"""
    
    list_display = ['nombre', 'ruc', 'email', 'activa', 'fecha_creacion']
    list_filter = ['activa']
    search_fields = ['nombre', 'ruc', 'razon_social']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    fieldsets = [
        ('Información Básica', {
            'fields': ('nombre', 'razon_social', 'ruc')
        }),
        ('Contacto', {
            'fields': ('direccion', 'telefono', 'email')
        }),
        ('Configuración', {
            'fields': ('logo', 'activa')
        }),
        ('Auditoría', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    ]


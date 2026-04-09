# FLEX-OP - Estructura Modular

Sistema de Gestión de Operaciones Flexibles desarrollado con Django y arquitectura modular.

## Estructura del Proyecto

```
ProyectoWorkT/
├── flexop/                   # Configuración principal del proyecto
│   ├── settings.py          # Configuración de Django
│   ├── urls.py              # URLs principales
│   └── wsgi.py
│
├── usuarios/                 # Módulo de Usuarios y Empresas
│   ├── models.py            # User, Empresa
│   ├── serializers.py       # UserSerializer, EmpresaSerializer
│   ├── views.py             # UserViewSet, EmpresaViewSet
│   ├── admin.py             # Admin personalizado
│   └── urls.py              # URLs del módulo
│
├── maquinas/                 # Módulo de Máquinas
│   ├── models.py            # TipoMaquina, UnidadEficiencia, Maquina, EstadoMaquina
│   ├── serializers.py       # Serializers de máquinas
│   ├── views.py             # ViewSets de máquinas
│   ├── admin.py             # Admin de máquinas
│   └── urls.py              # URLs del módulo
│
├── operaciones/              # Módulo de Operaciones
│   ├── models.py            # Turno, Habilidad, Operario
│   ├── serializers.py       # Serializers de operaciones
│   ├── views.py             # ViewSets de operaciones
│   ├── admin.py             # Admin de operaciones
│   └── urls.py              # URLs del módulo
│
├── populate_db.py           # Script para datos de prueba
├── manage.py                # CLI de Django
├── requirements.txt         # Dependencias
└── .env                     # Variables de entorno
```

## Módulos

### 1. Usuarios (`usuarios/`)
**Responsabilidad**: Gestión de usuarios y empresas (multi-tenant)

**Modelos**:
- `User`: Usuario extendido con roles (Admin, Gerente, Supervisor, Operario)
- `Empresa`: Cliente/empresa que usa el sistema

**Endpoints**:
- `/api/usuarios/` - CRUD de usuarios
- `/api/usuarios/me/` - Usuario actual
- `/api/usuarios/{id}/change_password/` - Cambiar contraseña
- `/api/usuarios/operarios/` - Listar operarios
- `/api/usuarios/supervisores/` - Listar supervisores
- `/api/empresas/` - CRUD de empresas

### 2. Máquinas (`maquinas/`)
**Responsabilidad**: Gestión de equipos productivos y sus estados

**Modelos**:
- `TipoMaquina`: Categorías de máquinas (Llenadora, Tractor, etc.)
- `UnidadEficiencia`: Unidades de medida (u/h, kg/h, ha/h)
- `Maquina`: Equipos con capacidad y estado
- `EstadoMaquina`: Historial de cambios de estado

**Endpoints**:
- `/api/tipos-maquina/` - CRUD de tipos
- `/api/unidades-eficiencia/` - CRUD de unidades
- `/api/maquinas/` - CRUD de máquinas
- `/api/maquinas/disponibles/` - Máquinas disponibles
- `/api/maquinas/operando/` - Máquinas operando
- `/api/maquinas/{id}/cambiar_estado/` - Cambiar estado

### 3. Operaciones (`operaciones/`)
**Responsabilidad**: Gestión de operarios, habilidades y turnos

**Modelos**:
- `Turno`: Turnos de trabajo (Mañana, Tarde, Noche)
- `Habilidad`: Competencias técnicas de operarios
- `Operario`: Perfil extendido con habilidades y métricas

**Endpoints**:
- `/api/turnos/` - CRUD de turnos
- `/api/habilidades/` - CRUD de habilidades
- `/api/operarios/` - CRUD de operarios
- `/api/operarios/disponibles/` - Operarios disponibles
- `/api/operarios/{id}/puede_operar_maquina/` - Validar habilidad

## Instalación

```bash
# Activar entorno virtual
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Aplicar migraciones
python manage.py migrate

# Poblar base de datos
python populate_db.py

# Iniciar servidor
python manage.py runserver
```

## Acceso al Sistema

**Servidor**: http://127.0.0.1:8000/

**Admin**: http://127.0.0.1:8000/admin/
- Usuario: `admin`
- Contraseña: `admin123`

**Swagger**: http://127.0.0.1:8000/swagger/

**Credenciales de prueba**:
- Admin: `admin` / `admin123`
- Supervisor: `supervisor1` / `super123`
- Gerente: `gerente1` / `gerente123`
- Operarios: `operario1-3` / `operario123`

## Ventajas de la Estructura Modular

### 1. Organización Clara
- Cada módulo tiene responsabilidad única y definida
- Fácil de navegar y entender
- Código agrupado por funcionalidad

### 2. Mantenibilidad
- Cambios en un módulo no afectan a otros
- Código más limpio y manejable
- Fácil identificar dónde hacer cambios

### 3. Escalabilidad
- Agregar nuevos módulos es sencillo
- Módulos pueden crecer independientemente
- Reutilización de componentes

### 4. Trabajo en Equipo
- Diferentes desarrolladores pueden trabajar en módulos distintos
- Menos conflictos en control de versiones
- Revisiones de código más enfocadas

### 5. Testing
- Tests organizados por módulo
- Pruebas unitarias más específicas
- Facilita TDD (Test Driven Development)

## Tecnologías

- **Django 6.0.3**: Framework web principal
- **Django REST Framework 3.16.1**: API REST
- **djangorestframework-simplejwt 5.5.1**: Autenticación JWT
- **drf-yasg 1.21.15**: Documentación OpenAPI/Swagger
- **django-cors-headers 4.9.0**: CORS
- **Pillow 12.1.1**: Manejo de imágenes
- **python-dotenv 1.2.2**: Variables de entorno

## Relaciones Entre Módulos

```
usuarios.Empresa
    ↓ (1:N)
usuarios.User ←──────────┐
    ↓ (1:1)              │
operaciones.Operario     │
    ↓ (N:M)              │
operaciones.Habilidad    │
    ↓ (N:M)              │
maquinas.TipoMaquina     │
    ↓ (1:N)              │
maquinas.Maquina ────────┘
    ↓ (1:N)
maquinas.EstadoMaquina
```

## Próximos Pasos

- **Fase 3**: Módulo de asignaciones (operario → máquina)
- **Fase 4**: Cálculo de eficiencia en tiempo real
- **Fase 5**: Sistema de alertas automáticas
- **Fase 6**: Motor de reasignación inteligente

## Documentación Adicional

- `PLAN_DESARROLLO.md`: Plan completo de 10 fases
- `MODELOS_DJANGO.md`: Documentación detallada de modelos
- `FASE1_2_COMPLETADA.md`: Resumen de fases completadas

---

**Desarrollado con**: Django 6.0 + DRF + JWT
**Fecha**: 5 de marzo de 2026
**Arquitectura**: Modular por funcionalidad

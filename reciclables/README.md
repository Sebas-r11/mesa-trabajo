# FLEX-OP - Flexible Operations Platform

Sistema de gestión de operaciones productivas que optimiza la eficiencia mediante la coordinación inteligente de recursos humanos, maquinaria y procesos medibles.

## Estado del Proyecto

Fase 1 Completada: Configuración inicial y modelos base con autenticación JWT
Fase 2 Completada: Módulo de configuración con gestión de máquinas y operarios

## Funcionalidades Implementadas

### Fase 1: Configuración Inicial y Modelos Base
- Proyecto Django configurado con Django REST Framework
- Autenticación JWT con roles (Operario, Supervisor, Gerente, Admin)
- Modelo de Usuario extendido con permisos por rol
- Modelo de Empresa (preparado para multitenancy)
- Sistema de migraciones aplicado
- Admin de Django personalizado

### Fase 2: Módulo de Configuración
- Gestión de Máquinas (CRUD completo)
- Gestión de Operarios con habilidades
- Tipos de Máquina
- Unidades de Eficiencia personalizables
- Gestión de Turnos
- Habilidades y asignación a operarios
- API REST completa con endpoints documentados
- Validaciones de negocio implementadas

## Stack Tecnológico

- **Backend**: Python 3.12 + Django 6.0
- **API**: Django REST Framework 3.16
- **Autenticación**: JWT (Simple JWT)
- **Base de Datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Documentación API**: Swagger/OpenAPI (drf-yasg)
- **CORS**: django-cors-headers

## Instalación

### Prerrequisitos
- Python 3.10 o superior
- pip
- virtualenv (recomendado)

### Pasos de instalación

1. **Clonar o navegar al directorio del proyecto**
```bash
cd /home/sebastian/Escritorio/ProyectoWorkT
```

2. **Activar entorno virtual (ya configurado)**
```bash
source .venv/bin/activate
```

3. **Instalar dependencias** (ya instaladas)
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
El archivo `.env` ya está configurado con valores de desarrollo.

5. **Aplicar migraciones** (ya aplicadas)
```bash
python manage.py migrate
```

6. **Crear datos de prueba** (ya creados)
```bash
python manage.py shell < populate_db.py
```

## Ejecutar el Servidor

```bash
python manage.py runserver
```

El servidor estará disponible en: `http://127.0.0.1:8000/`

## Acceso a la Documentación

### Admin de Django
- **URL**: http://127.0.0.1:8000/admin/
- **Usuario**: `admin`
- **Contraseña**: `admin123`

### Documentación de API (Swagger)
- **URL**: http://127.0.0.1:8000/swagger/
- Interfaz interactiva para probar todos los endpoints

### Documentación de API (ReDoc)
- **URL**: http://127.0.0.1:8000/redoc/
- Documentación en formato amigable

## Credenciales de Prueba

### Usuarios del Sistema

| Rol | Username | Password | Descripción |
|-----|----------|----------|-------------|
| Admin | `admin` | `admin123` | Acceso completo al sistema |
| Supervisor | `supervisor1` | `super123` | Gestión de operaciones |
| Gerente | `gerente1` | `gerente123` | Visualización de KPIs |
| Operario | `operario1` | `operario123` | Juan Pérez - Llenadora |
| Operario | `operario2` | `operario123` | Ana López - Etiquetadora |
| Operario | `operario3` | `operario123` | Pedro Ramírez - Ambas |

## Autenticación JWT

### Obtener Token
```bash
POST http://127.0.0.1:8000/api/auth/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Respuesta:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Usar Token en Peticiones
Agregar header en todas las peticiones:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Refrescar Token
```bash
POST http://127.0.0.1:8000/api/auth/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## Endpoints Principales

### Autenticación
- `POST /api/auth/login/` - Obtener tokens JWT
- `POST /api/auth/refresh/` - Refrescar token de acceso
- `POST /api/auth/verify/` - Verificar validez del token

### Usuarios
- `GET /api/usuarios/` - Listar usuarios
- `POST /api/usuarios/` - Crear usuario
- `GET /api/usuarios/{id}/` - Detalle de usuario
- `GET /api/usuarios/me/` - Usuario actual
- `POST /api/usuarios/{id}/change_password/` - Cambiar contraseña
- `GET /api/usuarios/operarios/` - Listar solo operarios
- `GET /api/usuarios/supervisores/` - Listar solo supervisores

### Empresas
- `GET /api/empresas/` - Listar empresas
- `POST /api/empresas/` - Crear empresa
- `GET /api/empresas/{id}/` - Detalle de empresa

### Máquinas
- `GET /api/maquinas/` - Listar máquinas
- `POST /api/maquinas/` - Crear máquina
- `GET /api/maquinas/{id}/` - Detalle de máquina
- `GET /api/maquinas/disponibles/` - Máquinas disponibles
- `GET /api/maquinas/operando/` - Máquinas en operación
- `POST /api/maquinas/{id}/cambiar_estado/` - Cambiar estado

### Operarios
- `GET /api/operarios/` - Listar operarios
- `POST /api/operarios/` - Crear operario
- `GET /api/operarios/{id}/` - Detalle de operario
- `GET /api/operarios/disponibles/` - Operarios disponibles
- `GET /api/operarios/{id}/puede_operar_maquina/?maquina_id=1` - Verificar habilidad

### Configuración
- `GET /api/tipos-maquina/` - Tipos de máquina
- `GET /api/habilidades/` - Habilidades
- `GET /api/unidades-eficiencia/` - Unidades de medida
- `GET /api/turnos/` - Turnos de trabajo

## Estructura del Proyecto

```
ProyectoWorkT/
├── flexop/                 # Configuración del proyecto Django
│   ├── settings.py        # Configuración principal
│   ├── urls.py            # URLs principales
│   └── wsgi.py
├── core/                  # App principal
│   ├── models/           # Modelos de datos
│   │   ├── empresa.py
│   │   ├── user.py
│   │   ├── maquina.py
│   │   ├── operario.py
│   │   └── ...
│   ├── serializers/      # Serializers de DRF
│   │   ├── user_serializer.py
│   │   ├── config_serializers.py
│   │   └── ...
│   ├── views/            # ViewSets de DRF
│   │   ├── auth_views.py
│   │   ├── config_views.py
│   │   └── ...
│   ├── admin.py          # Configuración del admin
│   └── urls.py           # URLs de la app
├── manage.py             # CLI de Django
├── requirements.txt      # Dependencias
├── .env                  # Variables de entorno
├── populate_db.py        # Script de datos de prueba
└── README.md            # Este archivo
```

## Modelos de Datos

### Modelos Implementados (Fases 1-2)

1. **Empresa** - Cliente que usa el sistema
2. **User** - Usuario con roles (Admin, Gerente, Supervisor, Operario)
3. **TipoMaquina** - Categorías de máquinas
4. **Maquina** - Equipos productivos con estados
5. **Habilidad** - Competencias de operarios
6. **UnidadEficiencia** - Unidades de medida (u/h, ha/h, kg/h)
7. **Turno** - Turnos de trabajo
8. **Operario** - Perfil extendido con habilidades
9. **EstadoMaquina** - Historial de cambios de estado

## Testing

### Probar con cURL

**Login:**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

**Listar máquinas (con token):**
```bash
curl -X GET http://127.0.0.1:8000/api/maquinas/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Probar con Swagger
1. Ir a http://127.0.0.1:8000/swagger/
2. Hacer login para obtener token
3. Hacer clic en "Authorize" y pegar el token
3. Probar cualquier endpoint interactivamente

## Próximas Fases

### Fase 3: Módulo de Operaciones y Asignaciones (Pendiente)
- Modelo de Asignación (operario → máquina)
- Registro de eventos (inicio/fin de tarea)
- Sistema de incidencias
- Validaciones de asignación

### Fase 4: Cálculo de Eficiencia (Pendiente)
- Motor de cálculo de eficiencia
- Registro de producción
- Métricas por operario/máquina/turno
- Históricos de eficiencia

### Fase 5: Sistema de Alertas (Pendiente)
- Motor de reglas configurables
- Generación automática de alertas
- Sistema de notificaciones
- Escalamiento de incidencias

## Contribución

Este es un proyecto educativo desarrollado con métodos simples y claros para facilitar el aprendizaje de Django y DRF.

## Licencia

Proyecto educativo - FLEX-OP Platform

---

**Última actualización**: 5 de marzo de 2026  
**Versión**: 1.0 - Fases 1 y 2 completadas

# Modulo de Usuarios - FLEX-OP

Este documento describe todos los endpoints disponibles en el modulo de usuarios.
El modulo gestiona la autenticacion, usuarios, empresas y roles del sistema.


## Autenticacion

La API utiliza JSON Web Tokens (JWT) para autenticacion. Todos los endpoints
protegidos requieren enviar el token en el header Authorization.

### Obtener Token de Acceso

```
POST /api/auth/login/
```

Autentica un usuario y retorna los tokens de acceso y refresco.

**Body de la peticion:**
```json
{
    "username": "usuario@empresa.com",
    "password": "contraseña123"
}
```

**Respuesta exitosa (200):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
}
```

**Como usar el token:**
Incluir en todas las peticiones protegidas:
```
Authorization: Bearer <access_token>
```


### Refrescar Token

```
POST /api/auth/refresh/
```

Obtiene un nuevo token de acceso usando el token de refresco.

**Body de la peticion:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
}
```

**Respuesta exitosa (200):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
}
```


### Verificar Token

```
POST /api/auth/verify/
```

Verifica si un token es valido.

**Body de la peticion:**
```json
{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
}
```

**Respuesta exitosa (200):**
```json
{}
```

**Token invalido (401):**
```json
{
    "detail": "Token is invalid or expired"
}
```


## Empresas

Las empresas son la entidad principal que agrupa a todos los usuarios,
maquinas y operaciones en el sistema.


### Listar Empresas

```
GET /api/empresas/
```

Retorna la lista de empresas (solo para superusuarios, usuarios normales 
ven solo su empresa).

**Parametros de consulta opcionales:**
- `activa`: Filtrar por estado activo (true/false)
- `search`: Buscar por nombre o razon social

**Respuesta exitosa (200):**
```json
[
    {
        "id": 1,
        "nombre": "Industrias ABC",
        "razon_social": "Industrias ABC S.A.C.",
        "ruc": "20123456789",
        "direccion": "Av. Industrial 123, Lima",
        "telefono": "01-2345678",
        "email": "contacto@industriasabc.com",
        "activa": true,
        "created_at": "2026-01-15T10:30:00Z"
    }
]
```


### Obtener Detalle de Empresa

```
GET /api/empresas/{id}/
```

Retorna el detalle completo de una empresa especifica.

**Respuesta exitosa (200):**
```json
{
    "id": 1,
    "nombre": "Industrias ABC",
    "razon_social": "Industrias ABC S.A.C.",
    "ruc": "20123456789",
    "direccion": "Av. Industrial 123, Lima",
    "telefono": "01-2345678",
    "email": "contacto@industriasabc.com",
    "activa": true,
    "created_at": "2026-01-15T10:30:00Z"
}
```


### Crear Empresa

```
POST /api/empresas/
```

Crea una nueva empresa en el sistema.

**Body de la peticion:**
```json
{
    "nombre": "Nueva Empresa",
    "razon_social": "Nueva Empresa S.A.C.",
    "ruc": "20987654321",
    "direccion": "Calle Nueva 456, Lima",
    "telefono": "01-9876543",
    "email": "info@nuevaempresa.com"
}
```

**Respuesta exitosa (201):**
```json
{
    "id": 2,
    "nombre": "Nueva Empresa",
    "razon_social": "Nueva Empresa S.A.C.",
    "ruc": "20987654321",
    "direccion": "Calle Nueva 456, Lima",
    "telefono": "01-9876543",
    "email": "info@nuevaempresa.com",
    "activa": true,
    "created_at": "2026-03-09T15:45:00Z"
}
```


### Actualizar Empresa

```
PUT /api/empresas/{id}/
PATCH /api/empresas/{id}/
```

Actualiza los datos de una empresa existente.
PUT requiere todos los campos, PATCH permite actualizacion parcial.

**Body de la peticion (PATCH):**
```json
{
    "telefono": "01-1111111",
    "direccion": "Nueva Direccion 789"
}
```


### Eliminar Empresa

```
DELETE /api/empresas/{id}/
```

Elimina una empresa. Esta accion es irreversible y eliminara todos los
datos asociados a la empresa.


## Usuarios

Los usuarios son las personas que acceden al sistema. Cada usuario pertenece
a una empresa y tiene un rol asignado.


### Listar Usuarios

```
GET /api/usuarios/
```

Retorna la lista de usuarios de la empresa del usuario autenticado.

**Parametros de consulta opcionales:**
- `rol`: Filtrar por rol (GERENTE, SUPERVISOR, OPERARIO)
- `is_active`: Filtrar por estado activo
- `search`: Buscar por nombre, apellido o email

**Respuesta exitosa (200):**
```json
[
    {
        "id": 1,
        "email": "gerente@empresa.com",
        "first_name": "Juan",
        "last_name": "Perez",
        "rol": "GERENTE",
        "empresa": 1,
        "empresa_nombre": "Industrias ABC",
        "is_active": true,
        "date_joined": "2026-01-15T10:30:00Z"
    },
    {
        "id": 2,
        "email": "supervisor@empresa.com",
        "first_name": "Maria",
        "last_name": "Garcia",
        "rol": "SUPERVISOR",
        "empresa": 1,
        "empresa_nombre": "Industrias ABC",
        "is_active": true,
        "date_joined": "2026-02-01T08:00:00Z"
    }
]
```


### Obtener Usuario

```
GET /api/usuarios/{id}/
```

Retorna el detalle de un usuario especifico.


### Crear Usuario

```
POST /api/usuarios/
```

Crea un nuevo usuario en el sistema.

**Body de la peticion:**
```json
{
    "email": "nuevo@empresa.com",
    "password": "contraseña123",
    "first_name": "Pedro",
    "last_name": "Lopez",
    "rol": "OPERARIO",
    "empresa": 1
}
```

**Validaciones:**
- El email debe ser unico en el sistema
- La contraseña debe tener al menos 8 caracteres
- El rol debe ser uno de: GERENTE, SUPERVISOR, OPERARIO


### Actualizar Usuario

```
PUT /api/usuarios/{id}/
PATCH /api/usuarios/{id}/
```

Actualiza los datos de un usuario.


### Eliminar Usuario

```
DELETE /api/usuarios/{id}/
```

Elimina un usuario del sistema. Considerar desactivar en lugar de eliminar
para mantener el historial.


### Obtener Mi Perfil

```
GET /api/usuarios/me/
```

Retorna los datos del usuario actualmente autenticado.

**Respuesta exitosa (200):**
```json
{
    "id": 5,
    "email": "usuario@empresa.com",
    "first_name": "Carlos",
    "last_name": "Ramirez",
    "rol": "SUPERVISOR",
    "empresa": 1,
    "empresa_nombre": "Industrias ABC",
    "is_active": true,
    "permisos": ["ver_reportes", "gestionar_operarios"]
}
```


### Cambiar Mi Contraseña

```
POST /api/usuarios/cambiar_password/
```

Permite al usuario cambiar su propia contraseña.

**Body de la peticion:**
```json
{
    "password_actual": "contraseña_actual",
    "password_nuevo": "nueva_contraseña",
    "password_confirmacion": "nueva_contraseña"
}
```

**Respuesta exitosa (200):**
```json
{
    "mensaje": "Contraseña actualizada correctamente"
}
```

**Errores posibles:**
- 400: La contraseña actual es incorrecta
- 400: Las contraseñas no coinciden
- 400: La nueva contraseña no cumple requisitos de seguridad


## Roles y Permisos

El sistema define tres roles principales:

| Rol | Descripcion | Permisos principales |
|-----|-------------|---------------------|
| GERENTE | Administrador de la empresa | Acceso total, reportes gerenciales, configuracion |
| SUPERVISOR | Encargado de turno | Gestionar operarios, alertas, asignaciones |
| OPERARIO | Personal de produccion | Ver sus asignaciones, registrar produccion |


## Codigos de Error Comunes

| Codigo | Descripcion |
|--------|-------------|
| 400 | Datos invalidos en la peticion |
| 401 | No autenticado o token invalido |
| 403 | Sin permisos para esta accion |
| 404 | Recurso no encontrado |
| 500 | Error interno del servidor |


## Notas de Implementacion

1. Todos los endpoints requieren autenticacion excepto login
2. Los usuarios solo pueden ver datos de su propia empresa
3. Los tokens de acceso expiran en 30 minutos
4. Los tokens de refresco expiran en 7 dias
5. Las contraseñas se almacenan hasheadas con PBKDF2

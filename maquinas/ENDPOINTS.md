# Modulo de Maquinas - FLEX-OP

Este documento describe todos los endpoints disponibles en el modulo de maquinas.
El modulo gestiona las maquinas de produccion, sus tipos, y los productos
que pueden fabricar.


## Tipos de Maquina

Los tipos de maquina permiten categorizar las maquinas segun su funcion
en la planta.


### Listar Tipos de Maquina

```
GET /api/tipos-maquina/
```

Retorna todos los tipos de maquina de la empresa.

**Parametros de consulta opcionales:**
- `activo`: Filtrar por estado activo (true/false)

**Respuesta exitosa (200):**
```json
[
    {
        "id": 1,
        "nombre": "Inyectora",
        "descripcion": "Maquinas de inyeccion de plastico",
        "empresa": 1,
        "activo": true,
        "created_at": "2026-01-15T10:30:00Z"
    },
    {
        "id": 2,
        "nombre": "Extrusora",
        "descripcion": "Maquinas de extrusion continua",
        "empresa": 1,
        "activo": true,
        "created_at": "2026-01-16T08:00:00Z"
    }
]
```


### Crear Tipo de Maquina

```
POST /api/tipos-maquina/
```

Crea un nuevo tipo de maquina.

**Body de la peticion:**
```json
{
    "nombre": "Prensa",
    "descripcion": "Prensas hidraulicas",
    "empresa": 1
}
```


### Actualizar Tipo de Maquina

```
PUT /api/tipos-maquina/{id}/
PATCH /api/tipos-maquina/{id}/
```

Actualiza un tipo de maquina existente.


### Eliminar Tipo de Maquina

```
DELETE /api/tipos-maquina/{id}/
```

Elimina un tipo de maquina. No se puede eliminar si hay maquinas asociadas.


## Maquinas

Las maquinas son los equipos de produccion donde trabajan los operarios.


### Listar Maquinas

```
GET /api/maquinas/
```

Retorna todas las maquinas de la empresa.

**Parametros de consulta opcionales:**
- `activa`: Filtrar por estado activo (true/false)
- `estado_actual`: Filtrar por estado (OPERANDO, PARADA, MANTENIMIENTO, INACTIVA)
- `tipo`: Filtrar por tipo de maquina (ID)
- `search`: Buscar por codigo o nombre

**Respuesta exitosa (200):**
```json
[
    {
        "id": 1,
        "codigo": "INY-001",
        "nombre": "Inyectora Principal",
        "tipo": 1,
        "tipo_nombre": "Inyectora",
        "empresa": 1,
        "ubicacion": "Nave A, Sector 1",
        "descripcion": "Inyectora de plastico 500 toneladas",
        "capacidad_produccion": 100,
        "estado_actual": "OPERANDO",
        "estado_display": "Operando",
        "activa": true,
        "created_at": "2026-01-20T14:00:00Z"
    }
]
```


### Obtener Detalle de Maquina

```
GET /api/maquinas/{id}/
```

Retorna el detalle completo de una maquina incluyendo historial de estados.

**Respuesta exitosa (200):**
```json
{
    "id": 1,
    "codigo": "INY-001",
    "nombre": "Inyectora Principal",
    "tipo": 1,
    "tipo_nombre": "Inyectora",
    "empresa": 1,
    "ubicacion": "Nave A, Sector 1",
    "descripcion": "Inyectora de plastico 500 toneladas",
    "capacidad_produccion": 100,
    "estado_actual": "OPERANDO",
    "estado_display": "Operando",
    "activa": true,
    "created_at": "2026-01-20T14:00:00Z",
    "updated_at": "2026-03-09T10:00:00Z"
}
```


### Crear Maquina

```
POST /api/maquinas/
```

Registra una nueva maquina en el sistema.

**Body de la peticion:**
```json
{
    "codigo": "INY-002",
    "nombre": "Inyectora Secundaria",
    "tipo": 1,
    "empresa": 1,
    "ubicacion": "Nave A, Sector 2",
    "descripcion": "Inyectora de plastico 300 toneladas",
    "capacidad_produccion": 80
}
```

**Validaciones:**
- El codigo debe ser unico dentro de la empresa
- La capacidad de produccion debe ser mayor a cero


### Actualizar Maquina

```
PUT /api/maquinas/{id}/
PATCH /api/maquinas/{id}/
```

Actualiza los datos de una maquina.


### Eliminar Maquina

```
DELETE /api/maquinas/{id}/
```

Elimina una maquina. Se recomienda desactivar en lugar de eliminar.


### Cambiar Estado de Maquina

```
POST /api/maquinas/{id}/cambiar_estado/
```

Cambia el estado operativo de una maquina.

**Body de la peticion:**
```json
{
    "estado": "MANTENIMIENTO",
    "motivo": "Mantenimiento preventivo programado"
}
```

**Estados validos:**
- OPERANDO: La maquina esta funcionando normalmente
- PARADA: La maquina esta detenida (sin motivo de mantenimiento)
- MANTENIMIENTO: La maquina esta en mantenimiento programado
- INACTIVA: La maquina esta fuera de servicio

**Respuesta exitosa (200):**
```json
{
    "mensaje": "Estado cambiado a MANTENIMIENTO",
    "maquina": {
        "id": 1,
        "codigo": "INY-001",
        "estado_actual": "MANTENIMIENTO"
    }
}
```


### Obtener Maquinas Disponibles

```
GET /api/maquinas/disponibles/
```

Retorna las maquinas que estan operando y disponibles para asignacion.

**Respuesta exitosa (200):**
```json
[
    {
        "id": 2,
        "codigo": "INY-002",
        "nombre": "Inyectora Secundaria",
        "estado_actual": "OPERANDO"
    }
]
```


### Obtener Maquinas en Mantenimiento

```
GET /api/maquinas/en_mantenimiento/
```

Retorna las maquinas que actualmente estan en mantenimiento.


## Productos

Los productos son los articulos que se fabrican en las maquinas.


### Listar Productos

```
GET /api/productos/
```

Retorna todos los productos de la empresa.

**Parametros de consulta opcionales:**
- `activo`: Filtrar por estado activo (true/false)
- `maquinas_compatibles`: Filtrar por maquina compatible (ID)
- `search`: Buscar por codigo o nombre

**Respuesta exitosa (200):**
```json
[
    {
        "id": 1,
        "codigo": "PROD-001",
        "nombre": "Botella PET 500ml",
        "descripcion": "Botella transparente de 500ml",
        "empresa": 1,
        "tiempo_ciclo": 15,
        "unidad_medida": "unidades",
        "maquinas_compatibles": [1, 2],
        "maquinas_nombres": ["Inyectora Principal", "Inyectora Secundaria"],
        "activo": true,
        "created_at": "2026-02-01T09:00:00Z"
    }
]
```


### Obtener Detalle de Producto

```
GET /api/productos/{id}/
```

Retorna el detalle completo de un producto.


### Crear Producto

```
POST /api/productos/
```

Crea un nuevo producto.

**Body de la peticion:**
```json
{
    "codigo": "PROD-002",
    "nombre": "Tapa Rosca 28mm",
    "descripcion": "Tapa de rosca para botella",
    "empresa": 1,
    "tiempo_ciclo": 8,
    "unidad_medida": "unidades",
    "maquinas_compatibles": [1]
}
```

**Validaciones:**
- El codigo debe ser unico dentro de la empresa
- El tiempo de ciclo debe ser mayor a cero
- Las maquinas compatibles deben pertenecer a la empresa


### Actualizar Producto

```
PUT /api/productos/{id}/
PATCH /api/productos/{id}/
```

Actualiza los datos de un producto.


### Eliminar Producto

```
DELETE /api/productos/{id}/
```

Elimina un producto. Se recomienda desactivar en lugar de eliminar.


### Obtener Productos por Maquina

```
GET /api/productos/por_maquina/?maquina={id}
```

Retorna los productos compatibles con una maquina especifica.

**Parametro requerido:**
- `maquina`: ID de la maquina

**Respuesta exitosa (200):**
```json
[
    {
        "id": 1,
        "codigo": "PROD-001",
        "nombre": "Botella PET 500ml",
        "tiempo_ciclo": 15
    }
]
```


## Estados de Maquina

El sistema maneja los siguientes estados para las maquinas:

| Estado | Color Semaforo | Descripcion |
|--------|---------------|-------------|
| OPERANDO | Verde | Funcionando normalmente |
| PARADA | Rojo | Detenida por algun motivo |
| MANTENIMIENTO | Amarillo | En mantenimiento programado |
| INACTIVA | Gris | Fuera de servicio |


## Codigos de Error Comunes

| Codigo | Descripcion |
|--------|-------------|
| 400 | Datos invalidos (codigo duplicado, etc.) |
| 401 | No autenticado |
| 403 | Sin permisos para esta accion |
| 404 | Maquina o producto no encontrado |
| 409 | Conflicto (no se puede eliminar por dependencias) |


## Notas de Implementacion

1. Las maquinas y productos se filtran automaticamente por empresa del usuario
2. Los codigos de maquina y producto deben ser unicos dentro de cada empresa
3. El cambio de estado de maquina genera eventos automaticos para reportes
4. La capacidad de produccion se usa para calcular eficiencia esperada
5. El tiempo de ciclo del producto se usa para calcular metricas de produccion
